from sqlalchemy.orm import Session
from app import models, schemas
from passlib.context import CryptContext
from app.utils.retry import retry

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@retry(times=3, delay=1, exceptions=(Exception,))
def get_user(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

@retry(times=3, delay=1, exceptions=(Exception,))
def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@retry(times=3, delay=1, exceptions=(Exception,))
def create_image(db: Session, image: schemas.ImageCreate, file_path: str, resolution: str, size: float):
    db_image = models.Image(
        name=image.name,
        file_path=file_path,
        resolution=resolution,
        size=size,
        tags=image.tags
    )
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image

@retry(times=3, delay=1, exceptions=(Exception,))
def get_images(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Image).offset(skip).limit(limit).all()

@retry(times=3, delay=1, exceptions=(Exception,))
def get_image(db: Session, image_id: int):
    return db.query(models.Image).filter(models.Image.id == image_id).first()

@retry(times=3, delay=1, exceptions=(Exception,))
def update_image(db: Session, image_id: int, image: schemas.ImageUpdate):
    db_image = get_image(db, image_id)
    if db_image:
        if image.name is not None:
            db_image.name = image.name
        if image.tags is not None:
            db_image.tags = image.tags
        db.commit()
        db.refresh(db_image)
    return db_image

@retry(times=3, delay=1, exceptions=(Exception,))
def delete_image(db: Session, image_id: int):
    db_image = get_image(db, image_id)
    if db_image:
        db.delete(db_image)
        db.commit()
    return db_image
