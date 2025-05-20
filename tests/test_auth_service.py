from datetime import datetime, timedelta, timezone
from unittest.mock import create_autospec, MagicMock

import pytest
from jose import jwt
from pydantic import SecretStr

from app.models import Librarian, Person
from app.repositories.librarian_repository import LibrarianRepository
from app.services.auth_service import AuthService
from app.utils.security import SecuritySettings, PasswordSecurity


class TestAuthService:
    @pytest.fixture
    def mock_repository(self):
        return create_autospec(LibrarianRepository)

    @pytest.fixture
    def mock_password_security(self):
        security = create_autospec(PasswordSecurity)
        security.verify_password.return_value = True
        security.get_password_hash.return_value = "new_hashed_password"
        return security

    @pytest.fixture
    def mock_security_settings(self):
        settings = create_autospec(SecuritySettings)
        settings.secret_key = SecretStr("test_secret_key")
        settings.algorithm = "HS256"
        settings.access_token_expire_minutes = 30
        return settings

    @pytest.fixture
    def auth_service(self, mock_repository, mock_password_security, mock_security_settings):
        return AuthService(
            repository=mock_repository,
            password_security=mock_password_security,
            security_settings=mock_security_settings
        )

    @pytest.fixture
    def sample_librarian(self):
        person = Person(
            id=1,
            first_name="Admin",
            last_name="User",
            email="admin@example.com"
        )
        return Librarian(
            id=1,
            person=person,
            hash_password="hashed_password",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

    def test_authenticate_success(self, auth_service, mock_repository, mock_password_security, sample_librarian):
        # Arrange
        email = "admin@example.com"
        password = SecretStr("password123")
        mock_repository.get_by_email.return_value = sample_librarian
        mock_password_security.verify_password.return_value = True

        # Act
        result = auth_service.authenticate(email, password)

        # Assert
        assert result == sample_librarian
        mock_repository.get_by_email.assert_called_once_with(email)
        mock_password_security.verify_password.assert_called_once_with(password, sample_librarian.hash_password)

    def test_authenticate_invalid_email(self, auth_service, mock_repository):
        # Arrange
        email = "nonexistent@example.com"
        password = SecretStr("password123")
        mock_repository.get_by_email.return_value = None

        # Act & Assert
        with pytest.raises(ValueError, match="Invalid email or password"):
            auth_service.authenticate(email, password)

    def test_authenticate_invalid_password(self, auth_service, mock_repository, mock_password_security,
                                           sample_librarian):
        # Arrange
        email = "admin@example.com"
        password = SecretStr("wrong_password")
        mock_repository.get_by_email.return_value = sample_librarian
        mock_password_security.verify_password.return_value = False

        # Act & Assert
        with pytest.raises(ValueError, match="Invalid email or password"):
            auth_service.authenticate(email, password)

    def test_authenticate_repository_error(self, auth_service, mock_repository):
        # Arrange
        email = "admin@example.com"
        password = SecretStr("password123")
        mock_repository.get_by_email.side_effect = Exception("DB error")

        # Act & Assert
        with pytest.raises(ValueError, match="Authentication failed"):
            auth_service.authenticate(email, password)

    def test_create_access_token_success(self, auth_service, mock_security_settings):
        # Arrange
        data = {"sub": "admin@example.com"}

        # Act
        token = auth_service.create_access_token(data)

        # Assert
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_error(self, auth_service, mock_security_settings):
        # Arrange
        data = {"sub": "admin@example.com"}
        # Create a new MagicMock for secret_key that will raise an exception
        mock_secret_key = MagicMock()
        mock_secret_key.get_secret_value.side_effect = Exception("Key error")
        mock_security_settings.secret_key = mock_secret_key

        # Act & Assert
        with pytest.raises(ValueError, match="Failed to create access token"):
            auth_service.create_access_token(data)

    def test_verify_token_success(self, auth_service, mock_security_settings, sample_librarian):
        # Arrange
        test_payload = {"sub": sample_librarian.person.email, "exp": datetime.now(timezone.utc) + timedelta(minutes=30)}
        valid_token = jwt.encode(test_payload, mock_security_settings.secret_key.get_secret_value(),
                                 algorithm=mock_security_settings.algorithm)

        # Act
        payload = auth_service.verify_token(valid_token)

        # Assert
        assert payload == test_payload

    def test_verify_token_invalid(self, auth_service):
        # Arrange
        invalid_token = "invalid.token.here"

        # Act & Assert
        with pytest.raises(ValueError, match="Invalid token"):
            auth_service.verify_token(invalid_token)

    def test_verify_token_missing_subject(self, auth_service, mock_security_settings):
        # Arrange
        test_payload = {"exp": datetime.now(timezone.utc) + timedelta(minutes=30)}
        token_without_sub = jwt.encode(test_payload, mock_security_settings.secret_key.get_secret_value(),
                                       algorithm=mock_security_settings.algorithm)

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            auth_service.verify_token(token_without_sub)

        assert "Invalid token - subject is missing" in str(exc_info.value.__cause__)

    def test_verify_token_expired(self, auth_service, mock_security_settings):
        # Arrange
        test_payload = {"sub": "admin@example.com", "exp": datetime.now(timezone.utc) - timedelta(minutes=30)}
        expired_token = jwt.encode(test_payload, mock_security_settings.secret_key.get_secret_value(),
                                   algorithm=mock_security_settings.algorithm)

        # Act & Assert
        with pytest.raises(ValueError, match="Invalid token"):
            auth_service.verify_token(expired_token)

    def test_change_password_success(self, auth_service, mock_repository, mock_password_security, sample_librarian):
        # Arrange
        current_password = SecretStr("old_password")
        new_password = SecretStr("new_password")
        mock_password_security.verify_password.return_value = True
        mock_repository.change_password.return_value = sample_librarian

        # Act
        result = auth_service.change_password(current_password, new_password, sample_librarian)

        # Assert
        assert result == sample_librarian
        mock_password_security.verify_password.assert_called_once_with(current_password, sample_librarian.hash_password)
        mock_password_security.get_password_hash.assert_called_once_with(new_password)
        mock_repository.change_password.assert_called_once_with(sample_librarian.id, "new_hashed_password")

    def test_change_password_wrong_current(self, auth_service, mock_password_security, sample_librarian):
        # Arrange
        current_password = SecretStr("wrong_password")
        new_password = SecretStr("new_password")
        mock_password_security.verify_password.return_value = False

        # Act & Assert
        with pytest.raises(ValueError, match="Current password is incorrect"):
            auth_service.change_password(current_password, new_password, sample_librarian)

    def test_change_password_repository_error(self, auth_service, mock_repository, mock_password_security,
                                              sample_librarian):
        # Arrange
        current_password = SecretStr("old_password")
        new_password = SecretStr("new_password")
        mock_password_security.verify_password.return_value = True
        mock_repository.change_password.side_effect = Exception("DB error")

        # Act & Assert
        with pytest.raises(ValueError, match="Failed to change password"):
            auth_service.change_password(current_password, new_password, sample_librarian)