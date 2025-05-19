from typing import List

from fastapi import APIRouter, Depends, HTTPException
#from sqlalchemy.testing.pickleable import User
from starlette import status

from app.models import Reader, Librarian
from app.schemas.reader_schema import ReaderResponse, ReaderUpdate, ReaderCreate
from app.services.reader_service import ReaderService
from dependencies import get_reader_service, get_current_user

router = APIRouter(prefix="/readers", tags=["Readers"])

@router.post("/", response_model=ReaderResponse)
def create(
    data: ReaderCreate,
    service: ReaderService = Depends(get_reader_service)
):
    try:
        return service.create(data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.put("/{id}", response_model=ReaderResponse)
def update(
        id: int,
        data: ReaderUpdate,
        service: ReaderService = Depends(get_reader_service),
        current_user: Librarian = Depends(get_current_user)
):
    try:
        return service.update(id, data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(
        id: int,
        service: ReaderService = Depends(get_reader_service),
        current_user: Librarian = Depends(get_current_user)
):
    if not service.delete(id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

@router.get("/by-id/{id}", response_model=ReaderResponse)
def get_by_id(
        id: int,
        service: ReaderService = Depends(get_reader_service),
        current_user: Librarian = Depends(get_current_user)
):
    reader = service.get_by_id(id)
    if not reader:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reader not found")
    return reader

@router.get('/by-email/{email}', response_model=ReaderResponse)
def get_by_email(
        email: str,
        service: ReaderService = Depends(get_reader_service),
        current_user: Librarian = Depends(get_current_user)
):

    reader = service.get_by_email(email)
    if not reader:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reader with the email not found")
    return reader

@router.get('/', response_model=List[ReaderResponse])
def get_all(
        service: ReaderService = Depends(get_reader_service),
        #current_user: Librarian = Depends(get_current_user)
):
    readers = service.get_all()
    if not readers:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No readers")
    return readers