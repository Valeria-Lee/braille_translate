# routers/documentos.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/documentos", tags=["documentos"])

class DocumentoCreate(BaseModel):
    titulo: str
    contenido: str
    autor: str

# GET /documentos/
@router.get("/")
async def get_documentos():
    # replace with your db query
    # documents = await db.execute(select(Documento))
    # return documents.scalars().all()
    return {"message": "lista de documentos"}

# GET /documentos/{id}
@router.get("/{documento_id}")
async def get_documento(documento_id: int):
    # documento = await db.get(Documento, documento_id)
    # if not documento:
    #     raise HTTPException(status_code=404, detail="Documento no encontrado")
    # return documento
    return {"message": f"documento {documento_id}"}

# POST /documentos/nuevo
@router.post("/nuevo")
async def nuevo_documento(documento: DocumentoCreate):
    # db.add(Documento(**documento.model_dump()))
    # await db.commit()
    return {"message": "documento creado", "documento": documento}