"""Tests for core AST inference functionality."""

from typing import Any, Dict, List
from unittest.mock import patch

import pytest

from fastapi_ast_inference import infer_response_model_from_ast


# Test functions defined at module level for inspect.getsource compatibility
def _returns_dict_literal() -> Dict[str, Any]:
    """Return a simple dictionary literal."""
    return {"name": "test", "value": 123, "active": True}


def _returns_variable() -> Dict[str, Any]:
    """Return via variable assignment."""
    data = {"status": "ok", "count": 42}
    return data


def _returns_annotated_variable() -> Dict[str, Any]:
    """Return via annotated variable."""
    result: Dict[str, Any] = {"message": "hello", "items": [1, 2, 3]}
    return result


def _returns_nested_dict() -> Dict[str, Any]:
    """Return nested dictionary structure."""
    return {
        "user": {"name": "John", "age": 30},
        "settings": {"theme": "dark"},
    }


def _returns_list_of_dicts() -> Dict[str, Any]:
    """Return with list of dicts."""
    return {
        "items": [
            {"id": 1, "name": "Item 1"},
            {"id": 2, "name": "Item 2"},
        ]
    }


def _uses_arg_types(user_id: int, name: str, active: bool, score: float) -> Dict[str, Any]:
    """Return dict with typed arguments."""
    return {"id": user_id, "name": name, "active": active, "score": score}


def _no_return_statement() -> Dict[str, Any]:
    """Function without return statement."""
    x = {"a": 1}  # noqa: F841


def _returns_empty_dict() -> Dict[str, Any]:
    """Return empty dictionary."""
    return {}


def _returns_function_call() -> Dict[str, Any]:
    """Return result of function call."""
    return {}.copy()


def _multiple_returns(flag: bool) -> Dict[str, Any]:
    """Function with multiple return statements."""
    if flag:
        return {"spam": "spam"}
    else:
        return {"eggs": "eggs"}


def _all_any_fields() -> Dict[str, Any]:
    """All fields resolve to Any type."""
    some_var = "value"
    return {"field1": some_var, "field2": some_var}


def _non_string_key() -> Dict[Any, Any]:
    """Dictionary with non-string key."""
    return {1: "value", "valid": "key"}


def _mixed_types_list() -> Dict[str, Any]:
    """List with mixed types."""
    return {"items": [1, "two", 3.0]}


def _homogeneous_list() -> Dict[str, Any]:
    """List with homogeneous types."""
    return {"numbers": [1, 2, 3], "names": ["a", "b", "c"]}


def _binary_operations() -> Dict[str, Any]:
    """Dictionary with binary operations."""
    return {"sum": 10 + 5, "concat": "foo" + "bar", "comparison": 5 > 3}


def _int_float_binop() -> Dict[str, Any]:
    """Binary operation with int and float."""
    return {"result": 10 + 5.5, "int_only": 10 + 5}


def _arg_no_annotation(a) -> Dict[str, Any]:
    """Argument without annotation."""
    return {"value": a}


def _arg_complex_annotation(items: List[int]) -> Dict[str, Any]:
    """Argument with complex annotation."""
    return {"items": items}


def _arg_list_type(items: list) -> Dict[str, Any]:
    """Argument with bare list type."""
    return {"items": items}


def _arg_dict_type(data: dict) -> Dict[str, Any]:
    """Argument with bare dict type."""
    return {"data": data}


