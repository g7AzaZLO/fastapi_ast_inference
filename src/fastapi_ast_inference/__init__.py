"""
FastAPI AST Inference - Automatic response model inference from return statements.

This library provides tools to automatically infer Pydantic response models
from FastAPI endpoint functions by analyzing their AST (Abstract Syntax Tree).

Features:
- Automatic type inference from dict literals
- Support for nested structures and lists
- Type inference from function arguments
- Multiple usage patterns: decorator, custom route class, or programmatic API

Quick Start:
    ```python
    from fastapi import FastAPI
    from fastapi_ast_inference import InferredAPIRoute

    app = FastAPI()
    app.router.route_class = InferredAPIRoute

    @app.get("/")
    async def endpoint():
        return {"status": "ok", "count": 42}
        # Automatically generates OpenAPI schema with typed fields!
    ```

Alternative usage with decorator:
    ```python
    from fastapi import FastAPI
    from fastapi_ast_inference import infer_response, InferredAPIRoute

    app = FastAPI()
    app.router.route_class = InferredAPIRoute

    @app.get("/")
    @infer_response  # Explicit marking for inference
    async def endpoint():
        return {"message": "Hello, World!"}
    ```
"""

__version__ = "0.1.0"

from .core import (
    PYDANTIC_V2,
    infer_response_model_from_ast,
)
from .decorator import (
    INFERRED_MODEL_ATTR,
    InferResponseFactory,
    get_inferred_model,
    infer_response,
)
from .route import (
    InferredAPIRoute,
    create_inferred_router,
)

__all__ = [
    # Version
    "__version__",
    # Core functions
    "infer_response_model_from_ast",
    "PYDANTIC_V2",
    # Decorator
    "infer_response",
    "get_inferred_model",
    "InferResponseFactory",
    "INFERRED_MODEL_ATTR",
    # Route class
    "InferredAPIRoute",
    "create_inferred_router",
]

