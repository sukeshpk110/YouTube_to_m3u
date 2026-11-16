import os
import re
from concurrent.futures import ThreadPoolExecutor
from yt_dlp import YoutubeDL

def process_channel(item):
    name, data = item
    query = f"ytsearch1:{name} live"

    has_cookies = os.path.exists('cookies.txt')
    ydl_opts = {
        'format': 'best',
        'quiet': False,
        'verbose': True,
        'skip_download': True,
        'socket_timeout': 15,
        'cookiefile': 'cookies.txt' if has_cookies else None,
        'extractor_args': {
            'youtube': {
                'player_client': ['web', 'mweb'] if has_cookies else ['android', 'ios']
            }
        }
    }
    
    stream_url = None
    error_reason = "EXTRACTION FAILED OR CHANNEL OFFLINE"
    try:
        with YoutubeDL(ydl_opts) as ydl:
            print(f"[{name}] Searching: {query}")
            info = ydl.extract_info(query, download=False)
            if 'entries' in info and info['entries']:
                entry = info['entries'][0]
                vid_url = entry.get('url') or f"https://www.youtube.com/watch?v={entry.get('id')}"
                sub_info = ydl.extract_info(vid_url, download=False)
                stream_url = sub_info.get('url')
    except Exception as e:
        error_reason = str(e)
        print(f"[{name}] Failed: {e}")

    os.makedirs(os.path.dirname(data["file"]), exist_ok=True)
    if stream_url:
        content = f'#EXTM3U\n#EXTINF:-1 group-title="{data["group"]}" tvg-logo="" tvg-id="", {name}\n{stream_url}\n'
        print(f"[{name}] Success")
    else:
        content = f'#EXTM3U\n#EXTINF:-1 group-title="{data["group"]}" tvg-logo="" tvg-id="", {name}\n# ERROR: {error_reason}\n'
        print(f"[{name}] Wrote failure marker")

    with open(data["file"], 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    config_path = "youtube_channel_info.txt"
    channels = {}

    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("~~") and not line.startswith("#"):
                    parts = [p.strip() for p in line.split("|")]
                    if len(parts) >= 1:
                        name = parts[0]
                        group = parts[2] if len(parts) > 2 else "Malayalam News"
                        slug = re.sub(r'[^a-z0-9]+', '_', name.lower()).strip('_')
                        channels[name] = {
                            "file": f"channels/{slug}.m3u",
                            "group": group
                        }

    with ThreadPoolExecutor(max_workers=6) as executor:
        executor.map(process_channel, channels.items())

    master_lines = ["#EXTM3U"]
    for name, data in channels.items():
        if os.path.exists(data["file"]):
            with open(data["file"], 'r', encoding='utf-8') as f:
                for line in f:
                    line_str = line.strip()
                    if line_str and line_str != "#EXTM3U":
                        master_lines.append(line_str)

    with open("youtube.m3u", 'w', encoding='utf-8') as f:
        f.write("\n".join(master_lines) + "\n")

    print("All channel playlists generated successfully!")

if __name__ == "__main__":
    main()
