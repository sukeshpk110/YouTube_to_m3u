import os
import re
from yt_dlp import YoutubeDL

def get_robust_stream_url(channel_name, identifier):
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

    # Build potential extraction targets to try in order
    targets = []
    # 1. Search query targeting active live broadcast
    targets.append(f"ytsearch1:{channel_name} live")
    
    # 2. Direct URL or ID based targets
    if identifier.startswith("http"):
        targets.append(identifier if identifier.endswith("/live") else f"{identifier.rstrip('/')}/live")
    elif identifier.startswith("UC"):
        targets.append(f"https://www.youtube.com/channel/{identifier}/live")
        targets.append(f"https://www.youtube.com/channel/{identifier}")
    elif identifier.startswith("@"):
        targets.append(f"https://www.youtube.com/{identifier}/live")
        targets.append(f"https://www.youtube.com/{identifier}")
    else:
        targets.append(f"https://www.youtube.com/@{identifier}/live")

    try:
        with YoutubeDL(ydl_opts) as ydl:
            for target in targets:
                print(f"Trying target for {channel_name}: {target}")
                try:
                    info = ydl.extract_info(target, download=False)
                    
                    # Handle search results or playlist entries
                    if 'entries' in info and info['entries']:
                        for entry in info['entries']:
                            vid_url = entry.get('url') or f"https://www.youtube.com/watch?v={entry.get('id')}"
                            try:
                                sub_info = ydl.extract_info(vid_url, download=False)
                                s_url = sub_info.get('url')
                                if s_url:
                                    print(f"Successfully extracted stream for {channel_name}!")
                                    return s_url
                            except Exception:
                                continue
                    elif 'url' in info:
                        return info.get('url')
                except Exception as target_e:
                    print(f"Target '{target}' failed: {target_e}")
                    continue
    except Exception as e:
        print(f"General extraction error for {channel_name}: {e}")
        
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
    stream_url = get_robust_stream_url(name, data["identifier"])
    
    os.makedirs(os.path.dirname(data["file"]), exist_
