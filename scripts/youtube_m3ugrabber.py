#! /usr/bin/python3
import subprocess

def grab(url):
    cmd = ["yt-dlp", "--remote-components", "ejs:github", "--cookies", "../cookies.txt", "-f", "95/94/93/b/best", "-g", url]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=45)
    for line in result.stdout.splitlines():
        clean = line.strip()
        if clean.startswith("http"):
            print(clean)
            return
    err = result.stderr.strip().replace("\n", " | ")
    print(f"# ERROR: {err}")

print('#EXTM3U')
with open('../youtube_channel_info.txt') as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('~~'):
            continue
        if not line.startswith('https:'):
            parts = (line + "|||").split('|')
            ch_name, grp_title, tvg_logo, tvg_id = parts.pop(0).strip(), parts.pop(0).strip().title(), parts.pop(0).strip(), parts.pop(0).strip()
            if not grp_title:
                grp_title = "News"
            print(f'\n#EXTINF:-1 group-title="{grp_title}" tvg-logo="{tvg_logo}" tvg-id="{tvg_id}", {ch_name}')
        else:
            grab(line)
