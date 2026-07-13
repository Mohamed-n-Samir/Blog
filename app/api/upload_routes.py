from fastapi import APIRouter, Depends, File, UploadFile, Query, HTTPException, status
from app.utils.image_uploader import save_uploaded_image

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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid folder name. Must be 'profile_pics' or 'blog_images'."
        )

    filename = await save_uploaded_image(file, folder)
    return {
        "filename": filename,
        "url": f"/media/{folder}/{filename}"
    }
