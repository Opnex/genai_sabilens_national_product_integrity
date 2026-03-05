"""File upload utility"""
import os
import uuid
from fastapi import UploadFile
from typing import List, Optional

class FileUploadUtil:
    """Utility for handling file uploads (Local/Cloudinary stub)"""
    
    UPLOAD_DIR = "uploads"
    
    @classmethod
    async def save_file(cls, file: UploadFile, sub_dir: str = "") -> str:
        """Save a file to the local directory or cloud storage"""
        os.makedirs(os.path.join(cls.UPLOAD_DIR, sub_dir), exist_ok=True)
        
        file_ext = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(cls.UPLOAD_DIR, sub_dir, unique_filename)
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
            
        # Return a relative URL or full URI
        return f"/{cls.UPLOAD_DIR}/{sub_dir}/{unique_filename}"

    @classmethod
    async def save_multiple(cls, files: List[UploadFile], sub_dir: str = "") -> List[str]:
        """Save multiple files"""
        urls = []
        for file in files:
            url = await cls.save_file(file, sub_dir)
            urls.append(url)
        return urls
