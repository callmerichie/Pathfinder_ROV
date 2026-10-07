import subprocess

_TEMP_PATH     = "/sys/class/thermal/thermal_zone0/temp"
_WIRELESS_PATH = "/proc/net/wireless"

# vcgencmd get_throttled bits
_UNDER_VOLTAGE_NOW      = 0x1
_THROTTLED_NOW          = 0x4
_UNDER_VOLTAGE_OCCURRED = 0x10000
_THROTTLED_OCCURRED     = 0x40000


def read_system():
    return {
        "temp_c":   _read_temp(),
        **_read_throttled(),
        "wifi_dbm": _read_wifi(),
    }


def _read_temp():
    try:
        with open(_TEMP_PATH) as f:
            return round(int(f.read()) / 1000, 1)
    except Exception:
        return None


def _read_throttled():
    # Output looks like "throttled=0x50000"
    try:
        out = subprocess.run(["vcgencmd", "get_throttled"],
                             capture_output=True, text=True, timeout=2).stdout
        flags = int(out.strip().split("=")[1], 16)
    except Exception:
        return {"under_voltage": None, "throttled": None,
                "under_voltage_occurred": None, "throttled_occurred": None}

    return {
        "under_voltage":          bool(flags & _UNDER_VOLTAGE_NOW),
        "throttled":              bool(flags & _THROTTLED_NOW),
        "under_voltage_occurred": bool(flags & _UNDER_VOLTAGE_OCCURRED),
        "throttled_occurred":     bool(flags & _THROTTLED_OCCURRED),
    }


def _read_wifi():
    # Data line looks like "wlan0: 0000   56.  -54.  -256 ..." → 3rd value is signal level in dBm
    try:
        with open(_WIRELESS_PATH) as f:
            for line in f.readlines()[2:]:
                parts = line.split()
                if parts and parts[0].startswith("wlan"):
                    return int(float(parts[3]))
    except Exception:
        pass
    return None


def system_task(socketio):
    while True:
        socketio.emit("system_update", read_system())
        socketio.sleep(5)
