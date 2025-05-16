# Copyright (c) 2024-2025 iiPython

# Modules
# from readchar import readkey
# from rich.console import Console
# from wrapt_timeout_decorator import timeout

# from anisq import __version__, __theme__
# from anisq.menu import menu
from anisq.client import AnimeClient
# from anisq.playback import play

# Initialization
# rcon, client = Console(), AnimeClient()
# def write(text: str) -> None:
    # rcon.print(__theme__ + text, highlight = False)

# # Handle data
# def perform_search(query: str) -> None:
#     with rcon.status(f"{__theme__}Searching"):
#         results = client.search(query)

#     if not results:
#         rcon.input("[red]No results found, press [ENTER] to continue.")
#         return

#     # Loop search results
#     while True:
#         rcon.clear()
#         write(f"Search >>> {query}")

#         # Fetch result from menu
#         selected = menu.show([(media["id"], media["title"]) for media in results[:10]])
#         if selected is None:
#             return

#         show_details(selected)

# def show_details(media_id: str) -> None:
#     rcon.clear()
#     with rcon.status(f"{__theme__}Locating episodes"):
#         media_data = client.info(media_id)

#     # Loop episode list
#     while True:
#         rcon.clear()
#         write(f"{media_data['title']} ({media_data['releaseDate']})")
#         write("-" * 50)

#         # List episodes
#         selected_episode = menu.show([(e["number"], f"Episode {e['number']}") for e in media_data["episodes"]])
#         if selected_episode is None:
#             break

#         # Autoplay all episodes starting at the current one
#         episodes = [episode for episode in media_data["episodes"] if episode["number"] >= selected_episode]
#         for index, episode in enumerate(episodes):
#             should_autoplay = play_media(
#                 episode["id"],
#                 media_data["title"],
#                 f"Episode {selected_episode + index}"
#             )
#             if (not should_autoplay) or (index == len(episodes) - 1):
#                 break

#             # Handle autoplay
#             def check_continue() -> None:
#                 rcon.clear()
#                 write("Autoplay status: [/][green]✓ Active\n")
#                 write("Next episode will begin playing in 5 second(s)...")
#                 write("Press any key to cancel autoplay.")
#                 readkey()

#             try:
#                 timeout(dec_timeout = 5)(check_continue)()
#                 break

#             except Exception:
#                 continue

# def play_media(episode_id: str, media_title: str, episode_name: str, position: float = 0) -> bool:
#     rcon.clear()
#     with rcon.status(f"{__theme__}Fetching stream link"):
#         best_source = client.watch(episode_id)

#     write(f"Now playing: {media_title} - {episode_name}")
#     write("Close mpv to continue back to the episode list.")

#     # Metadata holding class
#     result, end_position = play(f"{media_title} - {episode_name}", position, best_source)
#     if result is None:

#         # Stream must of died presumably?
#         return play_media(episode_id, media_title, episode_name, end_position)

#     return result

# Program entrypoint
def main() -> None:
    pass

    # while True:
    #     rcon.clear()
    #     write(f"ani² v{__version__}\nPowered by Geese 24/7, designed for DmmD™\n")

    #     try:
    #         search_query = rcon.input(f"{__theme__}Search >>> ")
    #         if not search_query.strip():
    #             continue

    #         perform_search(search_query)

    #     except KeyboardInterrupt:
    #         exit()

if __name__ == "__main__":
    main()
