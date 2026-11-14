import os
import re
import urllib.request
import xml.etree.ElementTree as ET
from yt_dlp import YoutubeDL

def get_latest_video_from_rss(channel_id):
    rss_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    try:
        req = urllib.request.Request(
            rss_url,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        with urllib.request.urlopen(req) as response:
            xml_data = response.read()
        
        root = ET.fromstring(xml_data)
        ns = {'yt': 'http://www.youtube.com/xml/schemas/2015', 'atom': 'http://www.w3.org/2005/Atom'}
        
        entry = root.find('atom:entry', ns)
        if entry is not None:
            video_id_elem = entry.find('yt:videoId', ns)
            if video_id_elem is not None:
                return f"https://www.youtube.com/watch?v={video_id_elem.text}"
    except Exception as e:
        print(f"RSS error for {channel_id}: {e}")
    return None

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
            print(f"Extracting stream from: {watch_url}")
            info = ydl.extract_info(watch_url, download=False)
            return info.get('url')
    except Exception as e:
        print(f"Extraction error: {e}")
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
                    # Generate clean uniform filename slug
                    slug = re.sub(r'[^a-z0-9]+', '_', name.lower()).strip('_')
                    channels[name] = {
                        "identifier": identifier,
                        "file": f"channels/{slug}.m3u",
                        "group": group
                    }

for name, data in channels.items():
    print(f"Processing channel: {name}...")
    identifier = data["identifier"]
    
    watch_url = None
    if identifier.startswith("UC"):
        watch_url = get_latest_video_from_rss(identifier)
    elif identifier.startswith("http"):
        watch_url = identifier
    elif identifier.startswith("@"):
        watch_url = f"https://www.youtube.com/{identifier}/live"
    else:
        watch_url = f"https://www.youtube.com/@{identifier}/live"
        
    stream_url = None
    if watch_url:
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
