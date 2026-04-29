"""
utils/device.py
─────────────────────────────────────────────────────────────────
Interfaz serial entre FastAPI y el ESP8266 (BrailLearn).

Configuración (.env):
DEVICE_PORT=/dev/ttyUSB0      # Linux
DEVICE_PORT=COM3              # Windows
DEVICE_BAUD=115200

Mapeo físico de la celda conectada (pines 24-31 → chip índice 3):
    Punto Braille 1 → solenoid 24
    Punto Braille 2 → solenoid 25
    Punto Braille 3 → solenoid 26
    Punto Braille 4 → solenoid 27
    Punto Braille 5 → solenoid 28
    Punto Braille 6 → solenoid 29

    Si cambias la celda activa, ajusta CELL_BASE_POINT.
"""

import os
import time
import threading
import logging
import serial
import serial.tools.list_ports

logger = logging.getLogger(__name__)

DEVICE_PORT  = os.getenv("DEVICE_PORT", "")   # e.g. /dev/ttyUSB0 o COM3
DEVICE_BAUD  = int(os.getenv("DEVICE_BAUD", "115200"))
DEVICE_TIMEOUT = 5  # segundos de espera para respuesta del ESP

# Punto de inicio del solenoide 0 de la celda activa.
# La celda está en pines 24-31 → chip index 3 → punto base = 24
CELL_BASE_POINT = int(os.getenv("CELL_BASE_POINT", "24"))


# ──────────────────────────────────────────────
# Singleton de conexión serial (thread-safe)
# ──────────────────────────────────────────────
class BrailleDevice:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._serial = None
                cls._instance._serial_lock = threading.Lock()
            return cls._instance

    # ── Conexión ──────────────────────────────
    def connect(self, port: str = None, baud: int = None) -> bool:
        port = port or DEVICE_PORT
        baud = baud or DEVICE_BAUD

        if not port:
            port = self._auto_detect_port()

        if not port:
            logger.error("No se encontró el puerto del ESP8266. "
                         "Define DEVICE_PORT en el .env")
            return False

        try:
            with self._serial_lock:
                if self._serial and self._serial.is_open:
                    self._serial.close()

                self._serial = serial.Serial(
                    port=port,
                    baudrate=baud,
                    timeout=DEVICE_TIMEOUT
                )

            # Esperar el "READY" del ESP después de su setup()
            ready = self._wait_for_ready()
            if ready:
                logger.info(f"ESP8266 listo en {port} @ {baud} baud")
            else:
                logger.warning("No se recibió READY del ESP, "
                               "pero la conexión está abierta")
            return True

        except serial.SerialException as e:
            logger.error(f"Error al abrir {port}: {e}")
            return False

    def disconnect(self):
        with self._serial_lock:
            if self._serial and self._serial.is_open:
                self._serial.close()
                logger.info("Conexión serial cerrada")

    def is_connected(self) -> bool:
        return self._serial is not None and self._serial.is_open

    # ── Envío de caracteres Braille ───────────
    def send_braille_dots(self, dot_positions: list[int]) -> bool:
        """
        Envía los puntos activos de UN carácter Braille al ESP.

        dot_positions: lista de enteros 1-6 (números de punto Braille estándar)
                       Ej: [1, 2, 4] para 'f'

        El ESP activa cada solenoide de forma secuencial (nunca dos a la vez).
        Retorna True si el ESP respondió OK.
        """
        if not dot_positions:
            return True  # nada que enviar

        if not self.is_connected():
            logger.warning("Dispositivo no conectado. Intentando reconectar...")
            if not self.connect():
                logger.error("No se pudo reconectar al dispositivo")
                return False

        # Convertir puntos braille (1-6) a números de solenoide absolutos
        solenoid_nums = self._dots_to_solenoids(dot_positions)
        if not solenoid_nums:
            logger.warning(f"Puntos inválidos: {dot_positions}")
            return False

        # Construir comando: "DOTS:24,26,27\n"
        payload = ",".join(str(s) for s in solenoid_nums)
        cmd = f"DOTS:{payload}\n"

        return self._send_command(cmd)

    def all_off(self) -> bool:
        """Apaga todos los solenoides de emergencia."""
        return self._send_command("OFF\n")

    # ── Utilidades internas ───────────────────
    def _dots_to_solenoids(self, dots: list[int]) -> list[int]:
        """
        Convierte números de punto Braille (1-6) a números de solenoide.

        Layout físico (pines 24-31, chip 3):
            Dot 1 → solenoid CELL_BASE_POINT + 0
            Dot 2 → solenoid CELL_BASE_POINT + 1
            Dot 3 → solenoid CELL_BASE_POINT + 2
            Dot 4 → solenoid CELL_BASE_POINT + 3
            Dot 5 → solenoid CELL_BASE_POINT + 4
            Dot 6 → solenoid CELL_BASE_POINT + 5
        """
        solenoids = []
        for dot in dots:
            if 1 <= dot <= 6:
                solenoids.append(CELL_BASE_POINT + (dot - 1))
            else:
                logger.warning(f"Número de punto inválido: {dot} (debe ser 1-6)")
        return solenoids

    def _send_command(self, cmd: str) -> bool:
        try:
            with self._serial_lock:
                self._serial.reset_input_buffer()
                self._serial.write(cmd.encode("ascii"))
                self._serial.flush()

                # Esperar respuesta "OK\n" o "ERR:...\n"
                response = self._serial.readline().decode("ascii").strip()

            if response == "OK":
                return True
            else:
                logger.error(f"Respuesta inesperada del ESP: '{response}'")
                return False

        except serial.SerialException as e:
            logger.error(f"Error de comunicación serial: {e}")
            self._serial = None  # marcar como desconectado
            return False

    def _wait_for_ready(self, timeout: float = 3.0) -> bool:
        """Lee líneas hasta recibir 'READY' o agotar el timeout."""
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                line = self._serial.readline().decode("ascii").strip()
                if line == "READY":
                    return True
            except Exception:
                break
        return False

    def _auto_detect_port(self) -> str:
        """Intenta detectar el ESP8266 por descripción del puerto."""
        for port_info in serial.tools.list_ports.comports():
            desc = (port_info.description or "").lower()
            if any(kw in desc for kw in ["cp210", "ch340", "esp", "uart", "usb serial"]):
                logger.info(f"Puerto auto-detectado: {port_info.device} ({port_info.description})")
                return port_info.device
        return ""


# Instancia global (singleton)
braille_device = BrailleDevice()