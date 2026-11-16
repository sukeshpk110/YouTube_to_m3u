import os
import subprocess

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
            "--extractor-args", "youtube:player_client=ios",
            "-f", "95/94/best[height<=720][protocol*=m3u8]",
            yt_url
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"yt-dlp error for {name}:\n{result.stderr}")
            continue

        stream_url = result.stdout.strip().split("\n")[0]
        
        if stream_url:
            title = name.replace("_", " ").title()
            header = (
                f"#EXTINF:-1,{title}\n"
                f"#EXTVLCOPT:http-user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15\n"
                f"#EXTVLCOPT:http-referrer=https://www.youtube.com/\n"
            )
            with open(f"channels/{name}.m3u", "w") as f:
                f.write(f"#EXTM3U\n{header}{stream_url}\n")
            
            master_playlist += f"{header}{stream_url}\n"
            print(f"Successfully extracted {name}")
    except Exception as e:
        print(f"Failed to extract {name}: {e}")

with open("youtube.m3u", "w") as f:
    f.write(master_playlist)

print("Playlist generation complete.")
