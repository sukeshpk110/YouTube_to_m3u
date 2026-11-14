import os
import re
from yt_dlp import YoutubeDL

def get_stream_url(watch_url):
    ydl_opts = {
        'format': 'best',
        'quiet': False,
        'skip_download': True,
        'socket_timeout': 20,
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'ios']
            }
        }
    }
    try:
        with YoutubeDL(ydl_opts) as ydl:
            print(f"Extracting live stream from: {watch_url}")
            info = ydl.extract_info(watch_url, download=False)
            
            # If it's a playlist/channel container, grab the first active entry
            if 'entries' in info and info['entries']:
                entry = info['entries'][0]
                vid_url = entry.get('url') or f"https://www.youtube.com/watch?v={entry.get('id')}"
                sub_info = ydl.extract_info(vid_url, download=False)
                return sub_info.get('url')
            
            return info.get('url')
    except Exception as e:
        print(f"Extraction error for {watch_url}: {e}")
    return None

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
                    identifier = parts[1]
                    group = parts[2] if len(parts) > 2 else "Malayalam News"
                    
                    slug = re.sub(r'[^a-z0-9]+', '_', name.lower()).strip('_')
                    channels[name] = {
                        "identifier": identifier,
                        "file": f"channels/{slug}.m3u",
                        "group": group
                    }

for name, data in channels.items():
    print(f"Processing channel: {name}...")
    identifier = data["identifier"]
    
    # Construct direct live URL
    if identifier.startswith("http"):
        watch_url = identifier if identifier.endswith("/live") else f"{identifier.rstrip('/')}/live"
    elif identifier.startswith("UC"):
        watch_url = f"https://www.youtube.com/channel/{identifier}/live"
    elif identifier.startswith("@"):
        watch_url = f"https://www.youtube.com/{identifier}/live"
    else:
        watch_url = f"https://www.youtube.com/@{identifier}/live"
        
    stream_url = get_stream_url(watch_url)
        
    os.makedirs(os.path.dirname(data["file"]), exist_ok=True)
    if stream_url:
        content = f"""#EXTM3U
#EXTINF:-1 group-title="{data['group']}" tvg-logo="" tvg-id="", {name}
{stream_url}
"""
        with open(data["file"], 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Successfully updated {data['file']}")
    else:
        content = f"""#EXTM3U
#EXTINF:-1 group-title="{data['group']}" tvg-logo="" tvg-id="", {name}
# ERROR: EXTRACTION FAILED OR CHANNEL OFFLINE
"""
        with open(data["file"], 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Wrote failure marker for {name}")
