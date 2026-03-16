from typing import Annotated 
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_db 
from app.domain.user.service import create_user, list_users 
from app.domain.user.schemas import UserCreate, UserResponse


router = APIRouter(prefix="/users", tags=['users'])

DbSession = Annotated[Session,Depends(get_db)]


@router.post(""
             ,response_model=UserResponse,
             status_code=status.HTTP_201_CREATED)
def create_user_endpoint(user_in: UserCreate, db :DbSession):
    created_user= create_user(db,user_in)
    return created_user 

@router.get("",
            response_model=list[UserResponse],)
def list_users_endpoint(db:DbSession):
    return list_users(db)