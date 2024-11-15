# Copyright (c) 2024 iiPython

# Modules
import os
from pathlib import Path

from rich.console import Console

from requests import get
from wrapt_timeout_decorator import timeout

from .menu import menu
from .client import AnimeClient

from readchar import readkey

# MPV importing (because its special idfk)
mpv_dll_path = Path(__file__).parent / "libmpv-2.dll"
if os.name == "nt" and not mpv_dll_path.is_file():
    print("Downloading MPV DLL bindings (might take a second)...")
    with get("https://github.com/gooslol/anisq/releases/download/v1.2.5/libmpv-2.dll", stream = True) as resp:
        with mpv_dll_path.open("wb") as fh:
            for chunk in resp.iter_content(chunk_size = 8192): 
                fh.write(chunk)

os.environ["PATH"] = os.path.dirname(__file__) + os.pathsep + os.environ["PATH"]
from mpv import MPV  # noqa: E402

# Configuration
__theme__ = "[#90BEDE]"
__version__ = "1.4.2"

# Initialization
rcon, client = Console(), AnimeClient()
def write(text: str) -> None:
    rcon.print(__theme__ + text, highlight = False)

# Handle data
def perform_search(query: str) -> None:
    with rcon.status(f"{__theme__}Searching"):
        results = client.search(query)

    if not results:
        rcon.input("[red]No results found, press [ENTER] to continue.")
        return

    # Loop search results
    while True:
        rcon.clear()
        write(f"Search >>> {query}")

        # Fetch result from menu
        selected = menu.show([(media["id"], media["title"]) for media in results[:10]])
        if selected is None:
            return

        show_details(selected)

def show_details(media_id: str) -> None:
    rcon.clear()
    with rcon.status(f"{__theme__}Locating episodes"):
        media_data = client.info(media_id)

    # Loop episode list
    while True:
        rcon.clear()
        write(f"{media_data['title']} ({media_data['releaseDate']})")
        write("-" * 50)

        # List episodes
        selected_episode = menu.show([(e["number"], f"Episode {e['number']}") for e in media_data["episodes"]])
        if selected_episode is None:
            break

        # Autoplay all episodes starting at the current one
        episodes = [episode for episode in media_data["episodes"] if episode["number"] >= selected_episode]
        for index, episode in enumerate(episodes):
            should_autoplay = play_media(
                episode["id"],
                media_data["title"],
                f"Episode {selected_episode + index}"
            )
            if (not should_autoplay) or (index == len(episodes) - 1):
                break

            # Handle autoplay
            def check_continue() -> None:
                rcon.clear()
                write("Autoplay status: [/][green]✓ Active\n")
                write("Next episode will begin playing in 5 second(s)...")
                write("Press any key to cancel autoplay.")
                readkey()

            try:
                timeout(dec_timeout = 5)(check_continue)()
                break

            except Exception:
                continue

def play_media(episode_id: str, media_title: str, episode_name: str, position: float = 0) -> bool:
    rcon.clear()
    with rcon.status(f"{__theme__}Fetching stream link"):
        best_source = client.watch(episode_id)

    write(f"Now playing: {media_title} - {episode_name}")
    write("Close mpv to continue back to the episode list.")

    # Metadata holding class
    class Metadata():
        duration:   float = 0
        position:   float = 0
        diderror:   bool = False
        
    meta = Metadata()
    def log_handler(loglevel: str, component: str, message: str) -> None:
        meta.diderror = loglevel == "error"

    # Send it off to MPV
    player = MPV(
        log_handler = log_handler,
        title = f"{media_title} - {episode_name}",

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

        # Stream must of died presumably?
        return play_media(episode_id, media_title, episode_name, meta.position)

    # Watch all of a episode except for the last 4 minutes in
    # order for autoplay to actually kick in.
    return meta.position >= (meta.duration - 240)

# Program entrypoint
def main() -> None:
    while True:
        rcon.clear()
        write(f"ani² v{__version__}\nPowered by Geese 24/7, designed for DmmD™\n")

        try:
            search_query = rcon.input(f"{__theme__}Search >>> ")
            if not search_query.strip():
                continue

            perform_search(search_query)

        except KeyboardInterrupt:
            exit()

if __name__ == "__main__":
    main()
