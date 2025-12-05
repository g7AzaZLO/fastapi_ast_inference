"""
FastAPI AST Inference Demo - Swagger UI visualization.

Run:
    python examples/demo_swagger.py

Then open in browser:
    http://127.0.0.1:8000/docs
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import uvicorn
from fastapi import FastAPI

from fastapi_ast_inference import InferredAPIRoute, infer_response


app = FastAPI(
    title="FastAPI AST Inference Demo",
    description="Automatic response model inference from AST analysis",
    version="0.1.0",
)
app.router.route_class = InferredAPIRoute


# =============================================================================
# Auto-inference examples
# =============================================================================


@app.get("/simple", tags=["Auto-inference"])
async def simple_endpoint():
    """Simple endpoint with basic types."""
    return {
        "message": "Hello, World!",
        "count": 42,
        "active": True,
        "score": 3.14,
    }


@app.get("/nested", tags=["Auto-inference"])
async def nested_endpoint():
    """Endpoint with nested structures."""
    return {
        "user": {
            "name": "John Doe",
            "age": 30,
            "email": "john@example.com",
        },
        "settings": {
            "theme": "dark",
            "notifications": True,
        },
    }


@app.get("/with-lists", tags=["Auto-inference"])
async def lists_endpoint():
    """Endpoint with lists."""
    return {
        "numbers": [1, 2, 3, 4, 5],
        "names": ["Alice", "Bob", "Charlie"],
        "items": [
            {"id": 1, "name": "Item 1"},
            {"id": 2, "name": "Item 2"},
        ],
    }


@app.get("/users/{user_id}", tags=["Auto-inference"])
async def get_user(user_id: int, include_details: bool = False):
    """Endpoint with path and query parameters."""
    return {
        "id": user_id,
        "username": "testuser",
        "email": "test@example.com",
        "is_active": True,
    }


@app.get("/from-args/{item_id}", tags=["Auto-inference"])
async def from_args_endpoint(item_id: int, name: str, price: float):
    """Types inferred from argument annotations."""
    return {
        "id": item_id,
        "name": name,
        "price": price,
    }


@app.get("/variable-return", tags=["Auto-inference"])
async def variable_return_endpoint():
    """Return via variable assignment."""
    data = {
        "status": "success",
        "code": 200,
        "timestamp": "2024-01-01T00:00:00Z",
    }
    return data


# =============================================================================
# @infer_response decorator examples
# =============================================================================


@app.get("/decorated", tags=["Decorator"])
@infer_response
async def decorated_endpoint():
    """Endpoint with @infer_response decorator. Works even without InferredAPIRoute."""
    return {
        "decorated": True,
        "value": 100,
        "description": "Model inferred by decorator",
    }


# =============================================================================
# No inference cases (fallback to standard behavior)
# =============================================================================


@app.get("/multiple-returns", tags=["No inference"])
async def multiple_returns_endpoint(flag: bool = True):
    """Multiple return statements - inference not possible."""
    if flag:
        return {"type": "a", "value": 1}
    return {"type": "b", "value": 2}


@app.get("/function-call", tags=["No inference"])
async def function_call_endpoint():
    """Function call return - inference not possible."""
    return dict(status="ok")


@app.get("/empty", tags=["No inference"])
async def empty_endpoint():
    """Empty dictionary - inference not possible."""
    return {}


# =============================================================================
# POST/PUT/DELETE examples
# =============================================================================


@app.post("/users", tags=["CRUD"])
async def create_user():
    """Create user."""
    return {
        "id": 1,
        "created": True,
        "message": "User created successfully",
    }


@app.put("/users/{user_id}", tags=["CRUD"])
async def update_user(user_id: int):
    """Update user."""
    return {
        "id": user_id,
        "updated": True,
        "message": "User updated successfully",
    }


@app.delete("/users/{user_id}", tags=["CRUD"])
async def delete_user(user_id: int):
    """Delete user."""
    return {
        "id": user_id,
        "deleted": True,
        "message": "User deleted successfully",
    }


# =============================================================================
# Complex examples
# =============================================================================


@app.get("/orders/{order_id}", tags=["Complex"])
async def get_order(order_id: str):
    """Order with nested structure."""
    return {
        "order_id": order_id,
        "status": "processing",
        "total": 99.99,
        "items": [
            {"name": "Item 1", "price": 49.99, "quantity": 1},
            {"name": "Item 2", "price": 50.00, "quantity": 2},
        ],
        "shipping": {
            "address": "123 Main St",
            "city": "New York",
            "country": "USA",
        },
    }


@app.get("/analytics", tags=["Complex"])
async def get_analytics():
    """Analytics data."""
    return {
        "total_users": 1000,
        "active_users": 750,
        "revenue": 50000.00,
        "growth_rate": 15.5,
        "top_products": ["Product A", "Product B", "Product C"],
        "metrics": {
            "page_views": 100000,
            "conversions": 5000,
            "bounce_rate": 35.2,
        },
    }


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🚀 FastAPI AST Inference Demo")
    print("=" * 60)
    print("\n📖 Open Swagger UI: http://127.0.0.1:8000/docs")
    print("📖 Or ReDoc: http://127.0.0.1:8000/redoc")
    print("\n" + "=" * 60 + "\n")

    uvicorn.run(app, host="127.0.0.1", port=8000)
