import os
import subprocess

def get_live_stream_url(youtube_url):
    cmd = [
        "yt-dlp",
        "--js-runtimes", "node",
        "--extractor-args", "youtube:player_client=android,ios",
        "--format", "best",
        "--get-url",
        "--skip-download",
        "--socket-timeout", "20",
        youtube_url
    ]
    try:
        print(f"Running command for: {youtube_url}")
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        url = result.stdout.strip().splitlines()
        if url:
            return url[0]
    except subprocess.CalledProcessError as e:
        print(f"yt-dlp error: {e.stderr}")
    return None

# Channel configuration
channels = {
    "Kannur Vision News 24x7": {
        "url": "https://www.youtube.com/@KannurVisionNews/live",
        "file": "channels/kannur_vision_news_24x7.m3u",
        "group": "Malayalam News"
    }
}

for name, data in channels.items():
    print(f"Processing {name}...")
    stream_url = get_live_stream_url(data["url"])
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
