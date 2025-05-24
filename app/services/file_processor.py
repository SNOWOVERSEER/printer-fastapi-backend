from fastapi import UploadFile, HTTPException
import os
import uuid
from typing import Tuple, Dict, Any
import aiofiles
import magic

class FileProcessor:
    
    async def process_file(self, file: UploadFile) -> Dict[str, Any]:
        
        content = await file.read(1024)  
        file_type = magic.from_buffer(content, mime=True)
        await file.seek(0) 
        
        allowed_types = ['application/pdf', 
                        'application/msword', 
                        'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
        
        if file_type not in allowed_types:
            raise HTTPException(status_code=400, detail="Not supported file type, only PDF and Word documents are supported for now")
        
        pages = await self._count_pages(file, file_type)
        
        return {
            "filename": None, 
            "original_name": file.filename,
            "pages": pages,
            "content_type": file_type
        }
    
    async def _count_pages(self, file: UploadFile, file_type: str) -> int:
       
        if file_type == 'application/pdf':
            return 5  # Dummy PDF
        elif file_type in ['application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
            return 3  # Dummy Word
        return 1
    
    async def save_file(self, file: UploadFile, upload_folder: str) -> str:
        os.makedirs(upload_folder, exist_ok=True)
        
        file_extension = os.path.splitext(file.filename)[1] if file.filename else ""
        file_id = uuid.uuid4()
        file_path = os.path.join(upload_folder, f"{file_id}{file_extension}")
        
        await file.seek(0)
        async with aiofiles.open(file_path, 'wb') as out_file:
            while content := await file.read(1024 * 1024):  
                await out_file.write(content)
        
        return file_id, file_path

file_processor = FileProcessor()

def get_file_processor():
    return file_processor