from sqlalchemy import select 
from sqlalchemy.orm import Session 
from fastapi import HTTPException, status 

from app.core.security import hash_password, verify_password
from app.domain.user.models import User 
from app.domain.user.schemas import UserCreate 




def create_user(db:Session, user_in:UserCreate)-> User:
    existing_user = db.scalar(
        select(User).where(User.email == user_in.eamil)
    )

    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 가입된 이메일입니다."
        )
    
    new_user = User(
        username=user_in.username,
        email= user_in.email,
        password=hash_password(user_in.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user 


def list_users(db:Session)-> list[User]:
    users = db.scalars(
        select(User).order_by(User.id.desc()).all()
    )
    return users 

def get_user_by_email(db:Session, email:str)-> User | None:
    return db.scalar(
        select(User).where(User.email ==email)
    )


def authenticate_user(db:Session, email:str, password:str) -> User | None:
    user = get_user_by_email(db,email)

    if user is None: 
        return None 
    if not verify_password(password,user.password_hash):
        return None 
    return user 