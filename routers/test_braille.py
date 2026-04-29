from fastapi import APIRouter, Query, HTTPException
from utils.braille_translation import braille_translate, convert_braille_characters_to_dots
 
router = APIRouter(prefix="/test", tags=["test"])

@router.get("/braille")
def test_braille(
    text: str = Query(..., description="Texto a traducir"),
    char_qty: int = Query(..., ge=1, description="Cantidad de caracteres por línea (celdas del dispositivo)"),
):
    if not text.strip():
        raise HTTPException(status_code=400, detail="El texto no puede estar vacío")
 
    # 1. Traducir texto → estructura Braille
    braille_data = braille_translate(text)
 
    # 2. Aplanar a lista de símbolos individuales
    flat_chars = _flatten(braille_data)
 
    # 3. Convertir cada símbolo a puntos
    chars_with_dots = []
    for symbol in flat_chars:
        dots = convert_braille_characters_to_dots(symbol)
        if dots is not None:                        # ignorar chars sin mapeo
            chars_with_dots.append({
                "symbol": symbol,
                "dots":   dots,
            })
 
    # 4. Paginar en líneas de char_qty
    lines = []
    for i in range(0, len(chars_with_dots), char_qty):
        chunk = chars_with_dots[i : i + char_qty]
        lines.append({
            "line_index": i // char_qty,
            "chars":      chunk,
        })
 
    return {
        "text":        text,
        "char_qty":    char_qty,
        "total_chars": len(chars_with_dots),
        "total_lines": len(lines),
        "lines":       lines,
    }
 
 
def _flatten(braille_data: list) -> list[str]:
    """Aplana [ oración [ palabra [ símbolo, ... ] ] ] a lista plana de símbolos."""
    result = []
    for sentence in braille_data:
        for word in sentence:
            result.extend(word)
    return result