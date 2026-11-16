import subprocess
import os

CHANNELS = [
    {
        "filename": "kerala_vision.m3u",
        "name": "Kerala Vision News 24x7",
        "url": "https://www.youtube.com/@keralavisionnews24x7/live",
        "tvg_id": "KeralaVisionNews.in",
    },
    {
        "filename": "kannur_vision.m3u",
        "name": "Kannur Vision News",
        "url": "https://www.youtube.com/@KannurVisionOnlinenews/live",
        "tvg_id": "KannurVisionNews.in",
    },
    {
        "filename": "amrita_news.m3u",
        "name": "Amrita News",
        "url": "https://www.youtube.com/@AmritaNews/live",
        "tvg_id": "AmritaNews.in",
    },
]

def get_live_url(youtube_url):
    try:
        cmd = [
            "yt-dlp",
            "-g",
            "--extractor-args", "youtube:player_client=web_safari,ios",
            "-f", "b[vcodec^=avc1][acodec^=mp4a]/best[ext=mp4]/best",
            youtube_url,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        links = result.stdout.strip().splitlines()
        return links[0] if links else None
    except Exception as e:
        print(f"Error extracting {youtube_url}: {e}")
        return None

def generate_m3u():
    os.makedirs("channels", exist_ok=True)
    master_content = "#EXTM3U\n\n"
    
    for channel in CHANNELS:
        print(f"Processing {channel['name']}...")
        stream_url = get_live_url(channel["url"])
        
        if stream_url:
            channel_content = "#EXTM3U\n\n"
            entry = f"#EXTINF:-1 tvg-id=\"{channel['tvg_id']}\" tvg-name=\"{channel['name']}\" group-title=\"Malayalam News\",{channel['name']}\n{stream_url}\n\n"
            
            channel_content += entry
            master_content += entry
            
            # Save individual channel file
            with open(os.path.join("channels", channel["filename"]), "w", encoding="utf-8") as f:
                f.write(channel_content)
                
            print(f"Successfully grabbed live link for {channel['name']}")
        else:
            print(f"Could not grab live link for {channel['name']}")

    # Save master playlist
    with open("youtube.m3u", "w", encoding="utf-8") as f:
        f.write(master_content)

    print("All M3U playlists generated successfully!")

if __name__ == "__main__":
    generate_m3u()
