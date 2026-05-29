import csv
import os
from datetime import datetime
import requests

# --- CONFIGURATION ---
# We now pull the API key from a secure environment variable
API_KEY = os.environ.get("AIzaSyBcno3v4pl5S3FP0KtBn6s8hKGkp5NVITc") 
VIDEO_ID = "T24rF_x0TmQ"  # Replace with your 11-character video ID
CSV_FILE = "youtube_views_history.csv"

def get_video_views(video_id, api_key):
    url = f"https://www.googleapis.com/youtube/v3/videos?part=statistics&id={video_id}&key={api_key}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        if "items" in data and len(data["items"]) > 0:
            return int(data["items"][0]["statistics"]["viewCount"])
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def log_views_to_csv():
    if not API_KEY:
        print("Error: YOUTUBE_API_KEY environment variable is missing.")
        return

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    views = get_video_views(VIDEO_ID, API_KEY)

    if views is not None:
        file_exists = os.path.isfile(CSV_FILE)
        
        with open(CSV_FILE, mode="a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(["Timestamp", "Views"])
            writer.writerow([current_time, views])
            
        print(f"Logged at {current_time}: {views} views")

if __name__ == "__main__":
    log_views_to_csv()