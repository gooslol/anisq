# Copyright (c) 2024-2025 iiPython

# Modules
from readchar import readkey
from rich.console import Console
from wrapt_timeout_decorator import timeout

from anisq import __version__, __theme__
from anisq.libraries import menu, play
from anisq.client import AnimeClient

# Initialization
rcon, client = Console(), AnimeClient()
def write(text: str) -> None:
    rcon.print(__theme__ + text, highlight = False)

# # Handle data
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
        selected = menu.show(results[:10])
        if selected[1] is None:
            return

        show_details(*selected)

def show_details(name: str, magnet: str) -> None:
    rcon.clear()
    with rcon.status(f"{__theme__}Locating episodes"):
        media_data = client.filelist(magnet)

    # Loop episode list
    while True:
        rcon.clear()
        write(name)
        write("-" * 50)

        # List episodes
        selected_episode = menu.show([(f"Episode {str(index + 1).zfill(2)}", episode, index) for index, episode in enumerate(media_data)])
        if selected_episode is None:
            break

        # Autoplay all episodes starting at the current one
        episodes = [episode for index, episode in enumerate(media_data) if index >= selected_episode[2]]
        for index, episode in enumerate(episodes):
            should_autoplay = play_media(
                name,
                f"Episode {selected_episode[2] + index + 1}",
                episode[1]
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

def play_media(anime_name: str, episode_name: str, magnet_link: str, position: float = 0) -> bool:
    rcon.clear()
    write(f"Now playing: {anime_name} - {episode_name}")
    write("Close mpv to continue back to the episode list.")

    # Metadata holding class
    result, end_position = play(f"{anime_name} - {episode_name}", position, magnet_link)
    exit()
    if result is None:

        # Stream must of died presumably?
        return play_media(anime_name, episode_name, magnet_link, end_position)

    return result

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
