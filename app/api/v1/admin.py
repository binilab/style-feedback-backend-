from typing import Annotated 
from fastapi import APIRouter, Depends 
from sqlalchemy.orm import Session 

from app.api.deps import get_db 
from app.api.v1.auth import get_current_admin_user 
from app.domain.user.models import User  
from app.domain.user.schemas import UserResponse 
from app.domain.user.service import list_users  

router = APIRouter(prefix='/admin', tags=['admin'])

DbSession = Annotated[Session, Depends(get_db)]
AdminUser = Annotated[User, Depends(get_current_admin_user)]

@router.get("/users", response_model=list[UserResponse])
def read_all_user(db: DbSession, admin_user: AdminUser):
    return list_users(db)

    