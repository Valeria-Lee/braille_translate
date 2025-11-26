from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from models import File as FileModel
from schemas import FileResponse
from database import get_session

router = APIRouter(prefix="/files", tags=["Files"])

@router.post("/{user_id}", response_model=FileResponse)
async def upload_file(
    user_id: int, 
    uploaded: UploadFile = File(...),
    db: AsyncSession = Depends(get_session)
):
    content = await uploaded.read()

    new_file = FileModel(
        title=uploaded.filename,
        file=content,
        user_id=user_id
    )

    db.add(new_file)
    await db.commit()
    await db.refresh(new_file)
    return new_file

@router.get("/{file_id}", response_model=FileResponse)
async def get_file(file_id: int, db: AsyncSession = Depends(get_session)):
    return await db.get(FileModel, file_id)
