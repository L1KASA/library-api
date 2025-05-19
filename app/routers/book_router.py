from typing import List

from fastapi import APIRouter, Depends, HTTPException, Body
from starlette import status

from app.models import Librarian
from app.schemas.book_schema import BookCreate, BookResponse, BookUpdate
from app.services.book_service import BookService
from dependencies import get_book_service, get_current_user

router = APIRouter(prefix="/books", tags=["Books"])

@router.post("/", response_model=BookResponse)
def create(
    data: BookCreate,
    service: BookService = Depends(get_book_service)
):
    try:
        return service.create(data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.put("/{id}", response_model=BookResponse)
def update(
        id: int,
        data: BookUpdate,
        service: BookService = Depends(get_book_service),
        current_user: Librarian = Depends(get_current_user)
):
    try:
        return service.update(id, data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(
        id: int,
        service: BookService = Depends(get_book_service),
        current_user: Librarian = Depends(get_current_user)
):
    if not service.delete(id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

@router.get("/by-id/{id}", response_model=BookResponse)
def get_by_id(
        id: int,
        service: BookService = Depends(get_book_service),
        current_user: Librarian = Depends(get_current_user)
):
    book = service.get_by_id(id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return book

@router.get('/', response_model=List[BookResponse])
def get_all(
        service: BookService = Depends(get_book_service),
        #current_user: Librarian = Depends(get_current_user)
):
    books = service.get_all()
    if not books:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No books")
    return books