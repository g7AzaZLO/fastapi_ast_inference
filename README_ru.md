# FastAPI AST Inference

[![PyPI version](https://badge.fury.io/py/fastapi-ast-inference.svg)](https://badge.fury.io/py/fastapi-ast-inference)
[![Python Versions](https://img.shields.io/pypi/pyversions/fastapi-ast-inference.svg)](https://pypi.org/project/fastapi-ast-inference/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Автоматический вывод моделей ответа для FastAPI с использованием AST-анализа.**

Эта библиотека анализирует ваши функции-эндпоинты FastAPI при запуске приложения и автоматически генерирует Pydantic-модели для OpenAPI-документации на основе структур словарей, которые вы возвращаете.

## Зачем?

### До (Стандартный подход с Pydantic)

```python
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

# Нужно определять отдельный класс модели для каждой структуры ответа
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

### После (С AST Inference)

```python
from fastapi import FastAPI
from fastapi_ast_inference import infer_response

app = FastAPI()

# Определение модели не нужно! Типы выводятся из return-выражения.
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

**Результат:** Полная OpenAPI-схема с типизированными полями, ноль шаблонного кода!

<img width="882" height="557" alt="image" src="https://github.com/user-attachments/assets/679ce882-13b3-4b53-b1fe-cdea6c5ed3db" />


## Установка

```bash
pip install fastapi-ast-inference
```

## Использование

### Вариант 1: Декоратор (Рекомендуется)

Используйте декоратор `@infer_response` на конкретных эндпоинтах — никакой дополнительной настройки не нужно:

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

### Вариант 2: Конфигурация на уровне приложения

> ⚠️ **Внимание:** Это затронет ВСЕ эндпоинты в вашем приложении.

Применить AST-вывод ко всем маршрутам автоматически:

```python
from fastapi import FastAPI
from fastapi_ast_inference import InferredAPIRoute

app = FastAPI()
app.router.route_class = InferredAPIRoute  # Затрагивает всё приложение

@app.get("/")
async def root():
    return {"message": "Hello, World!", "count": 42}
```

### Вариант 3: Конфигурация на уровне роутера

> ⚠️ **Внимание:** Это затронет все эндпоинты в роутере.

Применить к определённым роутерам:

```python
from fastapi import APIRouter
from fastapi_ast_inference import InferredAPIRoute, create_inferred_router

# Используя вспомогательную функцию
router = create_inferred_router(prefix="/api/v1", tags=["api"])

# Или вручную
router = APIRouter(route_class=InferredAPIRoute)  # Затрагивает весь роутер

@router.get("/items")
async def get_items():
    return {"items": ["a", "b", "c"], "total": 3}
```

### Вариант 4: Программный API

Использовать функцию вывода напрямую для особых случаев:

```python
from fastapi_ast_inference import infer_response_model_from_ast

def my_endpoint():
    return {"name": "test", "value": 123}

model = infer_response_model_from_ast(my_endpoint)
# model теперь Pydantic BaseModel с полями 'name: str' и 'value: int'
```

## Поддерживаемые паттерны

### ✅ Прямые литералы словарей

```python
@app.get("/")
async def endpoint():
    return {"key": "value", "number": 42, "flag": True}
```

### ✅ Возврат через переменные

```python
@app.get("/")
async def endpoint():
    data = {"status": "ok", "items": [1, 2, 3]}
    return data
```

### ✅ Аннотированные переменные

```python
@app.get("/")
async def endpoint():
    result: Dict[str, Any] = {"count": 100, "active": True}
    return result
```

### ✅ Вложенные структуры

```python
@app.get("/")
async def endpoint():
    return {
        "user": {"name": "John", "age": 30},
        "settings": {"theme": "dark", "notifications": True}
    }
```

### ✅ Вывод типов из аргументов

```python
@app.get("/items/{item_id}")
async def get_item(item_id: int, name: str):
    return {"id": item_id, "name": name}  # Типы выводятся из параметров
```

### ❌ Не поддерживается

- **Множественные return-выражения** (разные структуры в if/else)
- **Динамическое построение словарей** (например, `dict(key=value)`)
- **Возврат вызовов функций** (например, `return some_function()`)
- **Не-строковые ключи словарей**

## Как это работает

1. **При запуске приложения**: Когда FastAPI регистрирует маршруты, библиотека перехватывает функции-эндпоинты.

2. **AST-анализ**: Исходный код парсится в абстрактное синтаксическое дерево.

3. **Вывод типов**: Анализируются return-выражения для извлечения структуры словаря и вывода типов:
   - Константы → их Python-типы (`"hello"` → `str`, `42` → `int`)
   - Списки → `List[T]`, где T выводится из элементов
   - Вложенные словари → вложенные Pydantic-модели
   - Аргументы функции → типы из аннотаций

4. **Генерация модели**: Pydantic-модель создаётся динамически с выведенными полями.

5. **Интеграция с OpenAPI**: Сгенерированная модель используется для документации ответа.

## Производительность

- **Нулевые накладные расходы в runtime**: AST-анализ происходит один раз при запуске, не при каждом запросе
- **Кэшированные результаты**: Выведенные модели сохраняются и переиспользуются
- **Graceful fallback**: Если вывод не удался, сохраняется стандартное поведение FastAPI

## Логирование

Включить отладочное логирование для просмотра решений вывода:

```python
import logging
logging.getLogger("fastapi_ast_inference").setLevel(logging.DEBUG)
```

Пример вывода:
```
DEBUG:fastapi_ast_inference:AST inference skipped for 'get_data': multiple return statements detected (2)
DEBUG:fastapi_ast_inference:AST inference skipped for 'get_external': return value is not a dict literal
```

## API Reference

### `infer_response_model_from_ast(func) -> Optional[Type[BaseModel]]`

Анализирует функцию и возвращает выведенную Pydantic-модель, или None если вывод не удался.

### `@infer_response`

Декоратор, который предварительно вычисляет выведенную модель и прикрепляет её к функции. Работает независимо от `InferredAPIRoute`.

### `InferredAPIRoute`

Пользовательский класс маршрута, который автоматически применяет AST-вывод к эндпоинтам.

### `create_inferred_router(**kwargs) -> APIRouter`

Создаёт APIRouter с `InferredAPIRoute` как класс маршрута по умолчанию.

### `get_inferred_model(func) -> Optional[Type[BaseModel]]`

Получает выведенную модель из декорированной функции.

## Лицензия

MIT License - см. [LICENSE](LICENSE) для деталей.

## Вклад в проект

Contributions welcome! Не стесняйтесь отправлять Pull Request.

