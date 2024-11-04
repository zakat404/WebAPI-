from PIL import Image
import os

def resize_image(image_path: str, sizes: list):
    for size in sizes:
        with Image.open(image_path) as img:
            img.thumbnail(size)
            base, ext = os.path.splitext(image_path)
            new_image_path = f"{base}_{size[0]}x{size[1]}{ext}"
            img.save(new_image_path)

def convert_to_grayscale(image_path: str):
    with Image.open(image_path) as img:
        grayscale = img.convert("L")
        base, ext = os.path.splitext(image_path)
        new_image_path = f"{base}_grayscale{ext}"
        grayscale.save(new_image_path)
