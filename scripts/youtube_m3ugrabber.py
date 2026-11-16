import os
import re
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from yt_dlp import YoutubeDL

# Put your other M3U playlist URL here (raw link)
EXTERNAL_M3U_URL = "http://m3u4u.com/m3u/5z3endj9qzupzkr4nqpk"

def fetch_external_playlist(url):
    """Downloads an external M3U playlist from a URL."""
    if not url or "example.com" in url:
        return []
    try:
        print(f"Fetching external playlist from: {url}")
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as response:
            content = response.read().decode('utf-8', errors='ignore')
            lines = []
            for line in content.splitlines():
                line_str = line.strip()
                # Skip header lines from the external file to avoid duplication
                if line_str and line_str != "#EXTM3U":
                    lines.append(line_str)
            return lines
    except Exception as e:
        print(f"Failed to fetch external playlist: {e}")
        return []

def process_channel(item):
    name, data = item
    raw_query = data['query']
    
    if raw_query.startswith("http"):
        query = raw_query
    elif raw_query.startswith("@"):
        query = f"https://www.youtube.com/{raw_query}/live"
    elif raw_query.startswith("UC"):
        query = f"https://www.youtube.com/channel/{raw_query}/live"
    else:
        query = f"https://www.youtube.com/@{raw_query.replace(' ', '')}/live"

    has_cookies = os.path.exists('cookies.txt')
    cookie_size = os.path.getsize('cookies.txt') if has_cookies else 0

    ydl_opts = {
        'quiet': False,
        'verbose': True,
        'skip_download': True,
        'socket_timeout': 20,
        'cookiefile': 'cookies.txt' if has_cookies and cookie_size > 0 else None,
        'extractor_args': {
            'youtube': {
                'player_client': ['web', 'android']
            }
        }
    }
    
    stream_url = None
    error_reason = "EXTRACTION FAILED OR CHANNEL OFFLINE"
    queries = [query, f"ytsearch1:{name} live"]

    with YoutubeDL(ydl_opts) as ydl:
        for q in queries:
            try:
                print(f"[{name}] Trying query/URL: {q}")
                info = ydl.extract_info(q, download=False)
                if not info:
                    continue
                
                entry = info['entries'][0] if ('entries' in info and info['entries']) else info
                stream_url = entry.get('url')
                
                if not stream_url and 'id' in entry:
                    vid_url = f"https://www.youtube.com/watch?v={entry.get('id')}"
                    sub_info = ydl.extract_info(vid_url, download=False)
                    if sub_info:
                        stream_url = sub_info.get('url')
                        if not stream_url and 'formats' in sub_info:
                            for f in reversed(sub_info.get('formats', [])):
                                if f.get('url'):
                                    stream_url = f.get('url')
                                    break
                elif not stream_url and 'formats' in entry:
                    for f in reversed(entry.get('formats', [])):
                        if f.get('url'):
                            stream_url = f.get('url')
                            break
                            
                if stream_url:
                    break
            except Exception as e:
                error_reason = str(e)
                print(f"[{name}] Failed with {q}: {e}")
                continue

    os.makedirs(os.path.dirname(data["file"]), exist_ok=True)
    if stream_url:
        content = f'#EXTM3U\n#EXTINF:-1 group-title="{data["group"]}" tvg-logo="" tvg-id="", {name}\n{stream_url}\n'
        print(f"[{name}] Success")
    else:
        content = f'#EXTM3U\n#EXTINF:-1 group-title="{data["group"]}" tvg-logo="" tvg-id="", {name}\n# ERROR: {error_reason}\n'
        print(f"[{name}] Wrote failure marker")

    with open(data["file"], 'w', encoding='utf-8') as f:
        f.write(content)

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
                        query_term = parts[1]
                        group = parts[2] if len(parts) > 2 else "Malayalam News"
                    elif len(parts) == 1:
                        name = parts[0]
                        query_term = name
                        group = "Malayalam News"
                    else:
                        continue
                    
                    slug = re.sub(r'[^a-z0-9]+', '_', name.lower()).strip('_')
                    channels[name] = {
                        "query": query_term,
                        "file": f"channels/{slug}.m3u",
                        "group": group
                    }

    # Run thread pool to update local YouTube channel files
    with ThreadPoolExecutor(max_workers=6) as executor:
        executor.map(process_channel, channels.items())

    # Build the combined master playlist
    master_lines = ["#EXTM3U"]
    
    # 1. Add generated YouTube channels
    for name, data in channels.items():
        if os.path.exists(data["file"]):
            with open(data["file"], 'r', encoding='utf-8') as f:
                for line in f:
                    line_str = line.strip()
                    if line_str and line_str != "#EXTM3U":
                        master_lines.append(line_str)

    # 2. Append external playlist lines if URL is provided
    external_lines = fetch_external_playlist(EXTERNAL_M3U_URL)
    if external_lines:
        master_lines.extend(external_lines)

    # Write out the final unified master playlist
    with open("youtube.m3u", 'w', encoding='utf-8') as f:
        f.write("\n".join(master_lines) + "\n")

    print("Master playlist successfully generated and merged!")

if __name__ == "__main__":
    main()
