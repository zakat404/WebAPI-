from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from app import schemas, crud
from app.dependencies import get_db, get_current_user
import os
from PIL import Image
from app.utils import image_processing
import uuid
from app.config import settings
import aiofiles
import asyncio
import redis
import json
from fastapi.encoders import jsonable_encoder

router = APIRouter()

UPLOAD_DIR = "uploads"

r = redis.Redis.from_url(settings.REDIS_URL)
@router.post("/", response_model=schemas.Image, status_code=status.HTTP_201_CREATED)
async def upload_image(
    name: str,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    tags: str = None,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)

    filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    async with aiofiles.open(file_path, "wb") as buffer:
        content = await file.read()
        await buffer.write(content)

    background_tasks.add_task(process_image, file_path)

    resolution, size = await asyncio.to_thread(get_image_metadata, file_path)

    image_data = schemas.ImageCreate(name=name, tags=tags)
    db_image = crud.create_image(db, image=image_data, file_path=file_path, resolution=resolution, size=size)

    background_tasks.add_task(send_message_to_broker, "image_uploaded", {"image_id": db_image.id})

    return db_image

def get_image_metadata(file_path):
    with Image.open(file_path) as image:
        resolution = f"{image.width}x{image.height}"
    size = os.path.getsize(file_path)
    return resolution, size

def process_image(file_path):
    resolutions = [(100, 100), (500, 500)]
    image_processing.resize_image(file_path, resolutions)
    image_processing.convert_to_grayscale(file_path)

def send_message_to_broker(event_type, data):
    import pika
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='broker'))
    channel = connection.channel()
    channel.queue_declare(queue='image_queue')
    message = {'event': event_type, 'data': data}
    channel.basic_publish(exchange='', routing_key='image_queue', body=json.dumps(message))
    connection.close()

@router.get("/", response_model=list[schemas.Image])
def read_images(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    cache_key = f"images:{skip}:{limit}"
    cached_data = r.get(cache_key)
    if cached_data:
        return json.loads(cached_data)

    images = crud.get_images(db, skip=skip, limit=limit)
    result = [schemas.Image.from_orm(image) for image in images]
    data = jsonable_encoder(result)
    r.set(cache_key, json.dumps(data), ex=60)  # Кэш на 60 секунд
    return result

@router.get("/{image_id}", response_model=schemas.Image)
def read_image(
    image_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    db_image = crud.get_image(db, image_id=image_id)
    if db_image is None:
        raise HTTPException(status_code=404, detail="Image not found")
    return db_image

@router.put("/{image_id}", response_model=schemas.Image)
def update_image(
    image_id: int,
    background_tasks: BackgroundTasks,
    image: schemas.ImageUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    db_image = crud.update_image(db, image_id=image_id, image=image)
    if db_image is None:
        raise HTTPException(status_code=404, detail="Image not found")
    background_tasks.add_task(send_message_to_broker, "image_updated", {"image_id": db_image.id})
    return db_image

@router.delete("/{image_id}", response_model=schemas.Image)
def delete_image(
    image_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    db_image = crud.delete_image(db, image_id=image_id)
    if db_image is None:
        raise HTTPException(status_code=404, detail="Image not found")
    background_tasks.add_task(send_message_to_broker, "image_deleted", {"image_id": image_id})
    return db_image
