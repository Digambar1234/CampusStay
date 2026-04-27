from fastapi import HTTPException, UploadFile, status

from app.core.config import get_settings

ALLOWED_IMAGE_TYPES = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
}
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_UPLOAD_BYTES = 5 * 1024 * 1024


def _configure_cloudinary() -> None:
    settings = get_settings()
    if not settings.cloudinary_cloud_name or not settings.cloudinary_api_key or not settings.cloudinary_api_secret:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Cloudinary is not configured.",
        )

    import cloudinary

    cloudinary.config(
        cloud_name=settings.cloudinary_cloud_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True,
    )


async def upload_pg_photo(file: UploadFile, pg_id: str) -> dict[str, str]:
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only jpg, jpeg, png, and webp images are allowed.")
    filename = (file.filename or "").lower()
    if not any(filename.endswith(ext) for ext in ALLOWED_EXTENSIONS):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Image extension must be jpg, jpeg, png, or webp.")

    contents = await file.read()
    if len(contents) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Image must be 5MB or smaller.")

    _configure_cloudinary()
    import cloudinary.uploader

    result = cloudinary.uploader.upload(
        contents,
        folder=f"campusstay/pgs/{pg_id}",
        resource_type="image",
        overwrite=False,
    )
    return {
        "secure_url": result["secure_url"],
        "public_id": result["public_id"],
        "resource_type": result.get("resource_type", "image"),
    }


def delete_cloudinary_asset(public_id: str | None) -> None:
    if not public_id:
        return
    _configure_cloudinary()
    import cloudinary.uploader

    try:
        cloudinary.uploader.destroy(public_id, resource_type="image")
    except Exception:
        pass
