#!/usr/bin/env python3

"""
Bing Wallpaper of the Day
"""

import json
import logging
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from datetime import datetime

# ---------- Logging ----------
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("bing_wallpaper")

# ---------- Constants ----------
BING_URL = "https://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1"
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
MAX_ATTEMPTS = 5
INITIAL_BACKOFF = 1.0
BACKOFF_MULTIPLIER = 2.0
TIMEOUT = 15

# ---------- Helpers ----------
def http_get(url: str, timeout: int = TIMEOUT) -> bytes:
    attempt = 0
    last_exc = None
    while attempt < MAX_ATTEMPTS:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read()
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
            last_exc = e
            attempt += 1
            sleep_s = INITIAL_BACKOFF * (BACKOFF_MULTIPLIER ** (attempt - 1))
            logger.warning(f"HTTP GET failed (attempt {attempt}/{MAX_ATTEMPTS}) for {url}: {e}. Retrying in {sleep_s:.1f}s...")
            time.sleep(sleep_s)
    raise last_exc if last_exc else RuntimeError("Unknown network error")

def ensure_cache_dir() -> Path:
    cache_dir = Path.home() / ".cache" / "bing-wallpaper"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir

def get_image_urls() -> tuple[str, str]:
    """
    Fetch Bing JSON once, extract url and urlbase.
    Returns (hd_url, uhd_url).
    """
    raw = http_get(BING_URL)
    data = json.loads(raw.decode("utf-8"))
    img = data.get("images", [{}])[0]
    url = img.get("url")
    urlbase = img.get("urlbase")
    if not url or not urlbase:
        raise RuntimeError("Missing url/urlbase in Bing response")
    hd_url = f"https://www.bing.com{url}"
    uhd_url = f"https://www.bing.com{urlbase}_UHD.jpg"
    return hd_url, uhd_url

def download_image(urls: tuple[str, str], cache_dir: Path, date_str: str) -> Path:
    filename = f"bing_{date_str}.jpg"
    filepath = cache_dir / filename
    if filepath.exists():
        logger.info(f"Using cached image: {filepath}")
        return filepath

    # Try UHD first
    for url in [urls[1], urls[0]]:
        try:
            logger.info(f"Attempting download: {url}")
            body = http_get(url, timeout=30)
            with open(filepath, "wb") as f:
                f.write(body)
            logger.info(f"Image saved to {filepath}")
            return filepath
        except Exception as e:
            logger.warning(f"Failed to download from {url}: {e}")
    raise RuntimeError("Both UHD and HD downloads failed")

def set_gnome_wallpaper(image_path: Path) -> bool:
    import subprocess
    uri = f"file://{image_path.resolve()}"
    cmds = [
        ["gsettings", "set", "org.gnome.desktop.background", "picture-uri", uri],
        ["gsettings", "set", "org.gnome.desktop.background", "picture-uri-dark", uri],
        ["gsettings", "set", "org.gnome.desktop.background", "picture-options", "zoom"],
    ]
    for cmd in cmds:
        subprocess.run(cmd, check=True)
    logger.info("Wallpaper set.")
    return True

def run_once() -> bool:
    logger.info("Starting Bing Wallpaper")
    cache_dir = ensure_cache_dir()
    date_str = datetime.now().strftime("%Y%m%d")
    hd_url, uhd_url = get_image_urls()
    image_path = download_image((hd_url, uhd_url), cache_dir, date_str)
    return set_gnome_wallpaper(image_path)

def main():
    try:
        success = run_once()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
