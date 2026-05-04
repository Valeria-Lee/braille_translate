import asyncio
import logging
from fastapi import WebSocket
from utils.braille_translation import send_braille_characters

logger = logging.getLogger(__name__)

class BrailleDevice:
    def __init__(self):
        self._ws: WebSocket | None = None
        self._cells: int = 0
        self._done_event = asyncio.Event()
        self._lock = asyncio.Lock()
        self._pausa_chars: int = 200
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
        logger.info(f"ESP8266 conectado: {cells} celda(s)")

        await websocket.send_json({
            "type": "config",
            "pausa_chars": self._pausa_chars 
        })

        if self._lines:
            await asyncio.sleep(1.0)
            await self._send_current_line()

    async def on_disconnect(self):
        self._ws = None
        self._cells = 0
        self._lines = []
        self._current_line = 0 
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
        chars_as_dots = send_braille_characters(braille_data)
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

        timeout = len(line) * (0.050 + 0.020 + self._pausa_chars/1000) * 6 + 15
        try:
            await asyncio.wait_for(self._done_event.wait(), timeout=timeout)
            return True
        except asyncio.TimeoutError:
            logger.error(f"Timeout línea {idx}")
            return False


braille_device = BrailleDevice()