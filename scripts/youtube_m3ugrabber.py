import subprocess
import os

# Define your 3 Malayalam news channels
CHANNELS = [
    {
        "name": "Kerala Vision News 24x7",
        "url": "https://www.youtube.com/@keralavisionnews24x7/live",
        "tvg_id": "KeralaVisionNews.in",
    },
    {
        "name": "Kannur Vision News",
        "url": "https://www.youtube.com/@KannurVisionOnlinenews/live",
        "tvg_id": "KannurVisionNews.in",
    },
    {
        "name": "Amrita News",
        "url": "https://www.youtube.com/@AmritaNews/live",
        "tvg_id": "AmritaNews.in",
    },
]

def get_live_url(youtube_url):
    try:
        # Use yt-dlp to extract the direct live stream link
        cmd = [
            "yt-dlp",
            "-g",
            "--extractor-args", "youtube:player_client=web_safari,ios",
            "-f", "best[protocol*=m3u8]/best/bestvideo+bestaudio",
            youtube_url,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        links = result.stdout.strip().splitlines()
        return links[0] if links else None
    except Exception as e:
        print(f"Error extracting {youtube_url}: {e}")
        return None

def generate_m3u():
    m3u_content = "#EXTM3U\n\n"
    
    for channel in CHANNELS:
        print(f"Processing {channel['name']}...")
        stream_url = get_live_url(channel["url"])
        
        if stream_url:
            m3u_content += f"#EXTINF:-1 tvg-id=\"{channel['tvg_id']}\" tvg-name=\"{channel['name']}\" group-title=\"Malayalam News\",{channel['name']}\n"
            m3u_content += f"{stream_url}\n\n"
            print(f"Successfully grabbed live link for {channel['name']}")
        else:
            print(f"Could not grab live link for {channel['name']} (Channel might be offline)")

    # Save to youtube.m3u and channels/ folder
    os.makedirs("channels", exist_ok=True)
    with open("youtube.m3u", "w", encoding="utf-8") as f:
        f.write(m3u_content)
    
    with open("channels/malayalam_news.m3u", "w", encoding="utf-8") as f:
        f.write(m3u_content)

    print("M3U generation complete!")

if __name__ == "__main__":
    generate_m3u()
