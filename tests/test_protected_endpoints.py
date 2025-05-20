from datetime import datetime
from unittest.mock import create_autospec

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.models import Librarian, Person
from app.schemas.librarian_schema import LibrarianUpdate
from app.services.librarian_service import LibrarianService
from dependencies import get_current_user, get_librarian_service
from main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_librarian():
    person = Person(
        id=1,
        first_name="John",
        last_name="Doe",
        email="john@example.com"
    )
    librarian = Librarian(
        id=1,
        person=person,
        hash_password="hashed",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    return librarian


@pytest.fixture
def mock_librarian_service():
    service = create_autospec(LibrarianService)

    # Создаем корректный объект ответа
    person = Person(
        id=1,
        first_name="Updated",
        last_name="Name",
        email="updated@example.com"
    )
    librarian = Librarian(
        id=1,
        person=person,
        hash_password="hashed",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    service.update.return_value = librarian
    return service


def test_access_with_valid_token(client, mock_librarian, mock_librarian_service):
    try:
        # Переопределяем зависимости
        app.dependency_overrides[get_current_user] = lambda: mock_librarian
        app.dependency_overrides[get_librarian_service] = lambda: mock_librarian_service

        update_data = {
            "person": {
                "first_name": "Updated",
                "last_name": "Name",
                "email": "updated@example.com"
            }
        }

        response = client.put(
            "/librarians/1",
            json=update_data,
            headers={"Authorization": "Bearer valid_token"}
        )

        assert response.status_code == status.HTTP_200_OK
        mock_librarian_service.update.assert_called_once_with(1, LibrarianUpdate(**update_data))

        # Проверка структуры ответа
        response_data = response.json()
        assert response_data["id"] == 1
        assert response_data["person"]["email"] == "updated@example.com"
    finally:
        app.dependency_overrides.clear()


def test_access_without_token(client):
    response = client.put(
        "/librarians/1",
        json={
            "person": {
                "first_name": "Updated",
                "last_name": "Name",
                "email": "updated@example.com"
            }
        }
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "WWW-Authenticate" in response.headers