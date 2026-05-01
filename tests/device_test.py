import pytest
import asyncio
from utils.device import BrailleDevice
from utils.braille_translation import braille_translate

@pytest.fixture
def device():
    return BrailleDevice()

@pytest.mark.asyncio
async def test_load_text_paginates(device):
    device._cells = 4
    braille_data = braille_translate("hola")
    result = await device.load_text(braille_data)

    assert result == True
    assert device.total_lines > 0
    assert device.current_line == 0
    for line in device._lines:
        assert len(line) <= 4

@pytest.mark.asyncio
async def test_load_text_empty(device):
    result = await device.load_text([])
    assert result == False
    assert device.total_lines == 0

@pytest.mark.asyncio
async def test_next_line(device):
    device._cells = 2
    braille_data = braille_translate("hola mundo")
    await device.load_text(braille_data)

    initial_line = device.current_line
    await device.next_line()
    assert device.current_line == initial_line + 1

@pytest.mark.asyncio
async def test_prev_line_at_start(device):
    device._cells = 2
    braille_data = braille_translate("hola")
    await device.load_text(braille_data)

    result = await device.prev_line()
    assert result == False
    assert device.current_line == 0

@pytest.mark.asyncio
async def test_load_text_not_connected(device):
    device._cells = 4
    braille_data = braille_translate("hola")
    result = await device.load_text(braille_data)

    assert result == True
    assert device.is_connected == False