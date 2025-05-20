from typing import List

from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from app.models import Librarian
from app.schemas.librarian_schema import LibrarianCreate, LibrarianResponse, LibrarianUpdate
from app.services.librarian_service import LibrarianService
from dependencies import get_librarian_service, get_current_user

router = APIRouter(prefix="/librarians", tags=["Librarians"])


@router.post("/", response_model=LibrarianResponse)
def create(
        data: LibrarianCreate,
        service: LibrarianService = Depends(get_librarian_service)
):
    try:
        return service.create(data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/{id}", response_model=LibrarianResponse)
def update(
        id: int,
        data: LibrarianUpdate,
        service: LibrarianService = Depends(get_librarian_service),
        current_user: Librarian = Depends(get_current_user)
):
    try:
        if current_user.id != id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
        return service.update(id, data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(
        id: int,
        service: LibrarianService = Depends(get_librarian_service),
        current_user: Librarian = Depends(get_current_user)
):
    if current_user.id != id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    if not service.delete(id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")


@router.get("/by-id/{id}", response_model=LibrarianResponse)
def get_by_id(
        id: int,
        service: LibrarianService = Depends(get_librarian_service),
        current_user: Librarian = Depends(get_current_user)
):
    librarian = service.get_by_id(id)
    if not librarian:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Librarian not found")
    return librarian


@router.get('/by-email/{email}', response_model=LibrarianResponse)
def get_by_email(
        email: str,
        service: LibrarianService = Depends(get_librarian_service),
        current_user: Librarian = Depends(get_current_user)
):
    librarian = service.get_by_email(email)
    if not librarian:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Librarian with the email not found")
    return librarian


@router.get('/', response_model=List[LibrarianResponse])
def get_all(
        service: LibrarianService = Depends(get_librarian_service),
        # current_user: Librarian = Depends(get_current_user)
):
    librarians = service.get_all()
    if not librarians:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No librarians")
    return librarians
