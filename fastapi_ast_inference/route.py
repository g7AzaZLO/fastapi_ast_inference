import dataclasses
from typing import Any, Callable, Dict, List, Optional, Sequence, Set, Type, Union

from fastapi import params
from fastapi.datastructures import Default, DefaultPlaceholder
from fastapi.routing import APIRoute, generate_unique_id
from pydantic import BaseModel
from starlette.responses import JSONResponse, Response
from starlette.routing import BaseRoute

from .core import infer_response_model_from_ast
from .decorator import get_inferred_model


def _contains_response(annotation: Any) -> bool:
    """
    Check if an annotation contains a Response type.

    Args:
        annotation: The type annotation to check.

    Returns:
        True if the annotation is or contains a Response type.
    """
    from typing import get_args

    from fastapi._compat import lenient_issubclass

    if lenient_issubclass(annotation, Response):
        return True

    args = get_args(annotation)
    for arg in args:
        if _contains_response(arg):
            return True

    return False


class InferredAPIRoute(APIRoute):
    """
    Custom APIRoute class that automatically infers response models from AST.

    This route class extends FastAPI's APIRoute to automatically analyze
    endpoint functions and infer Pydantic models for response documentation.

    Usage with FastAPI app:
        ```python
        from fastapi import FastAPI
        from fastapi_ast_inference import InferredAPIRoute

        app = FastAPI()
        app.router.route_class = InferredAPIRoute

        @app.get("/")
        async def endpoint():
            return {"status": "ok", "count": 42}
        ```

    Usage with APIRouter:
        ```python
        from fastapi import APIRouter
        from fastapi_ast_inference import InferredAPIRoute

        router = APIRouter(route_class=InferredAPIRoute)

        @router.get("/")
        async def endpoint():
            return {"status": "ok"}
        ```

    The route class will:
    1. First check if the endpoint was decorated with `@infer_response`
    2. If not, automatically run AST inference on the endpoint
    3. Use the inferred model as `response_model` if no explicit model is set
    """

    def __init__(
        self,
        path: str,
        endpoint: Callable[..., Any],
        *,
        response_model: Any = Default(None),
        status_code: Optional[int] = None,
        tags: Optional[List[Union[str, Any]]] = None,
        dependencies: Optional[Sequence[params.Depends]] = None,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        response_description: str = "Successful Response",
        responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
        deprecated: Optional[bool] = None,
        name: Optional[str] = None,
        methods: Optional[Union[Set[str], List[str]]] = None,
        operation_id: Optional[str] = None,
        response_model_include: Optional[Any] = None,
        response_model_exclude: Optional[Any] = None,
        response_model_by_alias: bool = True,
        response_model_exclude_unset: bool = False,
        response_model_exclude_defaults: bool = False,
        response_model_exclude_none: bool = False,
        include_in_schema: bool = True,
        response_class: Union[Type[Response], DefaultPlaceholder] = Default(
            JSONResponse
        ),
        dependency_overrides_provider: Optional[Any] = None,
        callbacks: Optional[List[BaseRoute]] = None,
        openapi_extra: Optional[Dict[str, Any]] = None,
        generate_unique_id_function: Union[
            Callable[["APIRoute"], str], DefaultPlaceholder
        ] = Default(generate_unique_id),
    ) -> None:
        """
        Initialize the route with AST inference support.

        All parameters are the same as FastAPI's APIRoute, with the addition
        of automatic response model inference when `response_model` is not
        explicitly provided.
        """
        # Handle response model inference
        if isinstance(response_model, DefaultPlaceholder):
            from fastapi._compat import lenient_issubclass
            from fastapi.dependencies.utils import get_typed_return_annotation

            return_annotation = get_typed_return_annotation(endpoint)

            if lenient_issubclass(return_annotation, Response):
                response_model = None
            else:
                response_model = return_annotation

                if response_model is None or (
                    not lenient_issubclass(response_model, BaseModel)
                    and not dataclasses.is_dataclass(response_model)
                ):
                    if return_annotation is None or not _contains_response(
                        return_annotation
                    ):
                        # First check for decorator-provided model
                        inferred = get_inferred_model(endpoint)

                        # If no decorator model, run AST inference
                        if inferred is None:
                            inferred = infer_response_model_from_ast(endpoint)

                        if inferred:
                            response_model = inferred

        # Call parent __init__ with the resolved response_model
        super().__init__(
            path=path,
            endpoint=endpoint,
            response_model=response_model,
            status_code=status_code,
            tags=tags,
            dependencies=dependencies,
            summary=summary,
            description=description,
            response_description=response_description,
            responses=responses,
            deprecated=deprecated,
            name=name,
            methods=methods,
            operation_id=operation_id,
            response_model_include=response_model_include,
            response_model_exclude=response_model_exclude,
            response_model_by_alias=response_model_by_alias,
            response_model_exclude_unset=response_model_exclude_unset,
            response_model_exclude_defaults=response_model_exclude_defaults,
            response_model_exclude_none=response_model_exclude_none,
            include_in_schema=include_in_schema,
            response_class=response_class,
            dependency_overrides_provider=dependency_overrides_provider,
            callbacks=callbacks,
            openapi_extra=openapi_extra,
            generate_unique_id_function=generate_unique_id_function,
        )


def create_inferred_router(**kwargs: Any) -> "Any":
    """
    Create an APIRouter with InferredAPIRoute as the default route class.

    This is a convenience function to create a router that automatically
    uses AST inference for all routes.

    Usage:
        ```python
        from fastapi_ast_inference import create_inferred_router

        router = create_inferred_router(prefix="/api/v1", tags=["api"])

        @router.get("/items")
        async def get_items():
            return {"items": ["a", "b", "c"]}
        ```

    Args:
        **kwargs: Arguments to pass to APIRouter constructor.

    Returns:
        An APIRouter instance with InferredAPIRoute as the route class.
    """
    from fastapi import APIRouter

    kwargs.setdefault("route_class", InferredAPIRoute)
    return APIRouter(**kwargs)

