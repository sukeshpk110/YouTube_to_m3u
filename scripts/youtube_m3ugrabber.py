import os
from yt_dlp import YoutubeDL

def get_live_stream_url(url):
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
            print(f"Extracting for: {url}")
            info = ydl.extract_info(url, download=False)
            if 'entries' in info and info['entries']:
                entry = info['entries'][0]
                vid_url = entry.get('url') or f"https://www.youtube.com/watch?v={entry.get('id')}"
                sub_info = ydl.extract_info(vid_url, download=False)
                return sub_info.get('url')
            elif 'url' in info:
                return info.get('url')
    except Exception as e:
        print(f"Extraction error: {e}")
    return None

channels = {
    "Kannur Vision News 24x7": {
        "url": "https://www.youtube.com/channel/UCgVnHatRH3_QCSoQO-bgh9w/live",
        "file": "channels/kannur_vision_news_24x7.m3u",
        "group": "Malayalam News"
    }
}

for name, data in channels.items():
    print(f"Processing {name}...")
    stream_url = get_live_stream_url(data["url"])
    
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
