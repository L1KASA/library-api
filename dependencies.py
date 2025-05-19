from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from starlette import status

from app.models import Librarian
from app.repositories.book_repository import BookRepository
from app.repositories.librarian_repository import LibrarianRepository
from app.repositories.reader_repository import ReaderRepository
from app.services.auth_service import AuthService
from app.services.book_service import BookService
from app.services.librarian_service import LibrarianService
from app.services.reader_service import ReaderService
from database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_db_session(db: Session = Depends(get_db)):
    return db

def get_librarian_repository(db: Session = Depends(get_db)) -> LibrarianRepository:
    return LibrarianRepository(db)

def get_librarian_service(librarian_repo: LibrarianRepository = Depends(get_librarian_repository)) -> LibrarianService:
    return LibrarianService(librarian_repo)

def get_auth_service(librarian_repo: LibrarianRepository = Depends(get_librarian_repository)) -> AuthService:
    return AuthService(librarian_repo)

def get_current_user(
        token: str = Depends(oauth2_scheme),
        auth_service: AuthService = Depends(get_auth_service)
) -> Librarian:
    payload = auth_service.verify_token(token)
    email: str = payload.get("sub")
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

    librarian = auth_service.repository.get_by_email(email)
    if librarian is None:
        raise HTTPException(status_code=404, detail="User not found")
    return librarian

def get_reader_repository(db: Session = Depends(get_db)) -> ReaderRepository:
    return ReaderRepository(db)

def get_reader_service(reader_repo: ReaderRepository = Depends(get_reader_repository)) -> ReaderService:
    return ReaderService(reader_repo)

def get_book_repository(db: Session = Depends(get_db)) -> BookRepository:
    return BookRepository(db)

def get_book_service(book_repo: BookRepository = Depends(get_book_repository)) -> BookService:
    return BookService(book_repo)