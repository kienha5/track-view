import csv
import os
import re
from datetime import datetime, timezone, timedelta
import requests
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# --- CONFIGURATION ---
API_KEY = os.environ.get("YOUTUBE_API_KEY")

# Add as many 11-character video IDs to this list as you want!
VIDEO_IDS = [
    "T24rF_x0TmQ",
    "XKZIQlqVjjk",
    #"YOUR_VIDEO_ID_3"
]

def sanitize_filename(name):
    """Removes invalid characters to safely create folder names."""
    return re.sub(r'[\\/*?:"<>|]', "", name).strip()

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
            reader = list(csv.reader(file))
            if len(reader) > 1: 
                return int(reader[-1][2])
    except Exception as e:
        print(f"Error reading {csv_file}: {e}")
    return None

def update_chart(csv_file, folder_path, video_title):
    """Generates a line chart from the CSV data and saves it as an image."""
    timestamps = []
    views = []
    
    try:
        with open(csv_file, mode="r", encoding="utf-8") as file:
            reader = csv.reader(file)
            next(reader, None)  # Skip the header row
            for row in reader:
                if len(row) >= 3:
                    timestamps.append(datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S"))
                    views.append(int(row[2]))
    except Exception as e:
        print(f"Error reading CSV for chart: {e}")
        return

    if not timestamps:
        return

    # Plotting the data
    plt.figure(figsize=(10, 6))
    plt.plot(timestamps, views, marker='o', linestyle='-', color='b', markersize=4)
    plt.title(f"View Tracking: {video_title}")
    plt.xlabel("Time (ICT)")
    plt.ylabel("Total Views")
    plt.grid(True, linestyle='--', alpha=0.7)
    
    # Format x-axis to show dates nicely without crowding
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
    plt.gcf().autofmt_xdate() # Auto-rotate the x-axis labels
    
    # Save the plot inside the specific folder
    chart_path = os.path.join(folder_path, "view_chart.png")
    plt.savefig(chart_path, bbox_inches="tight", dpi=150)
    plt.close()
    print(f"Chart updated and saved to: {chart_path}")

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
            # --- FOLDER CREATION ---
            safe_title = sanitize_filename(title)
            folder_path = safe_title
            
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
                
            csv_file = os.path.join(folder_path, f"youtube_views_{video_id}.csv")
            file_exists = os.path.isfile(csv_file)

            # --- CALCULATE GAIN ---
            last_views = get_last_view_count(csv_file)
            if last_views is not None:
                view_gain = views - last_views
            else:
                view_gain = 0 

            # --- WRITE TO CSV ---
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
                print(f"Already logged at {current_time}, skipping CSV write.")

            # --- DRAW AND SAVE CHART ---
            # We always update the chart if a new row was added
            if not already_logged or not os.path.exists(os.path.join(folder_path, "view_chart.png")):
                update_chart(csv_file, folder_path, title)

if __name__ == "__main__":
    log_views_to_csv()
