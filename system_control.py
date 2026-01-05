# system_control.py
import os
import subprocess
from ctypes import POINTER, cast
import datetime
import pyautogui
import signal
import psutil

try:
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
except ImportError:
    AudioUtilities = None
    IAudioEndpointVolume = None
    CLSCTX_ALL = None

def _get_volume_interface():
    if AudioUtilities is None:
        raise RuntimeError("pycaw not installed or not available.")
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    return volume

def set_volume_percent(level: int):
    """Set master volume to `level` (0–100)."""
    level = max(0, min(100, level))
    vol = _get_volume_interface()
    # pycaw uses scalar 0.0–1.0
    vol.SetMasterVolumeLevelScalar(level / 100.0, None)

def volume_up(step: int = 5):
    vol = _get_volume_interface()
    current = vol.GetMasterVolumeLevelScalar()
    vol.SetMasterVolumeLevelScalar(min(1.0, current + step / 100.0), None)

def volume_down(step: int = 5):
    vol = _get_volume_interface()
    current = vol.GetMasterVolumeLevelScalar()
    vol.SetMasterVolumeLevelScalar(max(0.0, current - step / 100.0), None)


## screenshot code git neel 
def take_screenshot(save_dir: str = ".") -> str:
    """Take a screenshot and save to a timestamped PNG; returns the file path."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(save_dir, f"screenshot_{timestamp}.png")
    image = pyautogui.screenshot()
    image.save(path)
    return path

# open close application bt gits neel 

def open_app(command: str):
    """Open an app by command/path (e.g., 'notepad', 'calc', 'code')."""
    subprocess.Popen(command, shell=True)

def close_app_by_name(name_substring: str):
    """Close first process whose name contains the substring."""
    for proc in psutil.process_iter(["pid", "name"]):
        try:
            if name_substring.lower() in (proc.info["name"] or "").lower():
                os.kill(proc.info["pid"], signal.SIGTERM)
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False


# shutdow/restart 

def shutdown_system(force: bool = False):
    """Shutdown the machine (Windows)."""
    flag = "/s /t 0"
    if force:
        flag = "/s /f /t 0"
    os.system(f"shutdown {flag}")

def restart_system(force: bool = False):
    """Restart the machine (Windows)."""
    flag = "/r /t 0"
    if force:
        flag = "/r /f /t 0"
    os.system(f"shutdown {flag}")
