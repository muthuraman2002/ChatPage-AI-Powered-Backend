from sqlalchemy.orm import Session
from models.usermodel import User
from models.schemas import UserCreate

def create_user(db: Session, user_data: UserCreate):
    print(user_data)
    db_user = User( name=user_data.name,
        email=user_data.email,
        phone=user_data.phone,
        password=user_data.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_users(db: Session):
    return db.query(User).all()
