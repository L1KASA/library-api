from datetime import datetime
from unittest.mock import MagicMock, create_autospec

import pytest
from sqlalchemy.exc import SQLAlchemyError

from app.models import Book
from app.repositories.book_repository import BookRepository
from app.schemas.book_schema import BookCreate, BookUpdate
from app.services.book_service import BookService


class TestBookService:
    @pytest.fixture
    def mock_repository(self):
        return create_autospec(BookRepository)

    @pytest.fixture
    def book_service(self, mock_repository):
        return BookService(repository=mock_repository)

    @pytest.fixture
    def sample_book(self):
        return Book(
            id=1,
            name="Sample Book",
            author="Author",
            year=2023,
            isbn="123-456-789",
            number_of_copies=5
        )

    @pytest.fixture
    def active_borrowing(self):
        borrowing = MagicMock()
        borrowing.returned_date = None
        return borrowing

    @pytest.fixture
    def returned_borrowing(self):
        borrowing = MagicMock()
        borrowing.returned_date = datetime.now()
        return borrowing

    def test_create_book_success(self, book_service, mock_repository):
        book_data = BookCreate(
            name="Test Book",
            author="Test Author",
            year=2023,
            isbn="123-456-789",
            number_of_copies=5
        )
        expected_book = Book(**book_data.model_dump())

        mock_repository.exists_by_isbn.return_value = False
        mock_repository.author_exists.return_value = True
        mock_repository.create.return_value = expected_book

        result = book_service.create(book_data)

        assert result == expected_book
        mock_repository.exists_by_isbn.assert_called_once_with(book_data.isbn)
        mock_repository.author_exists.assert_called_once_with(book_data.author)
        mock_repository.create.assert_called_once_with(book_data)

    def test_create_book_with_existing_isbn(self, book_service, mock_repository):
        book_data = BookCreate(
            name="Test Book",
            author="Test Author",
            year=2023,
            isbn="123-456-789",
            number_of_copies=5
        )
        mock_repository.exists_by_isbn.return_value = True

        with pytest.raises(ValueError, match="Book with this ISBN already exists"):
            book_service.create(book_data)

    def test_create_book_with_nonexistent_author(self, book_service, mock_repository):
        book_data = BookCreate(
            name="Test Book",
            author="Nonexistent Author",
            year=2023,
            isbn="123-456-789",
            number_of_copies=5
        )
        mock_repository.exists_by_isbn.return_value = False
        mock_repository.author_exists.return_value = False

        with pytest.raises(ValueError, match="Author does not exist in our database"):
            book_service.create(book_data)

    def test_update_book_success(self, book_service, mock_repository, sample_book):
        update_data = BookUpdate(name="Updated Name")
        mock_repository.exists.return_value = True
        mock_repository.isbn_exists_except_current.return_value = False
        mock_repository.update.return_value = sample_book

        result = book_service.update(sample_book.id, update_data)

        assert result == sample_book
        mock_repository.exists.assert_called_once_with(sample_book.id)
        mock_repository.update.assert_called_once_with(sample_book.id, update_data)

    def test_update_nonexistent_book(self, book_service, mock_repository):
        book_id = 999
        update_data = BookUpdate(name="Updated Name")
        mock_repository.exists.return_value = False

        with pytest.raises(ValueError, match="Book not found"):
            book_service.update(book_id, update_data)

    def test_delete_book_success(self, book_service, mock_repository, sample_book):
        mock_repository.get_by_id.return_value = sample_book
        mock_repository.delete.return_value = True

        result = book_service.delete(sample_book.id)

        assert result is True
        mock_repository.get_by_id.assert_called_once_with(sample_book.id)
        mock_repository.delete.assert_called_once_with(sample_book.id)

    def test_delete_nonexistent_book(self, book_service, mock_repository):
        book_id = 999
        mock_repository.get_by_id.return_value = None

        with pytest.raises(ValueError, match="Book not found"):
            book_service.delete(book_id)

    def test_delete_book_with_active_borrowings(
            self,
            book_service,
            mock_repository,
            sample_book,
            active_borrowing,
            returned_borrowing
    ):
        sample_book.borrowings = [active_borrowing, returned_borrowing]
        mock_repository.get_by_id.return_value = sample_book

        with pytest.raises(ValueError, match="Cannot delete book with active borrowings"):
            book_service.delete(sample_book.id)

    def test_delete_book_with_only_returned_borrowings(
            self,
            book_service,
            mock_repository,
            sample_book,
            returned_borrowing
    ):
        sample_book.borrowings = [returned_borrowing]
        mock_repository.get_by_id.return_value = sample_book
        mock_repository.delete.return_value = True

        result = book_service.delete(sample_book.id)

        assert result is True
        mock_repository.delete.assert_called_once_with(sample_book.id)

    def test_get_book_by_id_success(self, book_service, mock_repository, sample_book):
        mock_repository.get_by_id.return_value = sample_book

        result = book_service.get_by_id(sample_book.id)

        assert result == sample_book
        mock_repository.get_by_id.assert_called_once_with(sample_book.id)

    def test_get_nonexistent_book_by_id(self, book_service, mock_repository):
        book_id = 999
        mock_repository.get_by_id.return_value = None

        with pytest.raises(ValueError, match="Book not found"):
            book_service.get_by_id(book_id)

    def test_get_all_books_success(self, book_service, mock_repository, sample_book):
        expected_books = [sample_book]
        mock_repository.get_all.return_value = expected_books

        result = book_service.get_all()

        assert result == expected_books
        mock_repository.get_all.assert_called_once()

    def test_repository_error_handling(self, book_service, mock_repository):
        book_data = BookCreate(
            name="Test Book",
            author="Test Author",
            year=2023,
            isbn="123-456-789",
            number_of_copies=5
        )
        mock_repository.exists_by_isbn.return_value = False
        mock_repository.author_exists.return_value = True
        mock_repository.create.side_effect = SQLAlchemyError("DB error")

        with pytest.raises(ValueError, match="Failed to create librarian"):
            book_service.create(book_data)