from unittest.mock import MagicMock, create_autospec
from datetime import datetime

import pytest
from pydantic import SecretStr
from sqlalchemy.exc import SQLAlchemyError

from app.models import Librarian, Person
from app.repositories.librarian_repository import LibrarianRepository
from app.schemas.librarian_schema import LibrarianCreate, LibrarianUpdate, LibrarianRepoCreate, LibrarianRepoUpdate
from app.schemas.person_schema import PersonUpdate, PersonCreate
from app.services.librarian_service import LibrarianService
from app.utils.security import PasswordSecurity


class TestLibrarianService:
    @pytest.fixture
    def mock_repository(self):
        return create_autospec(LibrarianRepository)

    @pytest.fixture
    def mock_password_security(self):
        security = create_autospec(PasswordSecurity)
        security.get_password_hash.return_value = "hashed_password"
        return security

    @pytest.fixture
    def librarian_service(self, mock_repository, mock_password_security):
        return LibrarianService(repository=mock_repository, password_security=mock_password_security)

    @pytest.fixture
    def sample_librarian(self):
        person = Person(
            id=1,
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com"
        )
        return Librarian(
            id=1,
            person=person,
            hash_password="hashed_password",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

    @pytest.fixture
    def librarian_create_data(self):
        return LibrarianCreate(
            person=PersonCreate(
                first_name="John",
                last_name="Doe",
                surname="",
                email="john.doe@example.com"
            ),
            password=SecretStr("password123")
        )

    @pytest.fixture
    def librarian_update_data(self):
        return LibrarianUpdate(
            person=PersonUpdate(
                first_name="Updated",
                last_name="Name",
                email="updated@example.com"
            )
        )

    def test_create_librarian_success(self, librarian_service, mock_repository, mock_password_security, librarian_create_data):
        # Arrange
        mock_repository.get_by_email.return_value = None
        expected_librarian = MagicMock()
        mock_repository.create.return_value = expected_librarian

        # Act
        result = librarian_service.create(librarian_create_data)

        # Assert
        assert result == expected_librarian
        mock_repository.get_by_email.assert_called_once_with(librarian_create_data.person.email)
        mock_password_security.get_password_hash.assert_called_once_with(librarian_create_data.password)
        mock_repository.create.assert_called_once()
        call_args = mock_repository.create.call_args[0][0]
        assert isinstance(call_args, LibrarianRepoCreate)
        assert call_args.hashed_password == "hashed_password"

    def test_create_librarian_with_existing_email(self, librarian_service, mock_repository, librarian_create_data):
        # Arrange
        mock_repository.get_by_email.return_value = MagicMock()

        # Act & Assert
        with pytest.raises(ValueError, match="Email already in use"):
            librarian_service.create(librarian_create_data)

    def test_create_librarian_repository_error(self, librarian_service, mock_repository, librarian_create_data):
        # Arrange
        mock_repository.get_by_email.return_value = None
        mock_repository.create.side_effect = SQLAlchemyError("DB error")

        # Act & Assert
        with pytest.raises(ValueError, match="Failed to create librarian"):
            librarian_service.create(librarian_create_data)

    def test_update_librarian_success(self, librarian_service, mock_repository, sample_librarian, librarian_update_data):
        # Arrange
        mock_repository.get_by_id.return_value = sample_librarian
        mock_repository.get_by_email.return_value = None
        mock_repository.update.return_value = sample_librarian

        # Act
        result = librarian_service.update(sample_librarian.id, librarian_update_data)

        # Assert
        assert result == sample_librarian
        mock_repository.get_by_id.assert_called_once_with(sample_librarian.id)
        mock_repository.update.assert_called_once_with(
            sample_librarian.id,
            LibrarianRepoUpdate(person=librarian_update_data.person)
        )

    def test_update_librarian_not_found(self, librarian_service, mock_repository, librarian_update_data):
        # Arrange
        mock_repository.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(ValueError, match="Librarian not found"):
            librarian_service.update(999, librarian_update_data)

    def test_update_librarian_with_existing_email(self, librarian_service, mock_repository, sample_librarian, librarian_update_data):
        # Arrange
        mock_repository.get_by_id.return_value = sample_librarian
        mock_repository.get_by_email.return_value = MagicMock()  # Simulate existing email

        # Act & Assert
        with pytest.raises(ValueError, match="New email already in use"):
            librarian_service.update(sample_librarian.id, librarian_update_data)

    def test_update_librarian_repository_error(self, librarian_service, mock_repository, sample_librarian, librarian_update_data):
        # Arrange
        mock_repository.get_by_id.return_value = sample_librarian
        mock_repository.get_by_email.return_value = None
        mock_repository.update.side_effect = SQLAlchemyError("DB error")

        # Act & Assert
        with pytest.raises(ValueError, match="Failed to update librarian"):
            librarian_service.update(sample_librarian.id, librarian_update_data)

    def test_delete_librarian_success(self, librarian_service, mock_repository, sample_librarian):
        # Arrange
        mock_repository.get_by_id.return_value = sample_librarian
        mock_repository.delete.return_value = True

        # Act
        result = librarian_service.delete(sample_librarian.id)

        # Assert
        assert result is True
        mock_repository.get_by_id.assert_called_once_with(sample_librarian.id)
        mock_repository.delete.assert_called_once_with(sample_librarian.id)

    def test_delete_librarian_not_found(self, librarian_service, mock_repository):
        # Arrange
        mock_repository.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(ValueError, match="Librarian not found"):
            librarian_service.delete(999)

    def test_delete_librarian_repository_error(self, librarian_service, mock_repository, sample_librarian):
        # Arrange
        mock_repository.get_by_id.return_value = sample_librarian
        mock_repository.delete.side_effect = SQLAlchemyError("DB error")

        # Act & Assert
        with pytest.raises(ValueError, match="Failed to delete librarian"):
            librarian_service.delete(sample_librarian.id)

    def test_get_librarian_by_id_success(self, librarian_service, mock_repository, sample_librarian):
        # Arrange
        mock_repository.get_by_id.return_value = sample_librarian

        # Act
        result = librarian_service.get_by_id(sample_librarian.id)

        # Assert
        assert result == sample_librarian
        mock_repository.get_by_id.assert_called_once_with(sample_librarian.id)

    def test_get_librarian_by_id_not_found(self, librarian_service, mock_repository):
        # Arrange
        mock_repository.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(ValueError, match="Librarian not found"):
            librarian_service.get_by_id(999)

    def test_get_librarian_by_id_repository_error(self, librarian_service, mock_repository):
        # Arrange
        mock_repository.get_by_id.side_effect = SQLAlchemyError("DB error")

        # Act & Assert
        with pytest.raises(ValueError, match="Failed to get librarian"):
            librarian_service.get_by_id(1)

    def test_get_librarian_by_email_success(self, librarian_service, mock_repository, sample_librarian):
        # Arrange
        email = "john.doe@example.com"
        mock_repository.get_by_email.return_value = sample_librarian

        # Act
        result = librarian_service.get_by_email(email)

        # Assert
        assert result == sample_librarian
        mock_repository.get_by_email.assert_called_once_with(email)

    def test_get_librarian_by_invalid_email(self, librarian_service):
        # Arrange
        invalid_email = "invalid-email"

        # Act & Assert
        with pytest.raises(ValueError, match="Invalid email format"):
            librarian_service.get_by_email(invalid_email)

    def test_get_librarian_by_email_not_found(self, librarian_service, mock_repository):
        # Arrange
        email = "not.found@example.com"
        mock_repository.get_by_email.return_value = None

        # Act & Assert
        with pytest.raises(ValueError, match="Librarian not found"):
            librarian_service.get_by_email(email)

    def test_get_librarian_by_email_repository_error(self, librarian_service, mock_repository):
        # Arrange
        email = "test@example.com"
        mock_repository.get_by_email.side_effect = SQLAlchemyError("DB error")

        # Act & Assert
        with pytest.raises(ValueError, match="Failed to get librarian"):
            librarian_service.get_by_email(email)

    def test_get_all_librarians_success(self, librarian_service, mock_repository, sample_librarian):
        # Arrange
        expected_librarians = [sample_librarian]
        mock_repository.get_all.return_value = expected_librarians

        # Act
        result = librarian_service.get_all()

        # Assert
        assert result == expected_librarians
        mock_repository.get_all.assert_called_once()

    def test_get_all_librarians_empty(self, librarian_service, mock_repository):
        # Arrange
        mock_repository.get_all.return_value = []

        # Act & Assert
        with pytest.raises(ValueError, match="No librarians found"):
            librarian_service.get_all()

    def test_get_all_librarians_repository_error(self, librarian_service, mock_repository):
        # Arrange
        mock_repository.get_all.side_effect = SQLAlchemyError("DB error")

        # Act & Assert
        with pytest.raises(ValueError, match="Failed to get all librarians"):
            librarian_service.get_all()