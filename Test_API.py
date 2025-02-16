import pytest
import requests
import uuid
from datetime import datetime

BASE_URL = "https://qa-internship.avito.com"


@pytest.fixture
def created_item():
    """Фикстура для создания тестового объявления"""
    data = {
        "sellerID": 222222,
        "name": "Test Item",
        "price": 1000
    }
    response = requests.post(f"{BASE_URL}/api/1/item", json=data)
    return response.json()


# 1. Тесты создания объявления
@pytest.mark.parametrize("data, expected_code", [
    # Позитивные тесты
    ({"sellerID": 111111, "name": "Valid 1", "price": 100}, 200),
    ({"sellerID": 999999, "name": "Valid 2", "price": 999}, 200),
    # Негативные тесты
    ({"sellerID": 100000, "name": "Invalid", "price": 100}, 400),
    ({"sellerID": "text", "name": "Invalid", "price": 100}, 400),
    ({"name": "No SellerID", "price": 100}, 400),
    ({"sellerID": 123456, "price": 100}, 400),
])
def test_create_item(data, expected_code):
    response = requests.post(f"{BASE_URL}/api/1/item", json=data)
    assert response.status_code == expected_code


# 2. Тесты получения объявления
def test_get_item_valid_id(created_item):
    item_id = created_item.get("id")
    response = requests.get(f"{BASE_URL}/api/1/item/{item_id}")

    assert response.status_code == 200
    data = response.json()[0]

    # Проверка структуры ответа
    assert all(key in data for key in ["id", "sellerId", "name", "price", "createdAt"])

    # Проверка формата UUID
    try:
        uuid.UUID(data["id"], version=4)
    except ValueError:
        pytest.fail("Invalid UUID format")

    # Проверка формата даты
    try:
        datetime.fromisoformat(data["createdAt"])
    except ValueError:
        pytest.fail("Invalid date format")


def test_get_item_invalid_id():
    response = requests.get(f"{BASE_URL}/api/1/item/invalid_id")
    assert response.status_code == 404


# 3. Тесты объявлений продавца
def test_get_seller_items_valid():
    response = requests.get(f"{BASE_URL}/api/1/222222/item")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_seller_items_empty():
    response = requests.get(f"{BASE_URL}/api/1/111111/item")
    assert response.status_code == 200
    assert len(response.json()) == 0


def test_get_seller_items_invalid():
    response = requests.get(f"{BASE_URL}/api/1/abc/item")
    assert response.status_code == 400


# 4. Тесты статистики
def test_get_statistics_valid(created_item):
    item_id = created_item.get("id")
    response = requests.get(f"{BASE_URL}/api/1/statistic/{item_id}")

    assert response.status_code == 200
    stats = response.json()[0]
    assert all(key in stats for key in ["likes", "viewCount", "contacts"])


def test_get_statistics_invalid():
    random_uuid = uuid.uuid4()
    response = requests.get(f"{BASE_URL}/api/1/statistic/{random_uuid}")
    assert response.status_code == 404