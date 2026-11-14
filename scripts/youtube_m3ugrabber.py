import os
import re
from concurrent.futures import ThreadPoolExecutor
from yt_dlp import YoutubeDL

def process_channel(item):
    name, data = item
    query = f"ytsearch1:{data['query']}"
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'socket_timeout': 8,
        'retries': 1,
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'ios']
            }
        }
    }

    stream_url = None
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=False)
            if 'entries' in info and info['entries']:
                entry = info['entries'][0]
                vid_url = entry.get('url') or f"https://www.youtube.com/watch?v={entry.get('id')}"
                sub_info = ydl.extract_info(vid_url, download=False)
                stream_url = sub_info.get('url')
            elif 'url' in info:
                stream_url = info.get('url')
    except Exception as e:
        print(f"[{name}] Failed: {e}")

    os.makedirs(os.path.dirname(data["file"]), exist_ok=True)
    if stream_url:
        content = f'#EXTM3U\n#EXTINF:-1 group-title="{data["group"]}" tvg-logo="" tvg-id="", {name}\n{stream_url}\n'
        print(f"[{name}] Success")
    else:
        content = f'#EXTM3U\n#EXTINF:-1 group-title="{data["group"]}" tvg-logo="" tvg-id="", {name}\n# ERROR: EXTRACTION FAILED OR CHANNEL OFFLINE\n'
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
                    if len(parts) >= 2:
                        name = parts[0]
                        query_term = parts[1].replace("ytsearch1:", "").strip()
                        group = parts[2] if len(parts) > 2 else "Malayalam News"
                        slug = re.sub(r'[^a-z0-9]+', '_', name.lower()).strip('_')
                        channels[name] = {
                            "query": query_term,
                            "file": f"channels/{slug}.m3u",
                            "group": group
                        }

    # Process all channels concurrently
    with ThreadPoolExecutor(max_workers=6) as executor:
        executor.map(process_channel, channels.items())

if __name__ == "__main__":
    main()
