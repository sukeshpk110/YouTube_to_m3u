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
            "--cookies", "cookies.txt",
            "--extractor-args", "youtube:player_client=web,tv_embedded",
            "-f", "95/22/best[height<=720][vcodec^=avc1]/best[height<=720]",
            yt_url
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"yt-dlp error for {name}:\n{result.stderr}")
            continue

        stream_url = result.stdout.strip().split("\n")[0]
        
        if stream_url:
            channel_content = f"#EXTM3U\n#EXTINF:-1,{name.replace('_', ' ').title()}\n{stream_url}\n"
            with open(f"channels/{name}.m3u", "w") as f:
                f.write(channel_content)
            
            master_playlist += f"#EXTINF:-1,{name.replace('_', ' ').title()}\n{stream_url}\n"
            print(f"Successfully extracted {name}")
    except Exception as e:
        print(f"Failed to extract {name}: {e}")

with open("youtube.m3u", "w") as f:
    f.write(master_playlist)

print("Playlist generation complete.")
