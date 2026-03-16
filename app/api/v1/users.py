from fastapi import APIRouter, status 

from app.domain.user.schemas import UserCreate, UserResponse 
from app.domain.user.service import create_user, list_users 


router = APIRouter(prefix="/users", tags=['users'])


@router.post(
    "",
    response_model = UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user_endpoint(user_in: UserCreate):
    created_user = create_user(user_in)
    return created_user

@router.get(
    "",
    response_model=list[UserResponse],
)
def list_users_endpoint():
    return list_users()

