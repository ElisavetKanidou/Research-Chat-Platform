"""
Authentication service for user management and JWT token handling
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.core.exceptions import AuthenticationException, ValidationException
from app.models.user import User


class AuthService:
    """Authentication service for user management"""

    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.algorithm = settings.ALGORITHM
        self.secret_key = settings.SECRET_KEY

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Hash a password"""
        return self.pwd_context.hash(password)

    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Create JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def verify_token(self, token: str, expected_type: str = "access") -> Dict[str, Any]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

            if payload.get("type") != expected_type:
                raise AuthenticationException("Invalid token type")

            return payload

        except JWTError as e:
            raise AuthenticationException(f"Invalid token: {str(e)}")

    async def authenticate_user(self, db: AsyncSession, email: str, password: str) -> Optional[User]:
        """Authenticate user by email and password"""
        # Get user by email
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if not user:
            return None

        if not self.verify_password(password, user.hashed_password):
            return None

        if not user.is_active:
            raise AuthenticationException("Account is deactivated")

        # Update last login
        user.update_last_login()
        await db.commit()

        return user

    async def create_user(
            self,
            db: AsyncSession,
            email: str,
            password: str,
            name: str,
            **kwargs
    ) -> User:
        """Create new user account"""

        # Check if email already exists
        result = await db.execute(select(User).where(User.email == email))
        if result.scalar_one_or_none():
            raise ValidationException("Email already registered")

        # Validate password strength
        if len(password) < 8:
            raise ValidationException("Password must be at least 8 characters long")

        # Create new user
        hashed_password = self.get_password_hash(password)

        user = User(
            email=email,
            name=name,
            hashed_password=hashed_password,
            **kwargs
        )

        db.add(user)
        await db.commit()
        await db.refresh(user)

        return user

    async def get_user_by_id(self, db: AsyncSession, user_id: str) -> Optional[User]:
        """Get user by ID"""
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_user_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """Get user by email"""
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    def create_token_pair(self, user: User) -> Dict[str, Any]:
        """Create access and refresh token pair"""
        token_data = {"sub": str(user.id), "email": user.email}

        access_token = self.create_access_token(token_data)
        refresh_token = self.create_refresh_token(token_data)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }

    async def refresh_access_token(self, db: AsyncSession, refresh_token: str) -> Dict[str, Any]:
        """Generate new access token from refresh token"""
        try:
            payload = self.verify_token(refresh_token, "refresh")
            user_id = payload.get("sub")

            if not user_id:
                raise AuthenticationException("Invalid token payload")

            user = await self.get_user_by_id(db, user_id)
            if not user or not user.is_active:
                raise AuthenticationException("User not found or inactive")

            # Create new access token
            token_data = {"sub": str(user.id), "email": user.email}
            access_token = self.create_access_token(token_data)

            return {
                "access_token": access_token,
                "token_type": "bearer",
                "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
            }

        except JWTError as e:
            raise AuthenticationException(f"Invalid refresh token: {str(e)}")

    async def change_password(
            self,
            db: AsyncSession,
            user: User,
            current_password: str,
            new_password: str
    ) -> bool:
        """Change user password"""

        # Verify current password
        if not self.verify_password(current_password, user.hashed_password):
            raise ValidationException("Current password is incorrect")

        # Validate new password
        if len(new_password) < 8:
            raise ValidationException("New password must be at least 8 characters long")

        if current_password == new_password:
            raise ValidationException("New password must be different from current password")

        # Update password
        user.hashed_password = self.get_password_hash(new_password)
        user.updated_at = datetime.utcnow()

        await db.commit()
        return True

    async def reset_password_request(self, db: AsyncSession, email: str) -> bool:
        """Initiate password reset process"""
        user = await self.get_user_by_email(db, email)
        if not user:
            # Don't reveal if email exists for security
            return True

        # Generate reset token (valid for 1 hour)
        reset_data = {"sub": str(user.id), "type": "password_reset"}
        reset_token = jwt.encode(
            {**reset_data, "exp": datetime.utcnow() + timedelta(hours=1)},
            self.secret_key,
            algorithm=self.algorithm
        )

        # TODO: Send email with reset token
        # This would typically integrate with an email service

        return True

    async def reset_password(self, db: AsyncSession, token: str, new_password: str) -> bool:
        """Reset password using reset token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

            if payload.get("type") != "password_reset":
                raise AuthenticationException("Invalid token type")

            user_id = payload.get("sub")
            user = await self.get_user_by_id(db, user_id)

            if not user:
                raise AuthenticationException("Invalid reset token")

            # Validate new password
            if len(new_password) < 8:
                raise ValidationException("Password must be at least 8 characters long")

            # Update password
            user.hashed_password = self.get_password_hash(new_password)
            user.updated_at = datetime.utcnow()

            await db.commit()
            return True

        except JWTError as e:
            raise AuthenticationException(f"Invalid or expired reset token: {str(e)}")

    async def deactivate_user(self, db: AsyncSession, user: User) -> bool:
        """Deactivate user account"""
        user.is_active = False
        user.updated_at = datetime.utcnow()
        await db.commit()
        return True

    async def verify_email(self, db: AsyncSession, token: str) -> bool:
        """Verify user email using verification token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

            if payload.get("type") != "email_verification":
                raise AuthenticationException("Invalid token type")

            user_id = payload.get("sub")
            user = await self.get_user_by_id(db, user_id)

            if not user:
                raise AuthenticationException("Invalid verification token")

            user.verify_email()
            await db.commit()
            return True

        except JWTError as e:
            raise AuthenticationException(f"Invalid or expired verification token: {str(e)}")


# Create global auth service instance
auth_service = AuthService()