class TestInferResponseModelSuccess:
    """Tests for successful inference cases."""

    def test_dict_literal(self):
        """Test inference from direct dict literal."""
        print("\n✓ Тест: test_dict_literal")
        _returns_dict_literal()  # Execute for coverage
        model = infer_response_model_from_ast(_returns_dict_literal)
        assert model is not None
        assert "name" in model.__annotations__
        assert "value" in model.__annotations__
        assert "active" in model.__annotations__
        print("  ✓ Успешно: модель выведена из словаря-литерала")

    def test_variable_return(self):
        """Test inference from variable return."""
        print("\n✓ Тест: test_variable_return")
        _returns_variable()
        model = infer_response_model_from_ast(_returns_variable)
        assert model is not None
        assert "status" in model.__annotations__
        assert "count" in model.__annotations__
        print("  ✓ Успешно: модель выведена из переменной")

    def test_annotated_variable(self):
        """Test inference from annotated variable."""
        print("\n✓ Тест: test_annotated_variable")
        _returns_annotated_variable()
        model = infer_response_model_from_ast(_returns_annotated_variable)
        assert model is not None
        assert "message" in model.__annotations__
        assert "items" in model.__annotations__
        print("  ✓ Успешно: модель выведена из аннотированной переменной")

    def test_nested_dict(self):
        """Test inference with nested dictionaries."""
        print("\n✓ Тест: test_nested_dict")
        _returns_nested_dict()
        model = infer_response_model_from_ast(_returns_nested_dict)
        assert model is not None
        assert "user" in model.__annotations__
        assert "settings" in model.__annotations__
        print("  ✓ Успешно: модель выведена из вложенного словаря")

    def test_list_of_dicts(self):
        """Test inference with list of dicts."""
        print("\n✓ Тест: test_list_of_dicts")
        _returns_list_of_dicts()
        model = infer_response_model_from_ast(_returns_list_of_dicts)
        assert model is not None
        assert "items" in model.__annotations__
        print("  ✓ Успешно: модель выведена из списка словарей")

    def test_arg_types(self):
        """Test type inference from function arguments."""
        print("\n✓ Тест: test_arg_types")
        _uses_arg_types(1, "test", True, 1.5)
        model = infer_response_model_from_ast(_uses_arg_types)
        assert model is not None
        assert "id" in model.__annotations__
        assert "name" in model.__annotations__
        print("  ✓ Успешно: модель выведена из типов аргументов")

    def test_homogeneous_list(self):
        """Test inference with homogeneous lists."""
        print("\n✓ Тест: test_homogeneous_list")
        _homogeneous_list()
        model = infer_response_model_from_ast(_homogeneous_list)
        assert model is not None
        assert "numbers" in model.__annotations__
        assert "names" in model.__annotations__
        print("  ✓ Успешно: модель выведена из однородных списков")

    def test_binary_operations(self):
        """Test inference with binary operations."""
        print("\n✓ Тест: test_binary_operations")
        _binary_operations()
        model = infer_response_model_from_ast(_binary_operations)
        assert model is not None
        assert "sum" in model.__annotations__
        assert "concat" in model.__annotations__
        assert "comparison" in model.__annotations__
        print("  ✓ Успешно: модель выведена из бинарных операций")

    def test_int_float_binop(self):
        """Test int+float binary operation."""
        print("\n✓ Тест: test_int_float_binop")
        _int_float_binop()
        model = infer_response_model_from_ast(_int_float_binop)
        assert model is not None
        assert "result" in model.__annotations__
        assert "int_only" in model.__annotations__
        print("  ✓ Успешно: модель выведена из int+float операции")

    def test_list_arg_type(self):
        """Test bare list type annotation."""
        print("\n✓ Тест: test_list_arg_type")
        _arg_list_type([])
        model = infer_response_model_from_ast(_arg_list_type)
        assert model is not None
        assert "items" in model.__annotations__
        print("  ✓ Успешно: модель выведена из bare list типа")

    def test_dict_arg_type(self):
        """Test bare dict type annotation."""
        print("\n✓ Тест: test_dict_arg_type")
        _arg_dict_type({})
        model = infer_response_model_from_ast(_arg_dict_type)
        assert model is not None
        assert "data" in model.__annotations__
        print("  ✓ Успешно: модель выведена из bare dict типа")


