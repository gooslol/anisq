# Copyright (c) 2024-2025 iiPython
# Multipurpose anime searching client based on webtorrent

# Modules
import os
import time
import atexit
import shutil
import typing
import zipfile
import tarfile
import tempfile
import subprocess
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from anisq import download

# Initialization
downloads = Path(__file__).parent / "downloads"
def nodejs_runtime(command: list[Path | str], function: typing.Callable) -> typing.Any:
    return function(
        command,
        env = os.environ.copy() | {"PATH": f"{downloads / 'node/bin'}{os.pathsep}{os.environ['PATH']}"},
        stdout = subprocess.DEVNULL,
        stderr = subprocess.DEVNULL
    )

# Handle downloading
if not downloads.is_dir():
    downloads.mkdir()

    # Download node runtime
    print("Downloading Node.js runtime (might take a few seconds)...")
    download({
        "nt": "https://nodejs.org/dist/latest-v22.x/node-v22.15.1-win-x64.zip",
        "posix": "https://nodejs.org/dist/latest-v22.x/node-v22.15.1-linux-x64.tar.gz"
    }[os.name], downloads / "node.bin")
    if os.name == "nt":
        with zipfile.ZipFile(downloads / "node.bin", "r") as file:
            file.extractall(downloads)

    else:
        with tarfile.open(downloads / "node.bin") as file:
            file.extractall(downloads)

    (downloads / "node.bin").unlink()
    for item in downloads.glob("node-*"):
        item.rename(downloads / "node")  # Normalize

    # Install webtorrent-cli
    nodejs_runtime([downloads / "node/bin/npm", "i", "-g", "webtorrent-cli"], subprocess.run)

# Main class
class AnimeClient:
    def __init__(self) -> None:
        self.session = requests.Session()
        self.tmpfile = tempfile.mkdtemp()
        self.process: typing.Optional[subprocess.Popen] = None

        atexit.register(self.cleanup)

    def cleanup(self) -> None:
        self.stop()
        shutil.rmtree(self.tmpfile)

    def stop(self) -> None:
        if self.process is not None:
            self.process.kill()

    def webtorrent(self, magnet: str) -> None:
        self.process = nodejs_runtime([downloads / "node/bin/webtorrent", magnet, "--port", "1338", "--out", self.tmpfile, "--quiet"], subprocess.Popen)

    def search(self, query: str) -> list[tuple[str, str]]:
        soup = BeautifulSoup(self.session.get("https://nyaa.si", params = {"f": "1", "c": "1_2", "q": query}).text, "html.parser")

        # Build result list
        results = []
        for element in soup.select("tr.success"):

            # Fetch elements
            title_link  = element.select_one("td[colspan = '2'] > a:not(.comments)")
            magnet_link = element.select_one("td.text-center > a:last-child")

            # Add to results
            if not all({title_link, magnet_link}):
                continue

            results.append((
                title_link.text,         # pyright: ignore
                magnet_link.get("href")  # pyright: ignore
            ))

        return results

    def filelist(self, magnet: str) -> list[tuple[str, str]]:
        self.webtorrent(magnet)

        # Check until webtorrent starts
        while True:
            try:
                torrent = BeautifulSoup(self.session.get("http://localhost:1338/webtorrent").text, "html.parser").select_one("a")
                if torrent is None:
                    time.sleep(1)
                    continue
                
                filelist = [
                    (link.text.strip().removeprefix(f"{torrent.text.strip()}/"), f"http://localhost:1338{link.get('href')}")
                    for link in BeautifulSoup(self.session.get(f"http://localhost:1338{torrent.get('href')}").text, "html.parser").select("a")
                ]
                if not filelist:
                    time.sleep(1)
                    continue

                return filelist

            except requests.exceptions.ConnectionError:
                time.sleep(1)
