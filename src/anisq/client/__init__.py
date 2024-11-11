# Copyright (c) 2024 iiPython
# Multipurpose anime searching client based on Consumet

# Modules
import requests
from typing import List

# Main class
class AnimeClient():
    def __init__(self) -> None:
        self.session = requests.Session()
        self.base_url = "https://anisq.iipython.dev/v1"

    def search(self, query: str) -> List[dict]:
        return self.session.get(f"{self.base_url}/search", params = {"q": query}).json()

    def info(self, media_id: str) -> dict:
        return self.session.get(f"{self.base_url}/info", params = {"id": media_id}).json()

    def watch(self, episode_id: str) -> str:
        sources = [s for s in self.session.get(f"{self.base_url}/watch", params = {"id": episode_id}).json()["sources"] if s["quality"][0].isdigit()]
        return [s for s in sources if s["quality"] == f"{max([int(s["quality"][:-1]) for s in sources])}p"][0]["url"]
