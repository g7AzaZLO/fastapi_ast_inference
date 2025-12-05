"""Tests for custom route class functionality."""

from typing import Any, Dict, List, Union

import pytest
from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

from fastapi_ast_inference import (
    InferredAPIRoute,
    create_inferred_router,
    infer_response,
)


def create_test_app() -> FastAPI:
    """Create a test FastAPI app with InferredAPIRoute."""
    app = FastAPI()
    app.router.route_class = InferredAPIRoute
    return app


class TestInferredAPIRoute:
    """Tests for InferredAPIRoute class."""

    def test_basic_inference(self):
        """Test basic response model inference."""
        print("\n✓ Тест: test_basic_inference")
        app = create_test_app()

        @app.get("/")
        async def endpoint():
            return {"message": "Hello", "count": 42}

        client = TestClient(app)
        response = client.get("/openapi.json")
        schema = response.json()

        # Check that response schema was generated
        path_schema = schema["paths"]["/"]["get"]["responses"]["200"]["content"][
            "application/json"
        ]["schema"]
        assert "$ref" in path_schema
        print("  ✓ Успешно: базовая модель ответа выведена")

    def test_nested_structure_inference(self):
        """Test inference with nested structures."""
        print("\n✓ Тест: test_nested_structure_inference")
        app = create_test_app()

        @app.get("/nested")
        async def endpoint():
            return {
                "user": {"name": "John", "age": 30},
                "items": [1, 2, 3],
            }

        client = TestClient(app)
        response = client.get("/openapi.json")
        schema = response.json()

        path_schema = schema["paths"]["/nested"]["get"]["responses"]["200"]["content"][
            "application/json"
        ]["schema"]
        assert "$ref" in path_schema
        print("  ✓ Успешно: вложенная структура выведена")

    def test_explicit_response_model_takes_precedence(self):
        """Test that explicit response_model overrides inference."""
        print("\n✓ Тест: test_explicit_response_model_takes_precedence")
        from pydantic import BaseModel

        class ExplicitModel(BaseModel):
            explicit_field: str

        app = create_test_app()

        @app.get("/explicit", response_model=ExplicitModel)
        async def endpoint():
            return {"explicit_field": "value", "ignored": 123}

        client = TestClient(app)
        response = client.get("/openapi.json")
        schema = response.json()

        # Should use ExplicitModel, not inferred model
        ref = schema["paths"]["/explicit"]["get"]["responses"]["200"]["content"][
            "application/json"
        ]["schema"]["$ref"]
        assert "ExplicitModel" in ref
        print("  ✓ Успешно: явная модель ответа имеет приоритет")

    def test_response_type_not_inferred(self):
        """Test that Response return type is not inferred."""
        print("\n✓ Тест: test_response_type_not_inferred")
        app = create_test_app()

        @app.get("/response")
        def endpoint() -> JSONResponse:
            return JSONResponse({"data": "value"})

        client = TestClient(app)
        response = client.get("/openapi.json")
        schema = response.json()

        # Should not have a $ref for Response types
        path_schema = schema["paths"]["/response"]["get"]["responses"]["200"]["content"][
            "application/json"
        ]["schema"]
        assert "$ref" not in path_schema
        print("  ✓ Успешно: тип Response не выводится")

    def test_decorator_takes_precedence(self):
        """Test that @infer_response decorator is used before auto-inference."""
        print("\n✓ Тест: test_decorator_takes_precedence")
        app = create_test_app()

        @app.get("/decorated")
        @infer_response
        async def endpoint():
            return {"decorated": True, "value": 100}

        client = TestClient(app)
        response = client.get("/openapi.json")
        schema = response.json()

        path_schema = schema["paths"]["/decorated"]["get"]["responses"]["200"]["content"][
            "application/json"
        ]["schema"]
        assert "$ref" in path_schema
        print("  ✓ Успешно: декоратор имеет приоритет над авто-выводом")

    def test_multiple_returns_no_inference(self):
        """Test that multiple returns result in no inference."""
        print("\n✓ Тест: test_multiple_returns_no_inference")
        app = create_test_app()

        @app.get("/multi")
        async def endpoint(flag: bool):
            if flag:
                return {"type": "a"}
            return {"type": "b"}

        client = TestClient(app)
        response = client.get("/openapi.json")
        schema = response.json()

        # Should not have $ref due to multiple returns
        path_schema = schema["paths"]["/multi"]["get"]["responses"]["200"]["content"][
            "application/json"
        ]["schema"]
        assert "$ref" not in path_schema
        print("  ✓ Успешно: множественные return не выводятся")

    def test_endpoint_execution(self):
        """Test that endpoints work correctly at runtime."""
        print("\n✓ Тест: test_endpoint_execution")
        app = create_test_app()

        @app.get("/")
        async def endpoint():
            return {"status": "ok", "value": 42}

        client = TestClient(app)
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"status": "ok", "value": 42}
        print("  ✓ Успешно: эндпоинт работает корректно в runtime")


class TestCreateInferredRouter:
    """Tests for create_inferred_router helper."""

    def test_router_uses_inferred_route(self):
        """Test that created router uses InferredAPIRoute."""
        print("\n✓ Тест: test_router_uses_inferred_route")
        router = create_inferred_router()
        assert router.route_class == InferredAPIRoute
        print("  ✓ Успешно: роутер использует InferredAPIRoute")

    def test_router_with_prefix(self):
        """Test router with prefix."""
        print("\n✓ Тест: test_router_with_prefix")
        router = create_inferred_router(prefix="/api/v1")
        assert router.prefix == "/api/v1"
        print("  ✓ Успешно: роутер работает с префиксом")

    def test_router_with_tags(self):
        """Test router with tags."""
        print("\n✓ Тест: test_router_with_tags")
        router = create_inferred_router(tags=["test"])
        assert "test" in router.tags
        print("  ✓ Успешно: роутер работает с тегами")

    def test_router_integration(self):
        """Test router integration with FastAPI app."""
        print("\n✓ Тест: test_router_integration")
        app = FastAPI()
        router = create_inferred_router(prefix="/api")

        @router.get("/items")
        async def get_items():
            return {"items": ["a", "b", "c"]}

        app.include_router(router)

        client = TestClient(app)
        response = client.get("/api/items")
        assert response.status_code == 200
        assert response.json() == {"items": ["a", "b", "c"]}
        print("  ✓ Успешно: роутер интегрирован с FastAPI приложением")


class TestContainsResponse:
    """Tests for _contains_response helper in route module."""

    def test_response_types(self):
        """Test detection of Response types."""
        print("\n✓ Тест: test_response_types")
        from fastapi_ast_inference.route import _contains_response

        assert _contains_response(Response) is True
        assert _contains_response(JSONResponse) is True
        assert _contains_response(str) is False
        assert _contains_response(Dict[str, Any]) is False
        assert _contains_response(Union[Response, dict]) is True
        assert _contains_response(Union[str, int]) is False
        assert _contains_response(List[str]) is False
        print("  ✓ Успешно: типы Response корректно определяются")


if __name__ == "__main__":
    pytest.main()

