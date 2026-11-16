import os
import subprocess

# Define your channels
channels = {
    "amrita_news": "https://www.youtube.com/@AmritaNews/live",
    "kerala_vision": "https://www.youtube.com/@keralavisionnews24x7/live",
    "kannur_vision": "https://www.youtube.com/@KannurVisionOnlinenews/live"
}

os.makedirs("channels", exist_ok=True)
master_playlist = "#EXTM3U\n"

for name, yt_url in channels.items():
    try:
        print(f"Extracting stream for {name}...")
        cmd = [
            "yt-dlp",
            "-g",
            "--cookies", "cookies.txt",
            "--extractor-args", "youtube:player_client=ios,web_safari",
            yt_url
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        stream_url = result.stdout.strip().split("\n")[0]
        
        if stream_url:
            # Create individual channel file
            channel_content = f"#EXTM3U\n#EXTINF:-1,{name.replace('_', ' ').title()}\n{stream_url}\n"
            with open(f"channels/{name}.m3u", "w") as f:
                f.write(channel_content)
            
            # Append to master playlist
            master_playlist += f"#EXTINF:-1,{name.replace('_', ' ').title()}\n{stream_url}\n"
            print(f"Successfully extracted {name}")
    except Exception as e:
        print(f"Failed to extract {name}: {e}")

# Save master playlist
with open("youtube.m3u", "w") as f:
    f.write(master_playlist)

print("Playlist generation complete.")
