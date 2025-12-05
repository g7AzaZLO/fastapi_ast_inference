"""Tests for decorator functionality."""

from typing import Any, Dict

import pytest

from fastapi_ast_inference import (
    INFERRED_MODEL_ATTR,
    InferResponseFactory,
    get_inferred_model,
    infer_response,
)


def _simple_endpoint() -> Dict[str, Any]:
    """Simple endpoint for testing."""
    return {"status": "ok", "count": 42}


def _complex_endpoint() -> Dict[str, Any]:
    """Complex endpoint with nested data."""
    return {
        "user": {"name": "John", "age": 30},
        "items": [1, 2, 3],
    }


def _no_inference_possible() -> Dict[str, Any]:
    """Endpoint where inference is not possible."""
    return {}.copy()  # Function call return


class TestInferResponseDecorator:
    """Tests for the @infer_response decorator."""

    def test_decorator_attaches_model(self):
        """Test that decorator attaches model to function."""
        print("\n✓ Тест: test_decorator_attaches_model")

        @infer_response
        def endpoint():
            return {"message": "hello"}

        endpoint()  # Execute for coverage
        assert hasattr(endpoint, INFERRED_MODEL_ATTR)
        model = getattr(endpoint, INFERRED_MODEL_ATTR)
        assert model is not None
        assert "message" in model.__annotations__
        print("  ✓ Успешно: декоратор прикрепил модель к функции")

    def test_decorator_with_complex_return(self):
        """Test decorator with complex return structure."""
        print("\n✓ Тест: test_decorator_with_complex_return")

        @infer_response
        def endpoint():
            return {"data": {"nested": "value"}, "items": [1, 2]}

        endpoint()
        model = get_inferred_model(endpoint)
        assert model is not None
        assert "data" in model.__annotations__
        assert "items" in model.__annotations__
        print("  ✓ Успешно: декоратор обработал сложную структуру возврата")

    def test_decorator_returns_none_when_inference_fails(self):
        """Test decorator sets None when inference fails."""
        print("\n✓ Тест: test_decorator_returns_none_when_inference_fails")

        @infer_response
        def endpoint():
            return {}.copy()

        endpoint()
        assert hasattr(endpoint, INFERRED_MODEL_ATTR)
        assert getattr(endpoint, INFERRED_MODEL_ATTR) is None
        print("  ✓ Успешно: декоратор установил None при неудачном выводе")

    def test_decorator_preserves_function(self):
        """Test that decorator preserves the original function."""
        print("\n✓ Тест: test_decorator_preserves_function")

        @infer_response
        def endpoint(x: int):
            return {"value": x}

        result = endpoint(42)
        assert result == {"value": 42}
        print("  ✓ Успешно: декоратор сохранил оригинальную функцию")


class TestGetInferredModel:
    """Tests for get_inferred_model helper."""

    def test_get_model_from_decorated_function(self):
        """Test getting model from decorated function."""
        print("\n✓ Тест: test_get_model_from_decorated_function")

        @infer_response
        def endpoint():
            return {"name": "test"}

        endpoint()
        model = get_inferred_model(endpoint)
        assert model is not None
        assert "name" in model.__annotations__
        print("  ✓ Успешно: модель получена из декорированной функции")

    def test_get_model_from_undecorated_function(self):
        """Test getting model from undecorated function returns None."""
        print("\n✓ Тест: test_get_model_from_undecorated_function")

        def endpoint():
            return {"name": "test"}

        endpoint()
        assert get_inferred_model(endpoint) is None
        print("  ✓ Успешно: не-декорированная функция возвращает None")

    def test_get_model_when_inference_failed(self):
        """Test getting model when inference failed returns None."""
        print("\n✓ Тест: test_get_model_when_inference_failed")

        @infer_response
        def endpoint():
            return {}.copy()

        endpoint()
        assert get_inferred_model(endpoint) is None
        print("  ✓ Успешно: неудачный вывод возвращает None")


class TestInferResponseFactory:
    """Tests for InferResponseFactory class."""

    def test_factory_basic_usage(self):
        """Test basic factory usage."""
        print("\n✓ Тест: test_factory_basic_usage")
        factory = InferResponseFactory()

        @factory
        def endpoint():
            return {"status": "active"}

        endpoint()
        model = get_inferred_model(endpoint)
        assert model is not None
        assert "status" in model.__annotations__
        print("  ✓ Успешно: фабрика работает в базовом режиме")

    def test_factory_strict_mode_success(self):
        """Test strict mode with successful inference."""
        print("\n✓ Тест: test_factory_strict_mode_success")
        factory = InferResponseFactory(strict=True)

        @factory
        def endpoint():
            return {"message": "hello"}

        endpoint()
        model = get_inferred_model(endpoint)
        assert model is not None
        print("  ✓ Успешно: строгий режим работает при успешном выводе")

    def test_factory_strict_mode_failure(self):
        """Test strict mode raises error on inference failure."""
        print("\n✓ Тест: test_factory_strict_mode_failure")
        factory = InferResponseFactory(strict=True)

        with pytest.raises(ValueError, match="Failed to infer"):

            @factory
            def endpoint():
                return {}.copy()
        print("  ✓ Успешно: строгий режим выбрасывает ошибку при неудаче")

    def test_factory_with_custom_prefix(self):
        """Test factory with custom model prefix."""
        print("\n✓ Тест: test_factory_with_custom_prefix")
        factory = InferResponseFactory(model_prefix="API")

        @factory
        def endpoint():
            return {"data": "value"}

        endpoint()
        model = get_inferred_model(endpoint)
        assert model is not None
        print("  ✓ Успешно: фабрика работает с кастомным префиксом")


if __name__ == "__main__":
    pytest.main()

