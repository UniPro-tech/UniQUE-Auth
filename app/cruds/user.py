from ..models import User
from ..schemas import User


def get_user_by_email(db, email):
    user = db.query(User).filter(User.email == email).first()
    return User.model_validate(user) if user else None

def get_user_by_id(db, user_id):
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_id(db, user_id):
    return db.query(User).filter(User.id == user_id).first()


