
# Bing Wallpaper for GNOME

A simple Python script that sets Bing's picture of the day as your GNOME wallpaper on Linux (Wayland-friendly).

## Features
- Downloads Bing's daily wallpaper
- Tries UHD resolution first, falls back to HD
- Caches images in `~/.cache/bing-wallpaper`
- Sets wallpaper using `gsettings` (GNOME only)

## Installation
Clone the repository:
```bash
git clone https://github.com/<your-username>/bing_wallpaper.git
cd bing_wallpaper
python bing_wallpaper.py
```
