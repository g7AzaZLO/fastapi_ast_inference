from typing import Any, Callable, Optional, Type, TypeVar

from pydantic import BaseModel

from .core import infer_response_model_from_ast

F = TypeVar("F", bound=Callable[..., Any])


# Attribute name used to store the inferred model on decorated functions
INFERRED_MODEL_ATTR = "__ast_inferred_response_model__"


def infer_response(func: F) -> F:
    """
    Decorator that infers and sets response model from AST analysis.

    This decorator analyzes the function's source code at decoration time
    and infers a Pydantic model from the return statement. The inferred model
    is automatically set as the function's return annotation, so FastAPI
    uses it as `response_model` without additional configuration.

    Usage:
        ```python
        from fastapi import FastAPI
        from fastapi_ast_inference import infer_response

        app = FastAPI()

        @app.get("/")
        @infer_response
        async def endpoint():
            return {"status": "ok", "count": 42}
        ```

    The decorator should be placed AFTER the route decorator (closer to the function).

    Args:
        func: The endpoint function to analyze.

    Returns:
        The same function with inferred response model set as return annotation.

    Note:
        - Inference happens at decoration time (application startup), not per request.
        - If inference fails, the original function is returned unchanged.
        - Works independently without `InferredAPIRoute`.
    """
    inferred_model = infer_response_model_from_ast(func)
    setattr(func, INFERRED_MODEL_ATTR, inferred_model)

    # Set return annotation so FastAPI automatically uses it as response_model
    if inferred_model is not None:
        if not hasattr(func, "__annotations__"):
            func.__annotations__ = {}
        func.__annotations__["return"] = inferred_model

    return func


def get_inferred_model(func: Callable[..., Any]) -> Optional[Type[BaseModel]]:
    """
    Get the inferred response model from a decorated function.

    Args:
        func: A function potentially decorated with `@infer_response`.

    Returns:
        The inferred Pydantic model, or None if the function was not decorated
        or inference failed.
    """
    return getattr(func, INFERRED_MODEL_ATTR, None)


class InferResponseFactory:
    """
    Factory class for creating configured inference decorators.

    This allows for more advanced configuration options in the future,
    such as custom model naming, field validation rules, etc.

    Usage:
        ```python
        from fastapi_ast_inference import InferResponseFactory

        infer = InferResponseFactory(model_prefix="API")

        @app.get("/")
        @infer()
        async def endpoint():
            return {"status": "ok"}
        ```
    """

    def __init__(
        self,
        model_prefix: str = "ResponseModel",
        strict: bool = False,
    ) -> None:
        """
        Initialize the factory with configuration options.

        Args:
            model_prefix: Prefix for generated model names.
            strict: If True, raise an error when inference fails instead of
                   silently returning None.
        """
        self.model_prefix = model_prefix
        self.strict = strict

    def __call__(self, func: F) -> F:
        """
        Apply inference to the given function.

        Args:
            func: The endpoint function to analyze.

        Returns:
            The decorated function with inferred model as return annotation.

        Raises:
            ValueError: If strict mode is enabled and inference fails.
        """
        inferred_model = infer_response_model_from_ast(func)

        if self.strict and inferred_model is None:
            raise ValueError(
                f"Failed to infer response model for function '{func.__name__}'. "
                "Ensure the function returns a dictionary literal with string keys."
            )

        setattr(func, INFERRED_MODEL_ATTR, inferred_model)

        # Set return annotation so FastAPI automatically uses it as response_model
        if inferred_model is not None:
            if not hasattr(func, "__annotations__"):
                func.__annotations__ = {}
            func.__annotations__["return"] = inferred_model

        return func

