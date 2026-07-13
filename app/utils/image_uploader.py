import os
import uuid
from fastapi import UploadFile, HTTPException, status
from app.constants.constant import ROOT_DIR

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "avif"}

async def save_uploaded_image(upload_file: UploadFile, folder: str) -> str:
    """
    Validates and saves an uploaded image file to the media/{folder} directory.
    GIF images are explicitly disallowed.
    Returns the generated unique filename.
    """
    if not upload_file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No filename provided in upload."
        )

    # Validate file extension
    ext = os.path.splitext(upload_file.filename)[1].lower().lstrip(".")
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File extension .{ext} is not allowed. Allowed types: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )
    
    # Validate content type
    content_type = upload_file.content_type or ""
    if not content_type.startswith("image/") or "gif" in content_type.lower():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is not a supported image type. GIFs are not allowed."
        )

    # Ensure the target directory exists
    target_dir = ROOT_DIR / "media" / folder
    target_dir.mkdir(parents=True, exist_ok=True)

    # Generate unique filename to avoid duplicates/collisions
    unique_filename = f"{uuid.uuid4().hex}.{ext}"
    file_path = target_dir / unique_filename

    # Save the file to disk
    try:
        content = await upload_file.read()
        with open(file_path, "wb") as f:
            f.write(content)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to write image file: {str(e)}"
        )
    finally:
        await upload_file.close()

    return unique_filename
