# Copyright (c) 2025 iiPython

# Modules
import os
from pathlib import Path

from anisq import download

# MPV importing (because its special idfk)
mpv_dll_path = Path(__file__).parent / "libmpv-2.dll"
if os.name == "nt" and not mpv_dll_path.is_file():
    print("Downloading MPV DLL bindings (might take a second)...")
    download("https://github.com/gooslol/anisq/releases/download/v1.2.5/libmpv-2.dll", mpv_dll_path)

os.environ["PATH"] = os.path.dirname(__file__) + os.pathsep + os.environ["PATH"]
from mpv import MPV  # noqa: E402

# Handle playback
class Metadata:
    duration:   float = 0
    position:   float = 0
    diderror:   bool = False

def play(title: str, position: float, best_source: str) -> tuple[bool | None, float]:
    meta = Metadata()
    def log_handler(loglevel: str, component: str, message: str) -> None:
        print(component, message)
        meta.diderror = loglevel == "error"

    # Send it off to MPV
    player = MPV(
        log_handler = log_handler,
        title = title,

        # Reenable the OSC
        input_default_bindings = True,
        input_vo_keyboard = True,
        osc = True
    )
    player.time_pos = position

    @player.property_observer("time-pos")
    def time_observer(_name, value):
        if value is not None:
            meta.position = value

    @player.property_observer("duration")
    def duration_observer(_name, value):
        if value is not None:
            meta.duration = value

    player.play(best_source)
    player.wait_for_playback()

    # Handle termination
    player.terminate()
    if meta.diderror:
        return None, meta.position

    # Watch all of a episode except for the last 4 minutes in
    # order for autoplay to actually kick in.
    return meta.position >= (meta.duration - 240), meta.position
