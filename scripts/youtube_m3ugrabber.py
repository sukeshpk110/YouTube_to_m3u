#! /usr/bin/python3
import os
import re
import subprocess

os.makedirs("../channels", exist_ok=True)

def grab(url):
    cmd = ["yt-dlp", "--remote-components", "ejs:github", "--cookies", "../cookies.txt", "-f", "95/94/93/b/best", "-g", url]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=45)
    for line in result.stdout.splitlines():
        clean = line.strip()
        if clean.startswith("http"):
            return clean
    return "https://githubusercontent.com"

print('#EXTM3U')
current_meta = None

with open('../youtube_channel_info.txt') as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('~~'):
            continue
        if not line.startswith('https:'):
            parts = (line + "|||").split('|')
            ch_name = parts.pop(0).strip()
            grp_title = parts.pop(0).strip().title() or "News"
            tvg_logo = parts.pop(0).strip()
            tvg_id = parts.pop(0).strip()
            extinf = f'#EXTINF:-1 group-title="{grp_title}" tvg-logo="{tvg_logo}" tvg-id="{tvg_id}", {ch_name}'
            print(f'\n{extinf}')
            current_meta = (ch_name, extinf)
        else:
            stream_url = grab(line)
            print(stream_url)
            if current_meta:
                ch_name, extinf = current_meta
                safe_name = re.sub(r'[^a-z0-9]+', '_', ch_name.lower()).strip('_')
                with open(f"../channels/{safe_name}.m3u", "w", encoding="utf-8") as ch_file:
                    ch_file.write(f"#EXTM3U\n{extinf}\n{stream_url}\n")
                current_meta = None
