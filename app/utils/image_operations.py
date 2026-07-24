import os
import uuid

from io import BytesIO
from pathlib import Path

from PIL import Image, ImageOps

from fastapi import UploadFile, status

from app.constants.constant import ROOT_DIR
from app.utils.exceptions import APPException, ServerException


ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "avif"}
IMAGE_MODES = {"RGBA", "LA", "P"}

MEDIA_DIR = ROOT_DIR / "media"

async def save_uploaded_image(upload_file: UploadFile, folder: str) -> str:
    """
    Validates and saves an uploaded image file to the media/{folder} directory.
    GIF images are explicitly disallowed.
    Returns the generated unique filename.
    """
    if not upload_file.filename:
        raise APPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="No filename provided in upload."
        )

    # Validate file extension
    ext = os.path.splitext(upload_file.filename)[1].lower().lstrip(".")
    if ext not in ALLOWED_EXTENSIONS:
        raise APPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=f"File extension .{ext} is not allowed. Allowed types: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )
    
    # Validate content type
    content_type = upload_file.content_type or ""
    if not content_type.startswith("image/") or "gif" in content_type.lower():
        raise APPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Uploaded file is not a supported image type. GIFs are not allowed."
        )

    try:
        content = await upload_file.read()
        image = process_profile_image(content)
        saved_filename = save_profile_image(img=image, folder=folder)

    except Exception as e:
        raise ServerException(
            message=f"Failed to write image file: {str(e)}"
        )
    finally:
        await upload_file.close()

    return saved_filename


def process_profile_image(content: bytes) -> Image:
    with Image.open(BytesIO(content)) as original:
        img = ImageOps.exif_transpose(original)
        img = ImageOps.fit(img, (300,300), method=Image.Resampling.LANCZOS)

        if img.mode in IMAGE_MODES:
            img = img.convert("RGB")

        return img
    
def save_profile_image(img, folder) -> str:
    target_dir = MEDIA_DIR / folder
    target_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{uuid.uuid4().hex}.jpg"
    file_path = target_dir / filename

    img.save(file_path, "JPEG", quality=85, optimize=True)

    return filename

def delete_profile_image(image_path: str | None) -> None:
    if image_path is None:
        return

    full_path = MEDIA_DIR / image_path

    if full_path.exists():
        full_path.unlink()
        
        
