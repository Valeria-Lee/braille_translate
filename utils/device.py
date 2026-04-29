import asyncio
import logging
from fastapi import WebSocket

logger = logging.getLogger(__name__)

_DOT_MAP = {
    "⠁": [1], "⠃": [1,2], "⠉": [1,4], "⠙": [1,4,5],
    "⠑": [1,5], "⠋": [1,2,4], "⠛": [1,2,4,5], "⠓": [1,2,5],
    "⠊": [2,4], "⠚": [2,4,5], "⠅": [1,3], "⠇": [1,2,3],
    "⠍": [1,3,4], "⠝": [1,3,4,5], "⠕": [1,3,5], "⠏": [1,2,3,4],
    "⠟": [1,2,3,4,5], "⠗": [1,2,3,5], "⠎": [2,3,4], "⠞": [2,3,4,5],
    "⠥": [1,3,6], "⠧": [1,2,3,6], "⠺": [2,4,5,6], "⠭": [1,3,4,6],
    "⠽": [1,3,4,5,6], "⠵": [1,3,5,6], "⠷": [1,2,3,5,6], "⠮": [2,3,4,6],
    "⠌": [3,4], "⠬": [2,4,6], "⠾": [1,2,3,5,6], "⠳": [1,2,5,6],
    "⠂": [2], "⠆": [2,3], "⠒": [2,5], "⠲": [2,5,6],
    "⠦": [2,3,6], "⠖": [2,3,5], "⠄": [3], "⠶": [2,3,5,6],
    "⠤": [3,6], "⠐": [5,6], "⠢": [2,6], "⠣": [1,2,6],
    "⠜": [3,4,5], "⠼": [3,4,5,6], "⠠": [6],
}


def _flatten_to_dots(braille_data: list) -> list:
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
        self._ws = None
        self._cells = 0
        self._done_event = asyncio.Event()
        self._lock = asyncio.Lock()

    @property
    def is_connected(self) -> bool:
        return self._ws is not None

    @property
    def cells(self) -> int:
        return self._cells

    async def on_connect(self, websocket: WebSocket, cells: int):
        self._ws = websocket
        self._cells = cells
        self._done_event.clear()
        logger.info(f"ESP8266 conectado — {cells} celda(s)")

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

    async def send_paragraph(self, braille_data: list) -> bool:
        if not self.is_connected:
            return False
        chars_as_dots = _flatten_to_dots(braille_data)
        if not chars_as_dots:
            return True
        cells = self._cells if self._cells > 0 else 1
        lines = [chars_as_dots[i:i+cells] for i in range(0, len(chars_as_dots), cells)]
        all_ok = True
        async with self._lock:
            for idx, line in enumerate(lines):
                ok = await self._send_line(line, idx)
                if not ok:
                    all_ok = False
                    break
        return all_ok

    async def emergency_off(self) -> bool:
        if not self.is_connected:
            return False
        try:
            await self._ws.send_json({"type": "off"})
            return True
        except Exception as e:
            logger.error(f"Error off: {e}")
            return False

    async def _send_line(self, line: list, idx: int) -> bool:
        self._done_event.clear()
        try:
            await self._ws.send_json({"type": "render", "chars": line})
        except Exception as e:
            logger.error(f"Error línea {idx}: {e}")
            return False
        timeout = len(line) * 6 * 0.07 + len(line) * 0.8 + 5
        try:
            await asyncio.wait_for(self._done_event.wait(), timeout=timeout)
            return True
        except asyncio.TimeoutError:
            logger.error(f"Timeout línea {idx}")
            return False


braille_device = BrailleDevice()
