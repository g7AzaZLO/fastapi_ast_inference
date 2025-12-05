import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import uvicorn
from fastapi import FastAPI

from fastapi_ast_inference import InferredAPIRoute, infer_response


app = FastAPI(
    title="FastAPI AST Inference Demo",
    description="Демонстрация автоматического вывода моделей ответа из AST",
    version="0.1.0",
)
app.router.route_class = InferredAPIRoute


# =============================================================================
# Примеры с автоматическим выводом типов
# =============================================================================


@app.get("/simple", tags=["Авто-вывод"])
async def simple_endpoint():
    """Простой эндпоинт с базовыми типами."""
    return {
        "message": "Hello, World!",
        "count": 42,
        "active": True,
        "score": 3.14,
    }


@app.get("/nested", tags=["Авто-вывод"])
async def nested_endpoint():
    """Эндпоинт с вложенными структурами."""
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


@app.get("/with-lists", tags=["Авто-вывод"])
async def lists_endpoint():
    """Эндпоинт со списками."""
    return {
        "numbers": [1, 2, 3, 4, 5],
        "names": ["Alice", "Bob", "Charlie"],
        "items": [
            {"id": 1, "name": "Item 1"},
            {"id": 2, "name": "Item 2"},
        ],
    }


@app.get("/users/{user_id}", tags=["Авто-вывод"])
async def get_user(user_id: int, include_details: bool = False):
    """Эндпоинт с параметрами пути и query."""
    return {
        "id": user_id,
        "username": "testuser",
        "email": "test@example.com",
        "is_active": True,
    }


@app.get("/from-args/{item_id}", tags=["Авто-вывод"])
async def from_args_endpoint(item_id: int, name: str, price: float):
    """Типы выводятся из аннотаций аргументов."""
    return {
        "id": item_id,
        "name": name,
        "price": price,
    }


@app.get("/variable-return", tags=["Авто-вывод"])
async def variable_return_endpoint():
    """Возврат через переменную."""
    data = {
        "status": "success",
        "code": 200,
        "timestamp": "2024-01-01T00:00:00Z",
    }
    return data


# =============================================================================
# Примеры с декоратором @infer_response
# =============================================================================


@app.get("/decorated", tags=["Декоратор"])
@infer_response
async def decorated_endpoint():
    """Эндпоинт с декоратором @infer_response. Декоратор работает даже без установки app.router.route_class = InferredAPIRoute, т.к. он сам устанавливает модель в return annotation."""
    return {
        "decorated": True,
        "value": 100,
        "description": "Модель выведена декоратором",
    }


# =============================================================================
# Случаи без вывода (fallback к стандартному поведению)
# =============================================================================


@app.get("/multiple-returns", tags=["Без вывода"])
async def multiple_returns_endpoint(flag: bool = True):
    """Множественные return - вывод невозможен."""
    if flag:
        return {"type": "a", "value": 1}
    return {"type": "b", "value": 2}


@app.get("/function-call", tags=["Без вывода"])
async def function_call_endpoint():
    """Возврат вызова функции - вывод невозможен."""
    return dict(status="ok")


@app.get("/empty", tags=["Без вывода"])
async def empty_endpoint():
    """Пустой словарь - вывод невозможен."""
    return {}


# =============================================================================
# POST/PUT/DELETE примеры
# =============================================================================


@app.post("/users", tags=["CRUD"])
async def create_user():
    """Создание пользователя."""
    return {
        "id": 1,
        "created": True,
        "message": "User created successfully",
    }


@app.put("/users/{user_id}", tags=["CRUD"])
async def update_user(user_id: int):
    """Обновление пользователя."""
    return {
        "id": user_id,
        "updated": True,
        "message": "User updated successfully",
    }


@app.delete("/users/{user_id}", tags=["CRUD"])
async def delete_user(user_id: int):
    """Удаление пользователя."""
    return {
        "id": user_id,
        "deleted": True,
        "message": "User deleted successfully",
    }


# =============================================================================
# Сложные примеры
# =============================================================================


@app.get("/orders/{order_id}", tags=["Сложные"])
async def get_order(order_id: str):
    """Заказ с вложенной структурой."""
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


@app.get("/analytics", tags=["Сложные"])
async def get_analytics():
    """Аналитические данные."""
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
    print("\n📖 Откройте Swagger UI: http://127.0.0.1:8000/docs")
    print("📖 Или ReDoc: http://127.0.0.1:8000/redoc")
    print("\n" + "=" * 60 + "\n")
    
    uvicorn.run(app, host="127.0.0.1", port=8000)

