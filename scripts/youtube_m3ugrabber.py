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
                        slug = re.sub(r'[^a-z0-9]+', '_', name.lower()).strip('_')
                        channels[name] = {
                            "query": query_term,
                            "file": f"channels/{slug}.m3u",
                            "group": group
                        }

    with ThreadPoolExecutor(max_workers=6) as executor:
        executor.map(process_channel, channels.items())

    # Combine all individual channel m3u files into a single root youtube.m3u file
    master_lines = ["#EXTM3U"]
    for name, data in channels.items():
        if os.path.exists(data["file"]):
            with open(data["file"], 'r', encoding='utf-8') as f:
                for line in f:
                    line_str = line.strip()
                    if line_str and line_str != "#EXTM3U":
                        master_lines.append(line_str)

    with open("youtube.m3u", 'w', encoding='utf-8') as f:
        f.write("\n".join(master_lines) + "\n")

    print("All channel playlists generated successfully!")

if __name__ == "__main__":
    main()
