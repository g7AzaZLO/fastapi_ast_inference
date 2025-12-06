import ast
import inspect
import logging
import textwrap
from typing import Any, Dict, List, Optional, Type, Union

from pydantic import BaseModel

try:
    from pydantic import __version__ as pydantic_version

    PYDANTIC_V2 = pydantic_version.startswith("2.")
except ImportError:
    PYDANTIC_V2 = False

logger = logging.getLogger("fastapi_ast_inference")


def _infer_type_from_ast(
    node: ast.AST,
    func_def: Union[ast.FunctionDef, ast.AsyncFunctionDef],
    context_name: str,
) -> Any:
    """
    Infer Python type from an AST node.

    Analyzes AST nodes recursively to determine the Python type of values,
    supporting constants, lists, dicts, binary operations, comparisons,
    and function arguments.

    Args:
        node: The AST node to analyze.
        func_def: The function definition containing this node.
        context_name: A name prefix for nested model generation.

    Returns:
        The inferred Python type (e.g., str, int, List[int], or a Pydantic model).
        Returns Any if type cannot be determined.
    """
    if isinstance(node, ast.Constant):
        return type(node.value)

    if isinstance(node, ast.List):
        if not node.elts:
            return List[Any]

        first_type = _infer_type_from_ast(node.elts[0], func_def, context_name + "Item")

        for elt in node.elts[1:]:
            current_type = _infer_type_from_ast(elt, func_def, context_name + "Item")
            if current_type != first_type:
                return List[Any]

        if first_type is not Any:
            return List[first_type]  # type: ignore
        return List[Any]

    if isinstance(node, ast.BinOp):
        left_type = _infer_type_from_ast(node.left, func_def, context_name)
        right_type = _infer_type_from_ast(node.right, func_def, context_name)
        if left_type == right_type and left_type in (int, float, str):
            return left_type
        if {left_type, right_type} == {int, float}:
            return float

    if isinstance(node, ast.Compare):
        return bool

    if isinstance(node, ast.Dict):
        fields = {}
        for key, value in zip(node.keys, node.values):
            if not isinstance(key, ast.Constant):
                continue
            field_name = key.value
            field_type = _infer_type_from_ast(
                value, func_def, context_name + "_" + str(field_name)
            )
            fields[field_name] = (field_type, ...)

        if not fields:
            return Dict[str, Any]

        if PYDANTIC_V2:
            from pydantic import create_model
        else:
            from pydantic import create_model

        return create_model(f"Model_{context_name}", **fields)  # type: ignore[call-overload]

    if isinstance(node, ast.Name):
        arg_name = node.id
        for arg in func_def.args.args:
            if arg.arg != arg_name:
                continue

            if not arg.annotation:
                continue

            if not isinstance(arg.annotation, ast.Name):
                continue

            annotation_id = arg.annotation.id
            if annotation_id == "int":
                return int
            if annotation_id == "str":
                return str
            if annotation_id == "bool":
                return bool
            if annotation_id == "float":
                return float
            if annotation_id == "list":
                return List[Any]
            if annotation_id == "dict":
                return Dict[str, Any]

    return Any


