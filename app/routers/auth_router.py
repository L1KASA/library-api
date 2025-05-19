from sys import prefix

from fastapi import Depends, HTTPException, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from app.models import Librarian
from app.routers.librarian_router import router
from app.schemas.auth_schema import Token, ChangePasswordRequest
from app.services.auth_service import AuthService
from dependencies import get_auth_service, get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post('/login', response_model=Token)
def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        auth_service: AuthService = Depends(get_auth_service)
):
    librarian = auth_service.authenticate(form_data.username, form_data.password)
    if not librarian:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'}
        )

    access_token = auth_service.create_access_token(
        data={'sub': librarian.person.email}
    )
    return {'access_token': access_token, 'token_type': 'bearer'}

@router.patch('/change-password', status_code=status.HTTP_204_NO_CONTENT)
def change_password(
        passwords: ChangePasswordRequest,
        auth_service: AuthService = Depends(get_auth_service),
        current_user: Librarian = Depends(get_current_user),
):
    try:
        updated_librarian = auth_service.change_password(
            current_password=passwords.current_password,
            new_password=passwords.new_password,
            librarian=current_user
        )
        return updated_librarian
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
