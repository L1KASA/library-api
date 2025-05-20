from typing import List

from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from app.schemas.borrowed_book_schema import BorrowedBookResponse
from app.services.borrow_book_service import BorrowedBookService
from dependencies import get_borrowed_book_service, get_current_user
from app.models import Librarian

router = APIRouter(prefix="/borrowings", tags=["Borrowings"])


@router.post("/borrow", response_model=BorrowedBookResponse)
def borrow_book(
        book_id: int,
        reader_id: int,
        service: BorrowedBookService = Depends(get_borrowed_book_service),
        current_user: Librarian = Depends(get_current_user)
):
    try:
        return service.borrow_book(
            book_id=book_id,
            reader_id=reader_id,
            librarian_id=current_user.id
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.patch("/return", response_model=BorrowedBookResponse)
def return_book(
        book_id: int,
        reader_id: int,
        service: BorrowedBookService = Depends(get_borrowed_book_service),
        current_user: Librarian = Depends(get_current_user)
):
    try:
        return service.return_book(book_id, reader_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/reader/{reader_id}", response_model=List[BorrowedBookResponse])
def get_reader_borrowings(
        reader_id: int,
        service: BorrowedBookService = Depends(get_borrowed_book_service),
        current_user: Librarian = Depends(get_current_user)
):
    try:
        return service.get_active_borrowings(reader_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/", response_model=List[BorrowedBookResponse])
def get_all_borrowings(
        service: BorrowedBookService = Depends(get_borrowed_book_service),
        current_user: Librarian = Depends(get_current_user)
):
    try:
        return service.get_all_active_borrowings()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )