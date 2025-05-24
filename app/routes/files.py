from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import os
from datetime import datetime
from app.services.file_processor import get_file_processor, FileProcessor
from app.core.config import settings
from app.core.security import get_current_user, get_current_user_optional
from app.models.user import User
from typing import Optional
router = APIRouter()

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user: Optional[User] = Depends(get_current_user_optional),
    file_processor: FileProcessor = Depends(get_file_processor)
):
    if current_user:
        print(f"Uploading file for user: {current_user.username}")
    else:
        print("Uploading file for anonymous user")
    
    try:
        file_info = await file_processor.process_file(file)
        
        file_id, file_path = await file_processor.save_file(file, settings.UPLOAD_FOLDER)
        return {
            "fileId": file_id,
            "filename": file_path,
            "originalName": file_info["original_name"],
            "contentType": file_info["content_type"],
            "pages": file_info["pages"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")

@router.get("/{filename}")
async def get_file(filename: str):
    file_path = os.path.join(settings.UPLOAD_FOLDER, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type='application/octet-stream'
    )