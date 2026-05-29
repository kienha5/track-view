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


def get_last_view_count(csv_file):
    """Reads the last row of the CSV to find the previous view count."""
    if not os.path.isfile(csv_file):
        return None
    try:
        with open(csv_file, mode="r", encoding="utf-8") as file:
            # Read the CSV and convert it into a list of rows
            reader = list(csv.reader(file))
            # If there is data beyond the header row
            if len(reader) > 1: 
                # The views are located in the 3rd column (index 2)
                return int(reader[-1][2])
    except Exception as e:
        print(f"Error reading {csv_file}: {e}")
    return None


def log_views_to_csv():
    if not API_KEY:
        print("Error: YOUTUBE_API_KEY environment variable is missing.")
        return

    ict_timezone = timezone(timedelta(hours=7))
    current_time = datetime.now(ict_timezone).strftime("%Y-%m-%d %H:%M:%S")

    for video_id in VIDEO_IDS:
        if "YOUR_VIDEO_ID" in video_id:
            continue

        title, views = get_video_data(video_id, API_KEY)

        if views is not None and title is not None:
            csv_file = f"youtube_views_{video_id}.csv"
            file_exists = os.path.isfile(csv_file)

            # --- NEW LOGIC: Calculate View Gain ---
            last_views = get_last_view_count(csv_file)
            
            if last_views is not None:
                view_gain = views - last_views
            else:
                view_gain = 0 # First ever entry

            # --- WRITE TO CSV ---
            # Check if this timestamp already exists in the CSV
            already_logged = False
            if os.path.isfile(csv_file):
                with open(csv_file, mode="r", encoding="utf-8") as f:
                    for row in csv.reader(f):
                        if row and row[0] == current_time:
                            already_logged = True
                            break
            
            if not already_logged:
                with open(csv_file, mode="a", newline="", encoding="utf-8") as file:
                    writer = csv.writer(file)
                    if not file_exists:
                        writer.writerow(["Timestamp", "Video Title", "Views", "View Gain"])
                    writer.writerow([current_time, title, views, view_gain])
                    print(f"Logged '{title}' at {current_time}: {views} views (+{view_gain})")
            else:
                print(f"Already logged at {current_time}, skipping.")

if __name__ == "__main__":
    log_views_to_csv()
