from typing import Annotated 

import jwt 
from fastapi import APIRouter, Depends, HTTPException, status 
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session 

from app.api.deps import get_db 
from app.core.security import create_access_token,decode_token
from app.domain.user.schemas import TokenResponse, UserCreate,UserResponse
from app.domain.user.service import authenticate_user, create_user, get_user_by_email

router = APIRouter(prefix='/auth', tags=['auth'])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/v1/auth/login')

DbSession = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[str, Depends(oauth2_scheme)]

def get_current_user(db:DbSession, token: TokenDep):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail= "유효하지 않은 인증 정보입니다",
        headers={"WWW-AUTHENTICATE": 'Bearer'},
    )

    try:
        payload = decode_token(token)
        subject = payload.get("sub")

        if subject is None:
            raise credentials_exception
    except jwt.InvalidTokenError:
        raise credentials_exception
    
    user = get_user_by_email(db,subject)

    if user is None:
        raise credentials_exception
    
    return user 
CurrentUser = Annotated[UserResponse, Depends(get_current_user)]

@router.post("/signup",
             response_model=UserResponse,
             status_code=status.HTTP_201_CREATED)
def signup(user_in: UserCreate, db:DbSession):
    return create_user(db,user_in)

@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(form_data: Annotated[OAuth2PasswordRequestForm,Depends()],db:Session):
    user = authenticate_user(
        db,
        form_data.username,
        form_data.password,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 올바르지 않습니다",
            headers={"WWW-Authenticate": 'Bearer'}
        )
    access_token = create_access_token(user.email)

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
@router.get("/me", response_model=UserResponse)
def read_me(current_user: CurrentUser):
    return current_user

