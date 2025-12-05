"""Integration tests for the complete library."""

from typing import Any, Dict

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from fastapi_ast_inference import InferredAPIRoute, infer_response


class TestFullIntegration:
    """Full integration tests simulating real-world usage."""

    def test_complete_api_workflow(self):
        """Test a complete API with multiple endpoints."""
        print("\n✓ Тест: test_complete_api_workflow")
        app = FastAPI(title="Test API")
        app.router.route_class = InferredAPIRoute

        @app.get("/users/{user_id}")
        async def get_user(user_id: int):
            return {
                "id": user_id,
                "username": "testuser",
                "email": "test@example.com",
                "is_active": True,
            }

        @app.get("/orders/{order_id}")
        async def get_order(order_id: str):
            return {
                "order_id": order_id,
                "status": "processing",
                "total": 99.99,
                "items": [
                    {"name": "Item 1", "price": 49.99},
                    {"name": "Item 2", "price": 50.00},
                ],
            }

        @app.post("/users")
        async def create_user():
            return {"id": 1, "created": True}

        client = TestClient(app)

        # Test endpoint functionality
        user_response = client.get("/users/1")
        assert user_response.status_code == 200
        assert user_response.json()["id"] == 1

        order_response = client.get("/orders/abc123")
        assert order_response.status_code == 200
        assert order_response.json()["order_id"] == "abc123"

        create_response = client.post("/users")
        assert create_response.status_code == 200
        assert create_response.json()["created"] is True

        # Test OpenAPI schema
        schema_response = client.get("/openapi.json")
        assert schema_response.status_code == 200
        schema = schema_response.json()

        # Verify schemas were generated
        assert "/users/{user_id}" in schema["paths"]
        assert "/orders/{order_id}" in schema["paths"]
        assert "/users" in schema["paths"]

        # Check that user endpoint has proper schema
        user_schema = schema["paths"]["/users/{user_id}"]["get"]["responses"]["200"][
            "content"
        ]["application/json"]["schema"]
        assert "$ref" in user_schema
        print("  ✓ Успешно: полный API workflow работает корректно")

    def test_mixed_decorated_and_auto(self):
        """Test mixing decorated and auto-inferred endpoints."""
        print("\n✓ Тест: test_mixed_decorated_and_auto")
        app = FastAPI()
        app.router.route_class = InferredAPIRoute

        @app.get("/auto")
        async def auto_endpoint():
            return {"type": "auto", "value": 1}

        @app.get("/decorated")
        @infer_response
        async def decorated_endpoint():
            return {"type": "decorated", "value": 2}

        client = TestClient(app)

        # Both should work
        auto_response = client.get("/auto")
        assert auto_response.json()["type"] == "auto"

        decorated_response = client.get("/decorated")
        assert decorated_response.json()["type"] == "decorated"

        # Both should have schemas
        schema = client.get("/openapi.json").json()
        auto_schema = schema["paths"]["/auto"]["get"]["responses"]["200"]["content"][
            "application/json"
        ]["schema"]
        decorated_schema = schema["paths"]["/decorated"]["get"]["responses"]["200"][
            "content"
        ]["application/json"]["schema"]

        assert "$ref" in auto_schema
        assert "$ref" in decorated_schema
        print("  ✓ Успешно: смешанные декорированные и авто-выведенные эндпоинты работают")

    def test_edge_cases_in_real_app(self):
        """Test various edge cases in a real application context."""
        print("\n✓ Тест: test_edge_cases_in_real_app")
        app = FastAPI()
        app.router.route_class = InferredAPIRoute

        # Nested function should be ignored
        @app.get("/with-nested")
        async def endpoint_with_nested():
            def helper():
                return {"inner": "ignored"}

            helper()  # Call for coverage
            return {"outer": "value"}

        # Variable assignment
        @app.get("/with-variable")
        async def endpoint_with_variable():
            data = {"key": "value", "number": 42}
            return data

        # Type from arguments
        @app.get("/with-args/{item_id}")
        async def endpoint_with_args(item_id: int, name: str):
            return {"id": item_id, "name": name}

        client = TestClient(app)

        # All should work
        assert client.get("/with-nested").json() == {"outer": "value"}
        assert client.get("/with-variable").json() == {"key": "value", "number": 42}
        assert client.get("/with-args/1?name=test").json() == {"id": 1, "name": "test"}

        # Check schemas
        schema = client.get("/openapi.json").json()

        # Nested function endpoint should have schema for outer dict only
        nested_schema = schema["paths"]["/with-nested"]["get"]["responses"]["200"][
            "content"
        ]["application/json"]["schema"]
        assert "$ref" in nested_schema
        print("  ✓ Успешно: граничные случаи в реальном приложении обработаны")

    def test_openapi_schema_structure(self):
        """Test the structure of generated OpenAPI schema."""
        print("\n✓ Тест: test_openapi_schema_structure")
        app = FastAPI(title="Schema Test API", version="1.0.0")
        app.router.route_class = InferredAPIRoute

        @app.get("/test")
        async def test_endpoint():
            return {
                "string_field": "hello",
                "int_field": 42,
                "float_field": 3.14,
                "bool_field": True,
                "list_field": [1, 2, 3],
                "nested_field": {"inner": "value"},
            }

        client = TestClient(app)
        schema = client.get("/openapi.json").json()

        # Get the generated model schema
        response_schema = schema["paths"]["/test"]["get"]["responses"]["200"]["content"][
            "application/json"
        ]["schema"]
        ref_name = response_schema["$ref"].split("/")[-1]
        model_schema = schema["components"]["schemas"][ref_name]

        properties = model_schema["properties"]

        # Verify types
        assert properties["string_field"]["type"] == "string"
        assert properties["int_field"]["type"] == "integer"
        assert properties["float_field"]["type"] == "number"
        assert properties["bool_field"]["type"] == "boolean"
        assert properties["list_field"]["type"] == "array"
        assert "$ref" in properties["nested_field"]
        print("  ✓ Успешно: структура OpenAPI схемы корректна")


if __name__ == "__main__":
    pytest.main()


