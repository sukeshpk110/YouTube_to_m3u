#! /usr/bin/python3
import subprocess
import sys

def grab(url):
    try:
        cmd = ["yt-dlp", "-f", "95/94/93/b", "-g", url]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        links = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        if links:
            print(links[0])
            return
    except Exception:
        pass
    print("https://raw.githubusercontent.com/benmoose39/YouTube_to_m3u/main/assets/moose_na.m3u")

print('#EXTM3U')
with open('../youtube_channel_info.txt') as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('~~'):
            continue
        if not line.startswith('https:'):
            parts = line.split('|')
            ch_name = parts[0].strip()
            grp_title = parts[1].strip().title() if len(parts) > 1 else "News"
            tvg_logo = parts[2].strip() if len(parts) > 2 else ""
            tvg_id = parts[3].strip() if len(parts) > 3 else ""
            print(f'\n#EXTINF:-1 group-title="{grp_title}" tvg-logo="{tvg_logo}" tvg-id="{tvg_id}", {ch_name}')
        else:
            grab(line)
