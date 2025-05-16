# Configuration
__theme__ = "[#90BEDE]"
__version__ = "2.0.0"

# Handle file downloading
import requests
from pathlib import Path

def download(url: str, destination: Path) -> None:
    with requests.get(url, stream = True) as resp:
        with destination.open("wb") as fh:
            for chunk in resp.iter_content(chunk_size = 8192): 
                fh.write(chunk)
