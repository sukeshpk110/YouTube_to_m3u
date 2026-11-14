import os
from yt_dlp import YoutubeDL

def get_stream_with_fallback():
    ydl_opts = {
        'format': 'best',
        'quiet': False,
        'skip_download': True,
        'socket_timeout': 15,
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'ios']
            }
        }
    }
    
    queries = [
        "ytsearch1:Kannur Vision Online live",
        "ytsearch1:Kannur Vision 24X7 LIVE",
        "ytsearch1:Kannur Vision News"
    ]
    
    try:
        with YoutubeDL(ydl_opts) as ydl:
            for q in queries:
                print(f"Trying query: {q}")
                try:
                    info = ydl.extract_info(q, download=False)
                    if 'entries' in info and info['entries']:
                        entry = info['entries'][0]
                        vid_url = entry.get('url') or f"https://www.youtube.com/watch?v={entry.get('id')}"
                        sub_info = ydl.extract_info(vid_url, download=False)
                        s_url = sub_info.get('url')
                        if s_url:
                            print(f"Successfully extracted stream using: {q}")
                            return s_url
                except Exception as query_e:
                    print(f"Query '{q}' failed: {query_e}")
                    continue
    except Exception as e:
        print(f"General extraction error: {e}")
        
    return None

channels = {
    "Kannur Vision News 24x7": {
        "file": "channels/kannur_vision_news_24x7.m3u",
        "group": "Malayalam News"
    }
}

for name, data in channels.items():
    print(f"Processing {name}...")
    stream_url = get_stream_with_fallback()
    
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
