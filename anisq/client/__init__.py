# Copyright (c) 2024-2025 iiPython
# Multipurpose anime searching client based on webtorrent

# Modules
import os
import typing
import zipfile
import tarfile
import subprocess
from pathlib import Path

from anisq import download

# Initialization
downloads = Path(__file__).parent / "downloads"
def nodejs_runtime(command: list[Path | str], function: typing.Callable) -> typing.Any:
    return function(
        command,
        env = os.environ.copy() | {"PATH": f"{downloads / 'node/bin'}{os.pathsep}{os.environ['PATH']}"}
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
        self.process: subprocess.Popen

    def webtorrent(self, magnet: str) -> None:
        self.process = nodejs_runtime([downloads / "node/bin/webtorrent", "download", magnet, "--port", "1338"], subprocess.Popen)

    def search(self, query: str) -> None:
        pass
