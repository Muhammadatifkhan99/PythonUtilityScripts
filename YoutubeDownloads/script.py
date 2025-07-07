import subprocess
import json
import os
import re

def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "_", name)

def get_playlist_title(playlist_url):
    try:
        result = subprocess.run(
            ["yt-dlp", "--flat-playlist", "-J", playlist_url],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        metadata = json.loads(result.stdout)
        return sanitize_filename(metadata.get("title", "YouTube_Playlist"))
    except Exception as e:
        print(f"⚠️ Failed to fetch playlist title: {e}")
        return "YouTube_Playlist"

def download_youtube_playlist(playlist_url):
    folder_name = get_playlist_title(playlist_url)
    output_dir = os.path.join("downloads", folder_name)

    os.makedirs(output_dir, exist_ok=True)

    command = [
        "yt-dlp",
        "-f", "best[height<=720]",
        "--yes-playlist",
        "--write-description",
        "--write-auto-sub",
        "--sub-lang", "en",
        "--convert-subs", "srt",
        "--external-downloader", "aria2c",
        "--external-downloader-args", "-x 16 -s 16 -k 1M",
        "-o", f"{output_dir}/%(playlist_index)s - %(title)s.%(ext)s",
        playlist_url
    ]

    print(f"📥 Downloading into: {output_dir}")
    try:
        subprocess.run(command, check=True)
        print("\n✅ Download complete.")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error during download: {e}")

if __name__ == "__main__":
    playlist_url = input("🔗 Enter YouTube playlist URL: ").strip()
    if playlist_url:
        download_youtube_playlist(playlist_url)
    else:
        print("❌ No URL provided.")
