import asyncio
import logging
from fastapi import WebSocket

logger = logging.getLogger(__name__)

_DOT_MAP = {
    "\u2801": [1], "\u2803": [1,2], "\u2809": [1,4], "\u2819": [1,4,5],
    "\u2811": [1,5], "\u280b": [1,2,4], "\u281b": [1,2,4,5], "\u2813": [1,2,5],
    "\u280a": [2,4], "\u281a": [2,4,5], "\u2805": [1,3], "\u2807": [1,2,3],
    "\u280d": [1,3,4], "\u281d": [1,3,4,5], "\u2815": [1,3,5], "\u280f": [1,2,3,4],
    "\u281f": [1,2,3,4,5], "\u2817": [1,2,3,5], "\u280e": [2,3,4], "\u281e": [2,3,4,5],
    "\u2825": [1,3,6], "\u2827": [1,2,3,6], "\u283a": [2,4,5,6], "\u282d": [1,3,4,6],
    "\u283d": [1,3,4,5,6], "\u2835": [1,3,5,6], "\u2837": [1,2,3,5,6], "\u282e": [2,3,4,6],
    "\u280c": [3,4], "\u282c": [2,4,6], "\u283e": [1,2,3,5,6], "\u2833": [1,2,5,6],
    "\u2802": [2], "\u2806": [2,3], "\u2812": [2,5], "\u2832": [2,5,6],
    "\u2826": [2,3,6], "\u2816": [2,3,5], "\u2804": [3], "\u2836": [2,3,5,6],
    "\u2824": [3,6], "\u2810": [5,6], "\u2822": [2,6], "\u2823": [1,2,6],
    "\u281c": [3,4,5], "\u283c": [3,4,5,6], "\u2820": [6],
}


def _flatten_to_dots(braille_data: list) -> list:
    """Aplana estructura braille a lista de listas de puntos."""
    result = []
    for sentence in braille_data:
        for word_idx, word in enumerate(sentence):
            for char in word:
                dots = _DOT_MAP.get(char)
                if dots is not None:
                    result.append(dots)
            if word_idx < len(sentence) - 1:
                result.append([])
    return result


class BrailleDevice:
    def __init__(self):
        self._ws: WebSocket | None = None
        self._cells: int = 0
        self._done_event = asyncio.Event()
        self._lock = asyncio.Lock()

        self._lines: list[list] = []
        self._current_line: int = 0

    @property
    def is_connected(self) -> bool:
        return self._ws is not None

    @property
    def cells(self) -> int:
        return self._cells

    @property
    def current_line(self) -> int:
        return self._current_line

    @property
    def total_lines(self) -> int:
        return len(self._lines)

    async def on_connect(self, websocket: WebSocket, cells: int):
        self._ws = websocket
        self._cells = cells
        self._done_event.clear()
        logger.info(f"ESP8266 conectado — {cells} celda(s)")

        if self._lines:
            await asyncio.sleep(1.0)
            await self._send_current_line()

    async def on_disconnect(self):
        self._ws = None
        self._cells = 0
        self._done_event.set()
        logger.warning("ESP8266 desconectado")

    async def on_message(self, msg: dict):
        t = msg.get("type")

        if t == "done":
            self._done_event.set()

        elif t == "error":
            logger.error(f"ESP error: {msg.get('msg')}")
            self._done_event.set()

        elif t == "hello":
            self._cells = msg.get("cells", self._cells)

        elif t == "next":
            await self.next_line()

        elif t == "prev":
            await self.prev_line()

    async def load_text(self, braille_data: list) -> bool:
        chars_as_dots = _flatten_to_dots(braille_data)
        if not chars_as_dots:
            return False

        cells = self._cells if self._cells > 0 else 1
        self._lines = [
            chars_as_dots[i:i + cells]
            for i in range(0, len(chars_as_dots), cells)
        ]
        self._current_line = 0

        logger.info(f"Texto cargado: {len(chars_as_dots)} chars, "
                    f"{len(self._lines)} líneas de {cells} celda(s)")

        if self.is_connected:
            return await self._send_current_line()
        return True

    async def next_line(self) -> bool:
        if not self._lines:
            return False
        if self._current_line < len(self._lines) - 1:
            self._current_line += 1
            logger.info(f"Línea → {self._current_line}/{len(self._lines)-1}")
            return await self._send_current_line()
        else:
            logger.info("Ya estás en la última línea")
            return False

    async def prev_line(self) -> bool:
        if not self._lines:
            return False
        if self._current_line > 0:
            self._current_line -= 1
            logger.info(f"Línea ← {self._current_line}/{len(self._lines)-1}")
            return await self._send_current_line()
        else:
            logger.info("Ya estás en la primera línea")
            return False

    async def emergency_off(self) -> bool:
        if not self.is_connected:
            return False
        try:
            await self._ws.send_json({"type": "off"})
            return True
        except Exception as e:
            logger.error(f"Error off: {e}")
            return False

    async def _send_current_line(self) -> bool:
        if not self._lines or not self.is_connected:
            return False
        line = self._lines[self._current_line]
        return await self._send_line(line, self._current_line)

    async def _send_line(self, line: list, idx: int) -> bool:
        self._done_event.clear()
        try:
            await self._ws.send_json({
                "type":         "render",
                "chars":        line,
                "line_index":   idx,
                "total_lines":  len(self._lines),
            })
        except Exception as e:
            logger.error(f"Error enviando línea {idx}: {e}")
            return False

        timeout = len(line) * 6 * 0.07 + len(line) * 0.8 + 5
        try:
            await asyncio.wait_for(self._done_event.wait(), timeout=timeout)
            return True
        except asyncio.TimeoutError:
            logger.error(f"Timeout línea {idx}")
            return False


braille_device = BrailleDevice()