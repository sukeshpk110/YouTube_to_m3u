import os
import re
from yt_dlp import YoutubeDL

def get_stream_with_fallback(channel_name, query_term):
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
    
    # Build fallback search variations
    queries = [
        f"ytsearch1:{query_term}",
        f"ytsearch1:{channel_name} live stream",
        f"ytsearch1:{channel_name}"
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
        print(f"General extraction error for {channel_name}: {e}")
        
    return None

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
                        query_term = parts[1]
                        group = parts[2] if len(parts) > 2 else "Malayalam News"
                        
                        slug = re.sub(r'[^a-z0-9]+', '_', name.lower()).strip('_')
                        channels[name] = {
                            "query": query_term,
                            "file": f"channels/{slug}.m3u",
                            "group": group
                        }

    for name, data in channels.items():
        print(f"Processing channel: {name}...")
        stream_url = get_stream_with_fallback(name, data["query"])
        
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

if __name__ == "__main__":
    main()
