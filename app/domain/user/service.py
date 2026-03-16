from typing import Any  
from fastapi import HTTPException, status 
from app.domain.user.schemas import UserCreate


users_store: list[dict[str,Any]] = []


def create_user(user_in: UserCreate) -> dict[str,Any]:
    for existing_user in users_store: 
        if existing_user['email'] == user_in.email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="이미 가입된 이메일입니다."
            )
    new_user = {
        "id": len(users_store)+1,
        "username": user_in.username,
        "email": user_in.email,
    }

    users_store.append(new_user)

    return new_user

def list_users() -> list[dict[str,Any]]:
    return users_store


