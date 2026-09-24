import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from app.models import User
from app.deps import require_admin
from app.config import settings

router = APIRouter(prefix="/api/upload", tags=["Uploads"])

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}

@router.post("")
async def upload_image(
    file: UploadFile = File(...),
    admin: User = Depends(require_admin)
):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed types: JPG, PNG, WEBP, GIF."
        )

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    filename = f"upload_{uuid.uuid4().hex[:12]}{ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, filename)

    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:  # 10MB limit
        raise HTTPException(status_code=400, detail="File size exceeds 10MB limit.")

    with open(file_path, "wb") as f:
        f.write(contents)

    relative_url = f"/static/images/uploads/{filename}"
    return {
        "url": relative_url,
        "filename": filename,
        "size": len(contents)
    }
