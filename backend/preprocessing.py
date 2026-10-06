from __future__ import annotations

from io import BytesIO
from pathlib import Path

from PIL import Image, UnidentifiedImageError

from config import ALLOWED_EXTENSIONS, MAX_FILE_SIZE_BYTES


def validate_image_bytes(data: bytes, filename: str) -> Image.Image:
    if not filename:
        raise ValueError("Invalid image file name.")

    suffix = Path(filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise ValueError("Invalid image format. Please upload a valid image.")

    if len(data) > MAX_FILE_SIZE_BYTES:
        raise ValueError("Image file is too large. Maximum size is 10 MB.")

    try:
        image = Image.open(BytesIO(data))
        image.load()
    except (UnidentifiedImageError, OSError, ValueError):
        raise ValueError("Unable to read image. Please upload another image.")

    return image.convert("RGB")
