from sqlalchemy import select 
from sqlalchemy.orm import Session 
from fastapi import HTTPException, status 


from app.domain.user.models import User 
from app.domain.user.schemas import UserCreate 


def fake_hash_password(password:str)-> str:
    return f"hashed::{password}"


def create_user(db:Session, user_in: UserCreate) -> User: 
    existing_user = db.scalar(
        select(User).where(User.email == user_in.email)
    )

    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 가입된 이메일입니다."
        )
    
    new_user = User(
        username= user_in.username,
        email = user_in.email,
        password_hash = fake_hash_password(user_in.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user 

def list_users(db:Session) -> list[User]:
    users= db.scalars(
        select(User).order_by(User.id.desc())
    ).all()

    return users 

