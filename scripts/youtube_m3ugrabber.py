import os
from yt_dlp import YoutubeDL

def get_live_stream_url(youtube_url):
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'skip_download': True,
        'playlist_items': '1',
        'socket_timeout': 15,
    }
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=False)
            if 'entries' in info and info['entries']:
                entry = info['entries'][0]
                info = ydl.extract_info(entry['url'], download=False)
            return info.get('url')
    except Exception as e:
        print(f"Error extracting stream for {youtube_url}: {e}")
        return None

channels = {
    "Kannur Vision News 24x7": {
        "url": "https://www.youtube.com/@KannurVisionNews/live",
        "file": "channels/kannur_vision_news_24x7.m3u",
        "group": "Malayalam News"
    }
}

for name, data in channels.items():
    stream_url = get_live_stream_url(data["url"])
    if stream_url:
        content = f"""#EXTM3U
#EXTINF:-1 group-title="{data['group']}" tvg-logo="" tvg-id="", {name}
{stream_url}
"""
        os.makedirs(os.path.dirname(data["file"]), exist_ok=True)
        with open(data["file"], 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Successfully updated {name}")
    else:
        print(f"Failed to fetch valid stream URL for {name}")
