from datetime import datetime
from unittest.mock import MagicMock, create_autospec

import pytest
from sqlalchemy.exc import SQLAlchemyError

from app.models import Reader, Person
from app.models.borrowed_book_model import BorrowedBook
from app.repositories.reader_repository import ReaderRepository
from app.schemas.person_schema import PersonCreate, PersonUpdate
from app.schemas.reader_schema import ReaderCreate, ReaderUpdate
from app.services.reader_service import ReaderService


class TestReaderService:
    @pytest.fixture
    def mock_repository(self):
        return create_autospec(ReaderRepository)

    @pytest.fixture
    def reader_service(self, mock_repository):
        return ReaderService(repository=mock_repository)

    @pytest.fixture
    def sample_reader(self):
        person = Person(
            id=1,
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com"
        )
        return Reader(
            id=1,
            person=person,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

    @pytest.fixture
    def sample_reader_with_borrowings(self, sample_reader):
        sample_reader.borrowings = [
            BorrowedBook(returned_date=None),  # Unreturned book
            BorrowedBook(returned_date=datetime.now())  # Returned book
        ]
        return sample_reader

    @pytest.fixture
    def reader_create_data(self):
        return ReaderCreate(
            person=PersonCreate(
                first_name="John",
                last_name="Doe",
                surname="",
                email="john.doe@example.com"
            )
        )

    @pytest.fixture
    def reader_update_data(self):
        return ReaderUpdate(
            person=PersonUpdate(
                first_name="Updated",
                last_name="Name",
                email="updated@example.com"
            )
        )

    def test_create_reader_success(self, reader_service, mock_repository, reader_create_data):
        # Arrange
        mock_repository.get_by_email.return_value = None
        expected_reader = MagicMock()
        mock_repository.create.return_value = expected_reader

        # Act
        result = reader_service.create(reader_create_data)

        # Assert
        assert result == expected_reader
        mock_repository.get_by_email.assert_called_once_with(reader_create_data.person.email)
        mock_repository.create.assert_called_once_with(reader_create_data)

    def test_create_reader_with_existing_email(self, reader_service, mock_repository, reader_create_data):
        # Arrange
        mock_repository.get_by_email.return_value = MagicMock()

        # Act & Assert
        with pytest.raises(ValueError, match="Email already in use"):
            reader_service.create(reader_create_data)

    def test_create_reader_repository_error(self, reader_service, mock_repository, reader_create_data):
        # Arrange
        mock_repository.get_by_email.return_value = None
        mock_repository.create.side_effect = SQLAlchemyError("DB error")

        # Act & Assert
        with pytest.raises(ValueError, match="Failed to create reader"):
            reader_service.create(reader_create_data)

    def test_update_reader_success(self, reader_service, mock_repository, sample_reader, reader_update_data):
        # Arrange
        mock_repository.get_by_id.return_value = sample_reader
        mock_repository.get_by_email.return_value = None
        mock_repository.update.return_value = sample_reader

        # Act
        result = reader_service.update(sample_reader.id, reader_update_data)

        # Assert
        assert result == sample_reader
        mock_repository.get_by_id.assert_called_once_with(sample_reader.id)
        mock_repository.update.assert_called_once_with(sample_reader.id, reader_update_data)

    def test_update_reader_not_found(self, reader_service, mock_repository, reader_update_data):
        # Arrange
        mock_repository.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(ValueError, match="Reader not found"):
            reader_service.update(999, reader_update_data)

    def test_update_reader_with_existing_email(self, reader_service, mock_repository, sample_reader, reader_update_data):
        # Arrange
        mock_repository.get_by_id.return_value = sample_reader
        mock_repository.get_by_email.return_value = MagicMock()  # Simulate existing email

        # Act & Assert
        with pytest.raises(ValueError, match="New email already in use"):
            reader_service.update(sample_reader.id, reader_update_data)

    def test_update_reader_repository_error(self, reader_service, mock_repository, sample_reader, reader_update_data):
        # Arrange
        mock_repository.get_by_id.return_value = sample_reader
        mock_repository.get_by_email.return_value = None
        mock_repository.update.side_effect = SQLAlchemyError("DB error")

        # Act & Assert
        with pytest.raises(ValueError, match="Failed to update reader"):
            reader_service.update(sample_reader.id, reader_update_data)

    def test_delete_reader_success(self, reader_service, mock_repository, sample_reader):
        # Arrange
        mock_repository.get_by_id.return_value = sample_reader
        mock_repository.delete.return_value = True

        # Act
        result = reader_service.delete(sample_reader.id)

        # Assert
        assert result is True
        mock_repository.get_by_id.assert_called_once_with(sample_reader.id)
        mock_repository.delete.assert_called_once_with(sample_reader.id)

    def test_delete_reader_not_found(self, reader_service, mock_repository):
        # Arrange
        mock_repository.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(ValueError, match="Reader not found"):
            reader_service.delete(999)

    def test_delete_reader_with_unreturned_books(self, reader_service, mock_repository, sample_reader_with_borrowings):
        # Arrange
        mock_repository.get_by_id.return_value = sample_reader_with_borrowings
        mock_repository.delete.side_effect = ValueError("Cannot delete reader with borrowed books")

        # Act & Assert
        with pytest.raises(ValueError, match="Reader cannot be deleted because they have unreturned books"):
            reader_service.delete(sample_reader_with_borrowings.id)

        # Act & Assert
        with pytest.raises(ValueError, match="Reader cannot be deleted because they have unreturned books"):
            reader_service.delete(sample_reader_with_borrowings.id)

    def test_delete_reader_repository_error(self, reader_service, mock_repository, sample_reader):
        # Arrange
        mock_repository.get_by_id.return_value = sample_reader
        mock_repository.delete.side_effect = SQLAlchemyError("DB error")

        # Act & Assert
        with pytest.raises(ValueError, match="Failed to delete reader"):
            reader_service.delete(sample_reader.id)

    def test_get_reader_by_id_success(self, reader_service, mock_repository, sample_reader):
        # Arrange
        mock_repository.get_by_id.return_value = sample_reader

        # Act
        result = reader_service.get_by_id(sample_reader.id)

        # Assert
        assert result == sample_reader
        mock_repository.get_by_id.assert_called_once_with(sample_reader.id)

    def test_get_reader_by_id_not_found(self, reader_service, mock_repository):
        # Arrange
        mock_repository.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(ValueError, match="Reader not found"):
            reader_service.get_by_id(999)

    def test_get_reader_by_id_repository_error(self, reader_service, mock_repository):
        # Arrange
        mock_repository.get_by_id.side_effect = SQLAlchemyError("DB error")

        # Act & Assert
        with pytest.raises(ValueError, match="Failed to get reader"):
            reader_service.get_by_id(1)

    def test_get_reader_by_email_success(self, reader_service, mock_repository, sample_reader):
        # Arrange
        email = "john.doe@example.com"
        mock_repository.get_by_email.return_value = sample_reader

        # Act
        result = reader_service.get_by_email(email)

        # Assert
        assert result == sample_reader
        mock_repository.get_by_email.assert_called_once_with(email)

    def test_get_reader_by_invalid_email(self, reader_service):
        # Arrange
        invalid_email = "invalid-email"

        # Act & Assert
        with pytest.raises(ValueError, match="Invalid email format"):
            reader_service.get_by_email(invalid_email)

    def test_get_reader_by_email_not_found(self, reader_service, mock_repository):
        # Arrange
        email = "not.found@example.com"
        mock_repository.get_by_email.return_value = None

        # Act & Assert
        with pytest.raises(ValueError, match="Reader not found"):
            reader_service.get_by_email(email)

    def test_get_reader_by_email_repository_error(self, reader_service, mock_repository):
        # Arrange
        email = "test@example.com"
        mock_repository.get_by_email.side_effect = SQLAlchemyError("DB error")

        # Act & Assert
        with pytest.raises(ValueError, match="Failed to get reader by email"):
            reader_service.get_by_email(email)

    def test_get_all_readers_success(self, reader_service, mock_repository, sample_reader):
        # Arrange
        expected_readers = [sample_reader]
        mock_repository.get_all.return_value = expected_readers

        # Act
        result = reader_service.get_all()

        # Assert
        assert result == expected_readers
        mock_repository.get_all.assert_called_once()

    def test_get_all_readers_empty(self, reader_service, mock_repository):
        # Arrange
        mock_repository.get_all.return_value = []

        # Act & Assert
        with pytest.raises(ValueError, match="No readers found"):
            reader_service.get_all()

    def test_get_all_readers_repository_error(self, reader_service, mock_repository):
        # Arrange
        mock_repository.get_all.side_effect = SQLAlchemyError("DB error")

        # Act & Assert
        with pytest.raises(ValueError, match="Failed to get all readers"):
            reader_service.get_all()