"""
Authentication API endpoints
"""
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthenticationException, ValidationException
from app.database.session import get_db
from app.services.auth_service import auth_service
from app.schemas.auth import (
    LoginRequest, LoginResponse, RegisterRequest, RefreshTokenRequest,
    ChangePasswordRequest, ResetPasswordRequest, ResetPasswordConfirmRequest
)
from app.schemas.user import UserResponse
from app.models.user import User

router = APIRouter()
security = HTTPBearer()


async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: AsyncSession = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    try:
        token = credentials.credentials
        payload = auth_service.verify_token(token, "access")
        user_id = payload.get("sub")

        if user_id is None:
            raise AuthenticationException("Invalid token payload")

        user = await auth_service.get_user_by_id(db, user_id)
        if user is None or not user.is_active:
            raise AuthenticationException("User not found or inactive")

        return user

    except AuthenticationException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/register", response_model=LoginResponse)
async def register(
        user_data: RegisterRequest,
        db: AsyncSession = Depends(get_db)
) -> Any:
    """Register a new user"""
    try:
        user = await auth_service.create_user(
            db=db,
            email=user_data.email,
            password=user_data.password,
            name=user_data.name,
            affiliation=user_data.affiliation,
            research_interests=user_data.research_interests or []
        )

        # Create token pair
        tokens = auth_service.create_token_pair(user)

        return LoginResponse(
            user=UserResponse.from_orm(user),
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type=tokens["token_type"],
            expires_in=tokens["expires_in"]
        )

    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.message
        )


@router.post("/login", response_model=LoginResponse)
async def login(
        login_data: LoginRequest,
        db: AsyncSession = Depends(get_db)
) -> Any:
    """Authenticate user and return tokens"""
    try:
        user = await auth_service.authenticate_user(
            db=db,
            email=login_data.email,
            password=login_data.password
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )

        # Create token pair
        tokens = auth_service.create_token_pair(user)

        return LoginResponse(
            user=UserResponse.from_orm(user),
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type=tokens["token_type"],
            expires_in=tokens["expires_in"]
        )

    except AuthenticationException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message
        )


@router.post("/refresh")
async def refresh_token(
        refresh_data: RefreshTokenRequest,
        db: AsyncSession = Depends(get_db)
) -> Any:
    """Refresh access token"""
    try:
        tokens = await auth_service.refresh_access_token(
            db=db,
            refresh_token=refresh_data.refresh_token
        )
        return tokens

    except AuthenticationException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
        current_user: User = Depends(get_current_user)
) -> Any:
    """Get current user information"""
    return UserResponse.from_orm(current_user)


@router.post("/change-password")
async def change_password(
        password_data: ChangePasswordRequest,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
) -> Any:
    """Change user password"""
    try:
        await auth_service.change_password(
            db=db,
            user=current_user,
            current_password=password_data.current_password,
            new_password=password_data.new_password
        )

        return {"message": "Password changed successfully"}

    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.message
        )


@router.post("/password-reset")
async def request_password_reset(
        reset_data: ResetPasswordRequest,
        db: AsyncSession = Depends(get_db)
) -> Any:
    """Request password reset"""
    await auth_service.reset_password_request(db=db, email=reset_data.email)
    return {"message": "If the email exists, a reset link has been sent"}


@router.post("/password-reset/confirm")
async def confirm_password_reset(
        reset_confirm_data: ResetPasswordConfirmRequest,
        db: AsyncSession = Depends(get_db)
) -> Any:
    """Confirm password reset"""
    try:
        await auth_service.reset_password(
            db=db,
            token=reset_confirm_data.token,
            new_password=reset_confirm_data.new_password
        )

        return {"message": "Password reset successfully"}

    except (AuthenticationException, ValidationException) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )


@router.post("/logout")
async def logout(
        current_user: User = Depends(get_current_user)
) -> Any:
    """Logout user (client should discard tokens)"""
    # In a more sophisticated setup, you might want to blacklist tokens
    # For now, we just return success as logout is handled client-side
    return {"message": "Logged out successfully"}


@router.post("/verify-email")
async def verify_email(
        token: str,
        db: AsyncSession = Depends(get_db)
) -> Any:
    """Verify user email"""
    try:
        await auth_service.verify_email(db=db, token=token)
        return {"message": "Email verified successfully"}

    except AuthenticationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )


@router.delete("/account")
async def deactivate_account(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
) -> Any:
    """Deactivate user account"""
    await auth_service.deactivate_user(db=db, user=current_user)
    return {"message": "Account deactivated successfully"}