from fastapi import APIRouter
from utils.braille_translation import braille_translate, send_braille_characters

router = APIRouter(prefix="/traducir", tags=["traducir"])

@router.post("/")
async def traducir(text: str):
    braille = braille_translate(text)
    send_braille_characters(braille)
    return {"braille": braille}