# FastAPI AST Inference

[![PyPI version](https://badge.fury.io/py/fastapi-ast-inference.svg)](https://badge.fury.io/py/fastapi-ast-inference)
[![Python Versions](https://img.shields.io/pypi/pyversions/fastapi-ast-inference.svg)](https://pypi.org/project/fastapi-ast-inference/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Automatic response model inference for FastAPI using AST analysis.**

> 🇷🇺 [Русская версия](README_ru.md)

This library analyzes your FastAPI endpoint functions at startup time and automatically generates Pydantic models for OpenAPI documentation based on the dictionary structures you return.

## Why?

### Before (Standard Pydantic Approach)

```python
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

# You must define a separate model class for every response structure
class CustomerInfo(BaseModel):
    name: str
    vip_status: bool
    preferences: Dict[str, Union[bool, str]]

class Item(BaseModel):
    item_id: int
    name: str
    price: float
    in_stock: bool

class OrderResponse(BaseModel):
    order_id: str
    status: str
    total_amount: float
    tags: List[str]
    customer_info: CustomerInfo
    items: List[Item]
    metadata: Optional[Dict[str, Any]] = None

app = FastAPI()

@app.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(order_id: str):
    return {
        "order_id": order_id,
        "status": "processing",
        "total_amount": 150.50,
        "tags": ["urgent", "new_customer"],
        "customer_info": {
            "name": "John Doe",
            "vip_status": False,
            "preferences": {"notifications": True, "theme": "dark"},
        },
        "items": [
            {
                "item_id": 1,
                "name": "Laptop Stand",
                "price": 45.00,
                "in_stock": True,
            },
        ],
        "metadata": None,
    }
```

### After (With AST Inference)

```python
from fastapi import FastAPI
from fastapi_ast_inference import infer_response

app = FastAPI()

# No model definition needed! Types are inferred from the return statement.
@app.get("/orders/{order_id}")
@infer_response
async def get_order(order_id: str):
    return {
        "order_id": order_id,
        "status": "processing",
        "total_amount": 150.50,
        "tags": ["urgent", "new_customer"],
        "customer_info": {
            "name": "John Doe",
            "vip_status": False,
            "preferences": {"notifications": True, "theme": "dark"},
        },
        "items": [
            {
                "item_id": 1,
                "name": "Laptop Stand",
                "price": 45.00,
                "in_stock": True,
            },
        ],
        "metadata": None,
    }
```

**Result:** Full OpenAPI schema with typed fields, zero boilerplate!

<img width="882" height="557" alt="image" src="https://github.com/user-attachments/assets/e52d44e9-6ff8-418f-948e-27eb5d979c5d" />

## Installation

```bash
pip install fastapi-ast-inference
```

## Usage

### Option 1: Decorator (Recommended)

Use the `@infer_response` decorator on specific endpoints — no additional configuration needed:

```python
from fastapi import FastAPI
from fastapi_ast_inference import infer_response

app = FastAPI()

@app.get("/")
@infer_response
async def root():
    return {"message": "Hello, World!", "count": 42}

@app.get("/users/{user_id}")
@infer_response
async def get_user(user_id: int):
    return {"id": user_id, "name": "John", "active": True}
```

### Option 2: App-Wide Configuration

> ⚠️ **Note:** This affects ALL endpoints in your application.

Apply AST inference to all routes automatically:

```python
from fastapi import FastAPI
from fastapi_ast_inference import InferredAPIRoute

app = FastAPI()
app.router.route_class = InferredAPIRoute  # Affects entire app

@app.get("/")
async def root():
    return {"message": "Hello, World!", "count": 42}
```

### Option 3: Router-Level Configuration

> ⚠️ **Note:** This affects all endpoints in the router.

Apply to specific routers:

```python
from fastapi import APIRouter
from fastapi_ast_inference import InferredAPIRoute, create_inferred_router

# Using the helper function
router = create_inferred_router(prefix="/api/v1", tags=["api"])

# Or manually
router = APIRouter(route_class=InferredAPIRoute)  # Affects entire router

@router.get("/items")
async def get_items():
    return {"items": ["a", "b", "c"], "total": 3}
```

### Option 4: Programmatic API

Use the inference function directly for custom use cases:

```python
from fastapi_ast_inference import infer_response_model_from_ast

def my_endpoint():
    return {"name": "test", "value": 123}

model = infer_response_model_from_ast(my_endpoint)
# model is now a Pydantic BaseModel with 'name: str' and 'value: int' fields
```

## Supported Patterns

### ✅ Direct Dictionary Literals

```python
@app.get("/")
async def endpoint():
    return {"key": "value", "number": 42, "flag": True}
```

### ✅ Variable Returns

```python
@app.get("/")
async def endpoint():
    data = {"status": "ok", "items": [1, 2, 3]}
    return data
```

### ✅ Annotated Variables

```python
@app.get("/")
async def endpoint():
    result: Dict[str, Any] = {"count": 100, "active": True}
    return result
```

### ✅ Nested Structures

```python
@app.get("/")
async def endpoint():
    return {
        "user": {"name": "John", "age": 30},
        "settings": {"theme": "dark", "notifications": True}
    }
```

### ✅ Type Inference from Arguments

```python
@app.get("/items/{item_id}")
async def get_item(item_id: int, name: str):
    return {"id": item_id, "name": name}  # Types inferred from parameters
```

### ❌ Not Supported

- **Multiple return statements** (different structures in if/else)
- **Dynamic dictionary construction** (e.g., `dict(key=value)`)
- **Function call returns** (e.g., `return some_function()`)
- **Non-string dictionary keys**

## How It Works

1. **At Application Startup**: When FastAPI registers routes, the library intercepts endpoint functions.

2. **AST Analysis**: The source code is parsed into an Abstract Syntax Tree.

3. **Type Inference**: Return statements are analyzed to extract dictionary structure and infer types:
   - Constants → their Python types (`"hello"` → `str`, `42` → `int`)
   - Lists → `List[T]` where T is inferred from elements
   - Nested dicts → nested Pydantic models
   - Function arguments → types from annotations

4. **Model Generation**: A Pydantic model is dynamically created with the inferred fields.

5. **OpenAPI Integration**: The generated model is used for response documentation.

## Performance

- **Zero runtime overhead**: AST analysis happens once at startup, not per request
- **Cached results**: Inferred models are stored and reused
- **Graceful fallback**: If inference fails, standard FastAPI behavior is preserved

## Logging

Enable debug logging to see inference decisions:

```python
import logging
logging.getLogger("fastapi_ast_inference").setLevel(logging.DEBUG)
```

Example output:
```
DEBUG:fastapi_ast_inference:AST inference skipped for 'get_data': multiple return statements detected (2)
DEBUG:fastapi_ast_inference:AST inference skipped for 'get_external': return value is not a dict literal
```

## API Reference

### `infer_response_model_from_ast(func) -> Optional[Type[BaseModel]]`

Analyze a function and return an inferred Pydantic model, or None if inference fails.

### `@infer_response`

Decorator that pre-computes the inferred model and sets it as the function's return annotation. Works independently without `InferredAPIRoute`.

### `InferredAPIRoute`

Custom route class that automatically applies AST inference to endpoints.

### `create_inferred_router(**kwargs) -> APIRouter`

Create an APIRouter with `InferredAPIRoute` as the default route class.

### `get_inferred_model(func) -> Optional[Type[BaseModel]]`

Retrieve the inferred model from a decorated function.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

