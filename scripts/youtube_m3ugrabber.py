import os
import re
import traceback
from yt_dlp import YoutubeDL

def get_stream_url(query):
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'skip_download': True,
        'socket_timeout': 15,
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'ios']
            }
        }
    }
    try:
        with YoutubeDL(ydl_opts) as ydl:
            print(f"Searching/Extracting: {query}")
            info = ydl.extract_info(query, download=False)
            if 'entries' in info and info['entries']:
                for entry in info['entries']:
                    vid_url = entry.get('url') or f"https://www.youtube.com/watch?v={entry.get('id')}"
                    try:
                        sub_info = ydl.extract_info(vid_url, download=False)
                        s_url = sub_info.get('url')
                        if s_url:
                            return s_url
                    except Exception:
                        continue
            elif 'url' in info:
                return info.get('url')
    except Exception as e:
        print(f"Error extracting {query}: {e}")
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
                        identifier = parts[1]
                        group = parts[2] if len(parts) > 2 else "Malayalam News"
                        
                        slug = re.sub(r'[^a-z0-9]+', '_', name.lower()).strip('_')
                        channels[name] = {
                            "identifier": identifier,
                            "file": f"channels/{slug}.m3u",
                            "group": group
                        }

    for name, data in channels.items():
        try:
            print(f"Processing channel: {name}...")
            identifier = data["identifier"]
            
            if identifier.startswith("http"):
                queries = [identifier, f"ytsearch1:{name} live"]
            elif identifier.startswith("UC"):
                queries = [f"https://www.youtube.com/channel/{identifier}/live", f"ytsearch1:{name} live"]
            elif identifier.startswith("@"):
                queries = [f"https://www.youtube.com/{identifier}/live", f"ytsearch1:{name} live"]
            else:
                queries = [f"https://www.youtube.com/@{identifier}/live", f"ytsearch1:{name} live"]

            stream_url = None
            for q in queries:
                stream_url = get_stream_url(q)
                if stream_url:
                    break
            
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
        except Exception as channel_err:
            print(f"Failed processing {name}: {channel_err}")
            traceback.print_exc()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Global script error: {e}")
        traceback.print_exc()
