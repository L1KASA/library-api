from unittest.mock import Mock

import pytest

from app.models.borrowed_book_model import BorrowedBook
from app.services.borrow_book_service import BorrowedBookService


class TestBorrowedBookService:
    @pytest.fixture
    def mock_repos(self):
        book_repo = Mock()
        borrow_repo = Mock()
        reader_repo = Mock()
        return book_repo, borrow_repo, reader_repo

    @pytest.fixture
    def service(self, mock_repos):
        book_repo, borrow_repo, reader_repo = mock_repos
        return BorrowedBookService(book_repo, borrow_repo, reader_repo)

    def test_borrow_book_success(self, service, mock_repos):
        book_repo, borrow_repo, reader_repo = mock_repos

        reader_repo.reader_exists.return_value = True
        book_repo.is_book_available.return_value = True
        borrow_repo.get_active_borrowings.return_value = []
        borrow_repo.create.return_value = BorrowedBook(
            book_id=1,
            reader_id=1,
            librarian_id=1
        )

        # Вызов метода
        result = service.borrow_book(book_id=1, reader_id=1, librarian_id=1)

        # Проверки
        assert isinstance(result, BorrowedBook)
        book_repo.decrease_book_copies.assert_called_once_with(1)
        borrow_repo.create.assert_called_once_with(1, 1, 1)

    def test_borrow_book_reader_not_found(self, service, mock_repos):
        book_repo, _, reader_repo = mock_repos
        reader_repo.reader_exists.return_value = False

        with pytest.raises(ValueError) as exc_info:
            service.borrow_book(book_id=1, reader_id=1, librarian_id=1)

        assert "Reader with ID 1 not found" in str(exc_info.value)

    def test_borrow_book_not_available(self, service, mock_repos):
        book_repo, _, reader_repo = mock_repos
        reader_repo.reader_exists.return_value = True
        book_repo.is_book_available.return_value = False

        with pytest.raises(ValueError) as exc_info:
            service.borrow_book(book_id=1, reader_id=1, librarian_id=1)

        assert "Book is not available for borrowing" in str(exc_info.value)

    def test_borrow_book_max_books_reached(self, service, mock_repos):
        book_repo, borrow_repo, reader_repo = mock_repos
        reader_repo.reader_exists.return_value = True
        book_repo.is_book_available.return_value = True
        borrow_repo.get_active_borrowings.return_value = [
            Mock(), Mock(), Mock()  # 3 книги уже взяты
        ]

        with pytest.raises(ValueError) as exc_info:
            service.borrow_book(book_id=1, reader_id=1, librarian_id=1)

        assert "Reader has reached the maximum number of borrowed books" in str(exc_info.value)

    def test_return_book_success(self, service, mock_repos):
        book_repo, borrow_repo, _ = mock_repos
        borrowing = BorrowedBook(book_id=1, reader_id=1, librarian_id=1)
        borrow_repo.get_active_borrowing.return_value = borrowing
        borrow_repo.mark_returned.return_value = borrowing

        result = service.return_book(book_id=1, reader_id=1)

        assert result == borrowing
        book_repo.increase_book_copies.assert_called_once_with(1)
        borrow_repo.mark_returned.assert_called_once_with(borrowing.id)

    def test_return_book_no_active_borrowing(self, service, mock_repos):
        _, borrow_repo, _ = mock_repos
        borrow_repo.get_active_borrowing.return_value = None

        with pytest.raises(ValueError) as exc_info:
            service.return_book(book_id=1, reader_id=1)

        assert "No active borrowing record found" in str(exc_info.value)