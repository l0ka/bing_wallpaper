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

## Autostart at Login
Create `~/.config/autostart/bing-wallpaper.desktop`:
```ini
[Desktop Entry]
Type=Application
Name=Bing Wallpaper
Comment=Set Bing picture of the day as wallpaper
Exec=/home/<your-username>/Documents/bing_wallpaper/bing_wallpaper.py
X-GNOME-Autostart-enabled=true
```
Replace `<your-username>` with your actual username.

## Daily Refresh with systemd
Create `~/.config/systemd/user/bing-wallpaper.service`:
```ini
[Unit]
Description=Bing Wallpaper of the Day

[Service]
Type=oneshot
ExecStart=/home/<your-username>/Documents/bing_wallpaper/bing_wallpaper.py
```

Create `~/.config/systemd/user/bing-wallpaper.timer`:
```ini
[Unit]
Description=Run Bing Wallpaper daily

[Timer]
OnCalendar=daily
Persistent=true
Unit=bing-wallpaper.service

[Install]
WantedBy=timers.target
```

Enable and start the timer:
```bash
systemctl --user daemon-reload
systemctl --user enable --now bing-wallpaper.timer
```

Check status:
```bash
systemctl --user status bing-wallpaper.timer
journalctl --user -u bing-wallpaper.service -n 50 --no-pager
```

## License
MIT License