def infer_response_model_from_ast(
    endpoint_function: Any,
) -> Optional[Type[BaseModel]]:
    """
    Analyze the endpoint function's source code to infer a Pydantic model
    from a returned dictionary literal or variable assignment.

    This function uses Python's AST module to parse the function's source code
    and extract type information from return statements. It supports:

    - Direct dictionary literal returns: `return {"key": "value"}`
    - Variable returns: `data = {"key": "value"}; return data`
    - Annotated variable returns: `data: Dict[str, Any] = {"key": "value"}; return data`
    - Nested dictionaries and lists
    - Type inference from function arguments

    Args:
        endpoint_function: The FastAPI endpoint function to analyze.

    Returns:
        A dynamically created Pydantic model representing the response structure,
        or None if inference is not possible (e.g., multiple return statements,
        non-dict returns, syntax errors, etc.).

    Note:
        - Functions with multiple return statements return None to avoid
          misleading OpenAPI documentation.
        - Functions where all fields resolve to Any type return None.
        - This analysis happens at startup time, not per-request.
    """
    func_name = getattr(endpoint_function, "__name__", "<unknown>")

    try:
        source = inspect.getsource(endpoint_function)
    except (OSError, TypeError):
        logger.debug(
            f"AST inference skipped for '{func_name}': could not retrieve source code"
        )
        return None

    source = textwrap.dedent(source)
    try:
        tree = ast.parse(source)
    except SyntaxError:
        logger.debug(
            f"AST inference skipped for '{func_name}': syntax error in source code"
        )
        return None

    if not tree.body:
        logger.debug(f"AST inference skipped for '{func_name}': empty AST body")
        return None

    func_def = tree.body[0]
    if not isinstance(func_def, (ast.FunctionDef, ast.AsyncFunctionDef)):
        logger.debug(
            f"AST inference skipped for '{func_name}': not a function definition"
        )
        return None

    # Collect ALL return statements (not just the first one)
    return_statements: List[ast.Return] = []

    nodes_to_visit: List[ast.AST] = list(func_def.body)
    while nodes_to_visit:
        node = nodes_to_visit.pop(0)

        if isinstance(node, ast.Return):
            return_statements.append(node)
            # Don't break - continue to find all returns

        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue

        for child in ast.iter_child_nodes(node):
            nodes_to_visit.append(child)

    if not return_statements:
        logger.debug(
            f"AST inference skipped for '{func_name}': no return statement found"
        )
        return None

    # If there are multiple return statements, skip inference to avoid
    # misleading documentation (we can't reliably determine the structure)
    if len(return_statements) > 1:
        logger.debug(
            f"AST inference skipped for '{func_name}': "
            f"multiple return statements detected ({len(return_statements)})"
        )
        return None

    return_stmt = return_statements[0]
    returned_value = return_stmt.value
    dict_node = None

    if isinstance(returned_value, ast.Dict):
        dict_node = returned_value
    elif isinstance(returned_value, ast.Name):
        variable_name = returned_value.id
        # Find assignment
        for node in func_def.body:
            if (
                isinstance(node, ast.AnnAssign)
                and isinstance(node.target, ast.Name)
                and node.target.id == variable_name
            ):
                if isinstance(node.value, ast.Dict):
                    dict_node = node.value
                    break
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == variable_name:
                        if isinstance(node.value, ast.Dict):
                            dict_node = node.value
                            break

    if not dict_node:
        logger.debug(
            f"AST inference skipped for '{func_name}': "
            "return value is not a dict literal or assigned variable"
        )
        return None

    fields = {}
    for key, value in zip(dict_node.keys, dict_node.values):
        if not isinstance(key, ast.Constant):
            continue

        if not isinstance(key.value, str):
            logger.debug(
                f"AST inference skipped for '{func_name}': non-string key found in dict"
            )
            return None

        field_name = key.value

        field_type = _infer_type_from_ast(value, func_def, f"{func_name}_{field_name}")

        fields[field_name] = (field_type, ...)

    if not fields:
        logger.debug(
            f"AST inference skipped for '{func_name}': no fields could be inferred"
        )
        return None

    # Don't create a model if all fields are Any - this provides no additional
    # type information compared to Dict[str, Any] and would override explicit
    # type annotations unnecessarily
    if all(field_type is Any for field_type, _ in fields.values()):
        logger.debug(
            f"AST inference skipped for '{func_name}': all fields resolved to Any type"
        )
        return None

    if PYDANTIC_V2:
        from pydantic import create_model
    else:
        from pydantic import create_model

    model_name = f"ResponseModel_{func_name}"
    try:
        return create_model(model_name, **fields)  # type: ignore[call-overload,no-any-return]
    except Exception as e:
        logger.debug(
            f"AST inference skipped for '{func_name}': failed to create model: {e}"
        )
        return None

