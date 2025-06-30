from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from app.config.database import get_db
from app.config.settings import settings
from app.models.user import User
from app.schemas.user_schemas import UserCreate, UserResponse, Token, UserLogin
from app.utils.security import hash_password, verify_password, create_access_token
from app.api.deps import get_current_user

# ✅ ADD: Imports for notifications
from app.models.notification import NotificationType, NotificationChannel  
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/auth", tags=["autenticación"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Registrar nuevo usuario"""
    
    # Check if the email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = hash_password(user_data.password)
    db_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        phone=user_data.phone
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login de usuario - devuelve token JWT"""
    
    # Search for user by email
    user = db.query(User).filter(User.email == form_data.username).first()
    
    # Verify user and password
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, 
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@router.post("/login-json", response_model=Token)
def login_json(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """Alternative login using JSON instead of form-data"""
    
    user = db.query(User).filter(User.email == user_credentials.email).first()
    
    if not user or not verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, 
        expires_delta=access_token_expires
    )
    
    # ✅ ADD: Welcome notification
    try:
        notification_service = NotificationService(db)
        notification_service.create_notification(
            user_id=user.id,
            notification_type=NotificationType.SYSTEM_UPDATE,
            channel=NotificationChannel.in_app,
            title=f"Welcome back to MechLink, {user.first_name}! 🚗",
            message=f"Hi {user.first_name}! Welcome back to MechLink. Keep your vehicle maintenance on track with our easy appointment system.",
            data={
                "login_time": datetime.now().isoformat(),
                "user_name": f"{user.first_name} {user.last_name}",
                "login_type": "success"
            }
        )
        print(f"✅ Welcome notification created for user {user.first_name}")
    except Exception as e:
        # Do not fail login if there is an error in notification
        print(f"❌ Error sending welcome notification: {e}")
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get authenticated user information"""
    return current_user

@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    """Logout (the token should be removed on the frontend)"""
    return {
        "message": "Successfully logged out",
        "user": current_user.email
    }

@router.post("/refresh", response_model=Token)
def refresh_token(current_user: User = Depends(get_current_user)):
    """Renovar token JWT"""
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": current_user.email}, 
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": current_user
    }