class TestInferResponseModelReturnsNone:
    """Tests for cases where inference should return None."""

    def test_no_return_statement(self):
        """Test function without return."""
        print("\n✓ Тест: test_no_return_statement")
        _no_return_statement()
        assert infer_response_model_from_ast(_no_return_statement) is None
        print("  ✓ Успешно: функция без return корректно обработана")

    def test_empty_dict(self):
        """Test empty dict return."""
        print("\n✓ Тест: test_empty_dict")
        _returns_empty_dict()
        assert infer_response_model_from_ast(_returns_empty_dict) is None
        print("  ✓ Успешно: пустой словарь корректно обработан")

    def test_function_call_return(self):
        """Test function call return."""
        print("\n✓ Тест: test_function_call_return")
        _returns_function_call()
        assert infer_response_model_from_ast(_returns_function_call) is None
        print("  ✓ Успешно: возврат вызова функции корректно обработан")

    def test_multiple_returns(self):
        """Test multiple return statements."""
        print("\n✓ Тест: test_multiple_returns")
        _multiple_returns(True)
        _multiple_returns(False)
        assert infer_response_model_from_ast(_multiple_returns) is None
        print("  ✓ Успешно: множественные return корректно обработаны")

    def test_all_any_fields(self):
        """Test all fields resolving to Any."""
        print("\n✓ Тест: test_all_any_fields")
        _all_any_fields()
        assert infer_response_model_from_ast(_all_any_fields) is None
        print("  ✓ Успешно: поля типа Any корректно обработаны")

    def test_non_string_key(self):
        """Test dict with non-string key."""
        print("\n✓ Тест: test_non_string_key")
        _non_string_key()
        assert infer_response_model_from_ast(_non_string_key) is None
        print("  ✓ Успешно: не-строковый ключ корректно обработан")

    def test_lambda(self):
        """Test lambda function (no source available)."""
        print("\n✓ Тест: test_lambda")
        assert infer_response_model_from_ast(lambda: {"a": 1}) is None
        print("  ✓ Успешно: lambda функция корректно обработана")

    def test_builtin(self):
        """Test builtin function."""
        print("\n✓ Тест: test_builtin")
        assert infer_response_model_from_ast(len) is None
        print("  ✓ Успешно: встроенная функция корректно обработана")

    def test_arg_no_annotation(self):
        """Test argument without annotation."""
        print("\n✓ Тест: test_arg_no_annotation")
        _arg_no_annotation(1)
        assert infer_response_model_from_ast(_arg_no_annotation) is None
        print("  ✓ Успешно: аргумент без аннотации корректно обработан")

    def test_arg_complex_annotation(self):
        """Test argument with complex annotation."""
        print("\n✓ Тест: test_arg_complex_annotation")
        _arg_complex_annotation([1, 2, 3])
        assert infer_response_model_from_ast(_arg_complex_annotation) is None
        print("  ✓ Успешно: сложная аннотация корректно обработана")


class TestInferResponseModelErrorHandling:
    """Tests for error handling in inference."""

    def test_getsource_error(self):
        """Test OSError from getsource."""
        print("\n✓ Тест: test_getsource_error")
        def func():
            pass
        func()
        with patch("inspect.getsource", side_effect=OSError):
            assert infer_response_model_from_ast(func) is None
        print("  ✓ Успешно: ошибка getsource корректно обработана")

    def test_syntax_error(self):
        """Test SyntaxError during parsing."""
        print("\n✓ Тест: test_syntax_error")
        def func():
            pass
        func()
        with patch("inspect.getsource", return_value="def func( invalid"):
            assert infer_response_model_from_ast(func) is None
        print("  ✓ Успешно: синтаксическая ошибка корректно обработана")

    def test_empty_body(self):
        """Test empty AST body."""
        print("\n✓ Тест: test_empty_body")
        def func():
            pass
        func()
        with patch("inspect.getsource", return_value="# just comments"):
            assert infer_response_model_from_ast(func) is None
        print("  ✓ Успешно: пустое тело AST корректно обработано")

    def test_not_function_def(self):
        """Test when parsed code is not a function."""
        print("\n✓ Тест: test_not_function_def")
        def func():
            pass
        func()
        with patch("inspect.getsource", return_value="class A: pass"):
            assert infer_response_model_from_ast(func) is None
        print("  ✓ Успешно: не-функция корректно обработана")

    def test_create_model_error(self):
        """Test create_model failure."""
        print("\n✓ Тест: test_create_model_error")
        def func():
            return {"a": 1}
        func()
        
        from fastapi_ast_inference.core import PYDANTIC_V2
        target = "pydantic.create_model" if PYDANTIC_V2 else "pydantic.create_model"
        
        with patch(target, side_effect=Exception("Model creation failed")):
            assert infer_response_model_from_ast(func) is None
        print("  ✓ Успешно: ошибка создания модели корректно обработана")


class TestMixedTypeLists:
    """Tests for list type inference."""

    def test_mixed_types(self):
        """Test list with mixed types results in List[Any]."""
        print("\n✓ Тест: test_mixed_types")
        _mixed_types_list()
        model = infer_response_model_from_ast(_mixed_types_list)
        assert model is not None
        assert "items" in model.__annotations__
        print("  ✓ Успешно: смешанные типы в списке корректно обработаны")

if __name__ == "__main__":
    pytest.main()