import struct

try:
    import smbus2
    _bus = smbus2.SMBus(0)
except Exception:
    _bus = None

_ADDRESS = 0x36


def read_battery():
    if _bus is None:
        return {"voltage": None, "percent": None}
    try:
        raw = _bus.read_word_data(_ADDRESS, 0x02)
        raw = struct.unpack("<H", struct.pack(">H", raw))[0]
        voltage = round((raw >> 4) * 1.25 / 1000, 2)

        raw = _bus.read_word_data(_ADDRESS, 0x04)
        raw = struct.unpack("<H", struct.pack(">H", raw))[0]
        percent = raw >> 8

        return {"voltage": voltage, "percent": percent}
    except Exception:
        return {"voltage": None, "percent": None}


def battery_task(socketio):
    while True:
        socketio.emit("battery_update", read_battery())
        socketio.sleep(5)
