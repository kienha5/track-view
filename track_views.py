import csv
import os
from datetime import datetime, timezone, timedelta
import requests

# --- CONFIGURATION ---
API_KEY = os.environ.get("YOUTUBE_API_KEY")

# Add as many 11-character video IDs to this list as you want!
VIDEO_IDS = [
    "T24rF_x0TmQ"
    #"YOUR_VIDEO_ID_2",
    #"YOUR_VIDEO_ID_3"
]


def get_video_data(video_id, api_key):
    # We add 'snippet' to the part parameter to retrieve the video title
    url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics&id={video_id}&key={api_key}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if "items" in data and len(data["items"]) > 0:
            video_info = data["items"][0]
            title = video_info["snippet"]["title"]
            view_count = video_info["statistics"]["viewCount"]
            return title, int(view_count)
        else:
            print(f"Video {video_id} not found or stats unavailable.")
            return None, None
    except Exception as e:
        print(f"Error fetching data for {video_id}: {e}")
        return None, None


def log_views_to_csv():
    if not API_KEY:
        print("Error: YOUTUBE_API_KEY environment variable is missing.")
        return

    # Set up Vietnam local time (ICT / UTC+7)
    ict_timezone = timezone(timedelta(hours=7))
    current_time = datetime.now(ict_timezone).strftime("%Y-%m-%d %H:%M:%S")

    # Loop through every video ID provided in the list
    for video_id in VIDEO_IDS:
        # Skip placeholder values
        if "YOUR_VIDEO_ID" in video_id:
            continue

        title, views = get_video_data(video_id, API_KEY)

        if views is not None and title is not None:
            # Dynamically create a unique CSV filename for each video ID
            csv_file = f"youtube_views_{video_id}.csv"
            file_exists = os.path.isfile(csv_file)

            with open(csv_file, mode="a", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                
                # Write header including the Video Title column if file is new
                if not file_exists:
                    writer.writerow(["Timestamp", "Video Title", "Views"])
                
                writer.writerow([current_time, title, views])
                
            print(f"Logged '{title}' ({video_id}) at {current_time}: {views} views")


if __name__ == "__main__":
    log_views_to_csv()
