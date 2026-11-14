import os
from yt_dlp import YoutubeDL

def get_live_stream_url():
    channel_url = "https://www.youtube.com/@KannurVisionOnlinenews/streams"
    ydl_opts = {
        'extract_flat': True,
        'quiet': False,
        'skip_download': True,
        'socket_timeout': 20,
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'ios', 'web']
            }
        }
    }
    try:
        with YoutubeDL(ydl_opts) as ydl:
            print(f"Fetching entries from {channel_url}")
            info = ydl.extract_info(channel_url, download=False)
            entries = info.get('entries', [])
            
            target_url = None
            for entry in entries:
                live_status = entry.get('live_status')
                title = entry.get('title', '')
                print(f"Checking video: {title} (status: {live_status})")
                if live_status == 'is_live' or 'LIVE' in title.upper():
                    target_url = entry.get('url') or f"https://www.youtube.com/watch?v={entry.get('id')}"
                    break
            
            # Fallback to the first entry if no explicit live status is flagged
            if not target_url and entries:
                target_url = entries[0].get('url') or f"https://www.youtube.com/watch?v={entries[0].get('id')}"

            if target_url:
                print(f"Extracting playable stream URL from: {target_url}")
                stream_opts = {
                    'format': 'best',
                    'quiet': False,
                    'skip_download': True,
                    'socket_timeout': 20,
                    'extractor_args': {
                        'youtube': {
                            'player_client': ['android', 'ios', 'web']
                        }
                    }
                }
                with YoutubeDL(stream_opts) as sydl:
                    s_info = sydl.extract_info(target_url, download=False)
                    return s_info.get('url')
    except Exception as e:
        print(f"Extraction error: {e}")
    return None

channels = {
    "Kannur Vision News 24x7": {
        "file": "channels/kannur_vision_news_24x7.m3u",
        "group": "Malayalam News"
    }
}

for name, data in channels.items():
    print(f"Processing {name}...")
    stream_url = get_live_stream_url()
    
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
