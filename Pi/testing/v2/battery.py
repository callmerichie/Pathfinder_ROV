import os
import struct
import subprocess

try:
    import smbus2
    _bus = smbus2.SMBus(1)
except Exception:
    _bus = None

try:
    from gpiozero import DigitalInputDevice
    _ac_pin = DigitalInputDevice(6)   # X728 AC-loss signal: high = adapter unplugged
except Exception:
    _ac_pin = None

_ADDRESS = 0x36

_LOW_V      = 3.50   # warn in the UI
_CRITICAL_V = 3.30   # stop motors and shut down
_MIN_VALID_V = 2.5   # below this the reading is a glitch, not a real cell voltage
_CRITICAL_READINGS = 3   # consecutive critical readings (×5 s) before acting, ignores short load dips
_SHUTDOWN_DELAY = 10     # seconds the UI shows the warning before the Pi goes down

# xSoft.sh pulses GPIO26: X728 asks the Pi to halt (via xPWR.sh) and then cuts battery power
_X728_OFF = "/usr/local/bin/xSoft.sh"


def read_battery():
    data = {"voltage": None, "percent": None, "on_battery": _on_battery()}
    if _bus is None:
        return data
    try:
        raw = _bus.read_word_data(_ADDRESS, 0x02)
        raw = struct.unpack("<H", struct.pack(">H", raw))[0]
        data["voltage"] = round((raw >> 4) * 1.25 / 1000, 2)

        raw = _bus.read_word_data(_ADDRESS, 0x04)
        raw = struct.unpack("<H", struct.pack(">H", raw))[0]
        data["percent"] = raw >> 8
    except Exception:
        pass
    return data


def _on_battery():
    if _ac_pin is None:
        return None
    try:
        return bool(_ac_pin.value)
    except Exception:
        return None


def _status(data):
    v = data["voltage"]
    # Charging (on_battery False) never triggers; unknown AC state (None) trusts the voltage
    if v is None or v < _MIN_VALID_V or data["on_battery"] is False:
        return "ok"
    if v <= _CRITICAL_V:
        return "critical"
    if v <= _LOW_V:
        return "low"
    return "ok"


def battery_task(socketio, keys, keys_lock):
    critical_count = 0
    while True:
        data = read_battery()
        data["status"] = _status(data)
        socketio.emit("battery_update", data)

        critical_count = critical_count + 1 if data["status"] == "critical" else 0
        if critical_count >= _CRITICAL_READINGS:
            _safe_shutdown(socketio, keys, keys_lock, data["voltage"])
            return
        socketio.sleep(5)


def _stop_motors(keys, keys_lock):
    with keys_lock:
        keys[:] = [0, 0, 0, 0]


def _safe_shutdown(socketio, keys, keys_lock, voltage):
    print(f"Battery critical ({voltage} V): stopping motors, shutting down in {_SHUTDOWN_DELAY} s")
    _stop_motors(keys, keys_lock)
    socketio.emit("battery_shutdown", {"voltage": voltage, "delay": _SHUTDOWN_DELAY})
    socketio.sleep(_SHUTDOWN_DELAY)

    # Again, in case a key was pressed during the countdown; driving_rov sends it within 10 ms
    _stop_motors(keys, keys_lock)
    socketio.sleep(0.5)

    if os.path.exists(_X728_OFF):
        subprocess.run([_X728_OFF, "0", "26"])
        socketio.sleep(30)
    # Fallback (no xSoft.sh, or the X728 didn't react): plain halt, the X728 keeps draining slowly
    subprocess.run(["sudo", "-n", "shutdown", "-h", "now"])
