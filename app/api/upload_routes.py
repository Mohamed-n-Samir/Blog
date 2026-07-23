from fastapi import APIRouter, Depends, File, UploadFile, Query, status
from app.utils.image_operations import save_uploaded_image
from app.utils.exceptions import APPException

upload_router = APIRouter()

@upload_router.post("/api/upload", status_code=status.HTTP_201_CREATED)
async def upload_image(
    file: UploadFile = File(...),
    folder: str = Query(..., description="Target media folder ('profile_pics' or 'blog_images')")
):
    """
    Asynchronously uploads an image file to the specified media subdirectory.
    """
    if folder not in {"profile_pics", "blog_images"}:
        raise APPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Invalid folder name. Must be 'profile_pics' or 'blog_images'."
        )

    filename = await save_uploaded_image(file, folder)
    return {
        "filename": filename,
        "url": f"/media/{folder}/{filename}"
    }
