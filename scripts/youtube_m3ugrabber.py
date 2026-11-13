import os
from yt_dlp import YoutubeDL

def get_live_stream_url(youtube_url):
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'skip_download': True,
        'extract_flat': False,
    }
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=False)
            
            # If the link points to a channel/playlist page, extract the active live entry
            if 'entries' in info and info['entries']:
                entry = info['entries'][0]
                info = ydl.extract_info(entry['url'], download=False)
                
            stream_url = info.get('url')
            return stream_url
    except Exception as e:
        print(f"Error extracting stream for {youtube_url}: {e}")
        return None

def generate_m3u_file(channel_name, youtube_url, output_path):
    stream_url = get_live_stream_url(youtube_url)
    if not stream_url:
        print(f"Failed to fetch valid stream URL for {channel_name}")
        return

    # Generate the standard M3U structure
    m3u_content = f"""#EXTM3U
#EXTINF:-1 group-title="Malayalam News" tvg-logo="" tvg-id="", {channel_name}
{stream_url}
"""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(m3u_content)
    print(f"Successfully generated M3U for {channel_name}")

if __name__ == "__main__":
    # Point this to your target YouTube live stream or channel live page
    channel = "Kannur Vision News 24x7"
    yt_url = "https://www.youtube.com/@KannurVisionNews/live"  
    output_file = "channels/kannur_vision_news_24x7.m3u"
    
    generate_m3u_file(channel, yt_url, output_file)
