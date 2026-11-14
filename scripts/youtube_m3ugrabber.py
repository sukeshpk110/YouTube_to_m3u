import os
import re
from yt_dlp import YoutubeDL

def get_channel_live_url(identifier):
    # Determine channel URL format
    if identifier.startswith("http"):
        base_url = identifier.rstrip('/')
    elif identifier.startswith("UC"):
        base_url = f"https://www.youtube.com/channel/{identifier}"
    elif identifier.startswith("@"):
        base_url = f"https://www.youtube.com/{identifier}"
    else:
        base_url = f"https://www.youtube.com/@{identifier}"
        
    streams_url = f"{base_url}/streams"
    
    ydl_opts = {
        'extract_flat': True,
        'skip_download': True,
        'quiet': True,
        'socket_timeout': 15,
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'ios', 'web']
            }
        }
    }
    
    target_video_url = None
    try:
        with YoutubeDL(ydl_opts) as ydl:
            # Try fetching from /streams first, fallback to main page
            for target_page in [streams_url, base_url]:
                print(f"Inspecting channel page: {target_page}")
                try:
                    info = ydl.extract_info(target_page, download=False)
                    entries = info.get('entries', [])
                    
                    # Look for active live stream
                    for entry in entries:
                        if not entry:
                            continue
                        live_status = entry.get('live_status')
                        title = entry.get('title', '')
                        vid_id = entry.get('id')
                        
                        if live_status == 'is_live' or 'LIVE' in title.upper():
                            target_video_url = f"https://www.youtube.com/watch?v={vid_id}"
                            print(f"Found live broadcast: {title} ({target_video_url})")
                            break
                    
                    # If no explicit live status found, take the latest entry as fallback
                    if not target_video_url and entries:
                        vid_id = entries[0].get('id')
                        if vid_id:
                            target_video_url = f"https://www.youtube.com/watch?v={vid_id}"
                            print(f"Using latest channel video as fallback: {target_video_url}")
                            break
                except Exception as page_e:
                    print(f"Failed to parse {target_page}: {page_e}")
                    continue
                    
    except Exception as e:
        print(f"Channel inspection error for {identifier}: {e}")

    # If we found a target video, extract the playable stream URL
    if target_video_url:
        stream_opts = {
            'format': 'best',
            'skip_download': True,
            'quiet': True,
            'socket_timeout': 15,
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'ios', 'web']
                }
            }
        }
        try:
            with YoutubeDL(stream_opts) as sydl:
                print(f"Extracting playable stream from: {target_video_url}")
                s_info = sydl.extract_info(target_video_url, download=False)
                return s_info.get('url')
        except Exception as stream_e:
            print(f"Stream extraction error: {stream_e}")
            
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
        print(f"Processing channel: {name}...")
        stream_url = get_channel_live_url(data["identifier"])
        
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

if __name__ == "__main__":
    main()
