import os
import urllib.request
import xml.etree.ElementTree as ET
from yt_dlp import YoutubeDL

def get_latest_video_url_from_rss(channel_id):
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
                video_id = video_id_elem.text
                return f"https://www.youtube.com/watch?v={video_id}"
    except Exception as e:
        print(f"Error fetching RSS feed: {e}")
    return None

def get_live_stream_url(watch_url):
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
            print(f"Extracting stream for: {watch_url}")
            info = ydl.extract_info(watch_url, download=False)
            return info.get('url')
    except Exception as e:
        print(f"Error extracting stream: {e}")
        return None

channels = {
    "Kannur Vision News 24x7": {
        "channel_id": "UCgVnHatRH3_QCSoQO-bgh9w",
        "file": "channels/kannur_vision_news_24x7.m3u",
        "group": "Malayalam News"
    }
}

for name, data in channels.items():
    print(f"Processing {name}...")
    watch_url = get_latest_video_url_from_rss(data["channel_id"])
    if not watch_url:
        print(f"Failed to get video URL from RSS for {name}")
        continue
        
    stream_url = get_live_stream_url(watch_url)
    if stream_url:
        content = f"""#EXTM3U
#EXTINF:-1 group-title="{data['group']}" tvg-logo="" tvg-id="", {name}
{stream_url}
"""
        os.makedirs(os.path.dirname(data["file"]), exist_ok=True)
        with open(data["file"], 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Successfully updated {data['file']}")
    else:
        print(f"Failed to fetch valid stream URL for {name}")
