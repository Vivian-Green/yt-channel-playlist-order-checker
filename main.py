import subprocess
import re
import os
import json
import threading
import time
import math
from pytube import YouTube, Playlist

# copy pasted from YoinkYt common.py Jul 19 2024


THREAD_MAX = 50
# Prompt the user for input
thread_max_input = input(f"Enter max threads (default is {THREAD_MAX}): ")

# Check if the user provided input
if thread_max_input.strip():  # Check if input is not empty after stripping whitespace
    try:
        THREAD_MAX = int(thread_max_input)
        if THREAD_MAX <= 0:
            raise ValueError("THREAD_MAX must be a positive integer")
    except ValueError as e:
        print(f"Error: {e}. Using default value of {THREAD_MAX}")

print(f"THREAD_MAX set to: {THREAD_MAX}")


TRUST_CACHE = not input("Trust cache? (Skip re-checking playlists for changes. Default: Y)").strip().lower().startswith("n")

# Constants
CACHE_PATH = "cache.json"
FONT_PATH = "/Windows/Fonts/heygorgeous.ttf"
BIT_RATE = "10000k"
DIR_PATH = os.path.dirname(os.path.realpath(__file__))

# Global variables
cache_data = {}  # This will store our cached data

# Function to load cache data from file
def load_cache():
    global cache_data
    if os.path.exists(CACHE_PATH):
        with open(CACHE_PATH, 'r') as f:
            cache_data = json.load(f)

# Load cache data when script starts
load_cache()

def video_title_is_cached(video_url):
    return extract_video_id(video_url) in cache_data

def playlist_links_are_cached(playlist_url):
    return playlist_url in cache_data

# Function to fetch title from YouTube
youtube_title_fetch_count = 0
last_save_time = time.time()
def fetch_title(video_url):
    global cache_data
    global youtube_title_fetch_count
    global last_save_time
    global cache_locked
    video_id = extract_video_id(video_url)
    
    if cache_locked == True:
        time.sleep(0.5)
        
    if video_id in cache_data:
        #print(f"Fetching title from cache for {video_url}")
        #print(f" {cache_data[video_id]}")
        return cache_data[video_id]
    
    #print("\\rFetching title from YouTube...")
    
    title = ""
    try:
        youtube = YouTube(video_url)
        title = youtube.title
    except:
        title = "err fetching title, probably a private video"
        
    youtube_title_fetch_count += 1
    cache_data[video_id] = title
    #print(f" {cache_data[video_id]}")
    autosave(1)
    
    return title

cache_locked = False
def autosave(interval):
    global last_save_time
    global cache_data
    global CACHE_PATH
    global cache_locked
    if time.time() - last_save_time > interval:
        if not cache_locked:
            try:
                cache_locked = True
                last_save_time = time.time()
                with open(CACHE_PATH, 'w') as f:
                    json.dump(cache_data, f, indent=4)
                cache_locked = False
            except:
                i = 0
                while cache_locked and i < 40: # 2 seconds
                    time.sleep(0.05)
                    i += 1
                cache_locked = False
                autosave(-1)


# Function to extract video ID from YouTube URL
def extract_video_id(video_url):
    return video_url.split('?v=')[-1]
   
def extract_playlist_id(playlist_url):
    return playlist_url.split('?list=')[-1]

youtube_playlist_links_fetch_count = 0
def get_playlist_links(playlist_url):
    global cache_data

    # Check if playlist URL is already memoized
    if playlist_url in cache_data:
        #print(f"Fetching playlist links from cache for {playlist_url}")
        return cache_data[playlist_url]

    #print("Fetching playlist links from YouTube...")
    
    playlist = Playlist(playlist_url)
    links = list(playlist.video_urls)

    # Cache the fetched links
    cache_data[playlist_url] = links
    autosave(1)
        
    return links
    
def dump_cache():
    global CACHE_PATH
    global cache_data
    with open(CACHE_PATH, 'w') as f:
        json.dump(cache_data, f, indent=4)

# Function to sanitize title
def sanitize_title(title):
    title = re.sub(r'[\\/*?:%#<>|]', '', title).strip()
    title = title.replace("'", "").replace('"', "").replace(" ", "_")
    title = title.replace("__", "-").replace("_-_", "-")
    title = title[-60:]
    title = re.sub('^[^a-zA-Z]*', '', title)
    return title
































CACHE_FILE = "playlist-validity-cache.json"


RED = '\033[91m'
ENDC = '\033[0m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
ORANGE = '\033[33m'


# Load memoized data from file
def load_memoized_data():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                print(f"Warning: Could not decode JSON from {CACHE_FILE}. The file might be empty or corrupted.")
                return {}
    else:
        return {}


# Save memoized data to file
def save_memoized_data(data):
    with open(CACHE_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# Global variable to store our memoized data
memoized_data = load_memoized_data()

def fetch_channel_playlists(channel_url):
    command = ['yt-dlp', '--flat-playlist', '--get-id', '--', channel_url+"/playlists"]
    print(f"Running command: {' '.join(command)}")  # Debug print

    try:
        playlist_ids = subprocess.run(command, check=True, capture_output=True, text=True).stdout.splitlines()
        print(f"Playlist IDs: {playlist_ids}")  # Debug print
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        playlist_ids = []

    playlist_links = [f"https://www.youtube.com/playlist?list={playlist_id}" for playlist_id in playlist_ids]
    print(f"Generated playlist links: {playlist_links}")  # Debug print

    return playlist_links

def sanitize_channel_url(url):
    # Find the position of '@'
    at_pos = url.find('@')
    if at_pos == -1:
        return url

    # Find the position of the first '/' after '@'
    slash_pos = url.find('/', at_pos)
    if slash_pos == -1:
        return url

    # Return the substring from the start to the first '/' after '@'
    return url[:slash_pos]


def fetch_and_check(i, link, expected_part_number, offset, results, playlist_link):
    global threadCount
    threadCount += 1
    expected_part_number += offset
    title = fetch_title(link)
    match = re.search(r'(Part|Section|Day|Episode|Ep|\||#) (\d{1,3})', title, re.IGNORECASE)
    
    if not match:
        match = re.search(r'(#|Ep)(\d{1,3})', title, re.IGNORECASE)
        
    global playlist_titles_fetched
    global total_titles_fetched
    global delta
    total_titles_fetched += 1
    playlist_titles_fetched += 1
    
    bad_color = RED
    if "finale" in title.lower():
        bad_color = ORANGE
    
    if match:
        part_number = int(match.group(2))
        if part_number != expected_part_number:
            results[i] = f"{bad_color}Expected Part {expected_part_number}, actual {title}{ENDC}               diff: {expected_part_number - part_number}                    {playlist_link}"
            offset = expected_part_number - part_number
        else:
            results[i] = f"{GREEN}Part {expected_part_number} is correct: {title}{ENDC} "
    else:
        if "finale" in title.lower():
            results[i] = f"{YELLOW}No 'Part ###', 'Section ###' or 'Day ###' found: {title}{ENDC} "
        else:
            results[i] = f"{ORANGE}No 'Part ###', 'Section ###' or 'Day ###' found: {title}{ENDC}                    {playlist_link}"

        
    global playlist_length
    global videos_to_fetch
    progress_percentage = round(playlist_titles_fetched / playlist_length * 100)
    eta_seconds = round(delta * (playlist_length - playlist_titles_fetched))

    # Calculate total ETA in minutes, and seconds
    minutes = eta_seconds // 60
    seconds = eta_seconds % 60

    # Calculate total ETA in hours, minutes, and seconds
    progress_percentage2 = round(total_titles_fetched / videos_to_fetch * 100)
    total_eta_seconds = round(delta * (videos_to_fetch - total_titles_fetched))
    hours2 = total_eta_seconds // 3600
    minutes2 = (total_eta_seconds % 3600) // 60
    seconds2 = total_eta_seconds % 60

    # Print the updated message including total ETA
    progress_bar = "|" * math.floor(progress_percentage * 0.5) + "." * (50 - math.floor(progress_percentage * 0.5))
    progress_bar2 = "|" * math.floor(progress_percentage2 * 0.5) + "." * (50 - math.floor(progress_percentage2 * 0.5))
    print(f"    [{progress_bar2}] {math.floor(total_titles_fetched/videos_to_fetch * 100)}% total ETA: {hours2}h {minutes2}m {seconds2}s \ttotal titles: {total_titles_fetched}/{videos_to_fetch}\t\t[{progress_bar}] got title {playlist_titles_fetched}/{playlist_length} {progress_percentage}% ETA: {minutes}m {seconds}s", end='\r', flush=True)
    threadCount -= 1

playlist_titles_fetched = 0
playlist_length = 0
total_titles_fetched = 0
threadCount = 0
def check_playlist_order(playlist_url):
    global playlist_titles_fetched
    global playlist_length
    playlist_titles_fetched = 0
    links = get_playlist_links(playlist_url)
    expected_part_number = 1
    offset = 0
    results = [""] * len(links)

    threads = []
    playlist_length = len(links)
    for i, link in enumerate(links):
        if not video_title_is_cached(link):
            if threadCount >= THREAD_MAX:
                delay_ticks = 0
                while threadCount >= THREAD_MAX:
                    time.sleep(0.1)
                    delay_ticks += 1
                    if delay_ticks % 20 == 0:
                        print(".")
            else:
                time.sleep(0.1)
        thread = threading.Thread(target=fetch_and_check, args=(i, link, expected_part_number, offset, results, playlist_url))
        thread.start()
        threads.append(thread)
        expected_part_number += 1

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    return results




def check_and_update_playlists_cache():
    global cache_data
    global TRUST_CACHE
    
    if not TRUST_CACHE:
        print("\nChecking and updating playlists cache...")

        for playlist_url in cache_data.keys():
            try:
                current_playlist_links = get_playlist_links(playlist_url)
                cached_links = cache_data[playlist_url]

                if set(current_playlist_links) != set(cached_links):
                    print(f"Playlist {playlist_url} has changes. Updating cache...")

                    cache_data[playlist_url] = current_playlist_links
                    autosave(1)
            except Exception as e:
                print(f"Error checking playlist {playlist_url}: {e}")

        print("Playlist cache update complete.")




































channel_url = sanitize_channel_url(input("Please enter the YouTube channel URL: "))

# Check if '@' symbol is present in the sanitized channel_url
if channel_url.find("@") == -1:
    # If no '@' symbol, check if there's a cached last_channel_url
    if "last_channel_url" in cache_data:
        channel_url = cache_data["last_channel_url"]
else:
    # If '@' symbol is present, update cache_data with this channel_url
    cache_data["last_channel_url"] = channel_url

# Fetch the playlists from the channel
playlists = fetch_channel_playlists(channel_url)

videos_to_fetch = 0
processed_playlists = 0
threads = []
links = []
def fetch_links(playlist):
    global videos_to_fetch
    global processed_playlists
    this_links = get_playlist_links(playlist)
    links.extend(this_links)
    videos_to_fetch += len(this_links)
    processed_playlists += 1
    print(f"Caching video links from playlist {processed_playlists}/{len(playlists)}. Total videos: {videos_to_fetch}", end='\r', flush=True)
    #print(f"Fetched {len(this_links)} links from {playlist}")

# Create threads for fetching links from each playlist
print()
for playlist in playlists:
    if not playlist_links_are_cached(playlist):
        time.sleep(0.025)
    time.sleep(0.001)
    thread = threading.Thread(target=fetch_links, args=(playlist,))
    threads.append(thread)
    thread.start()
    

# Wait for all threads to complete
for thread in threads:
    thread.join()
dump_cache()

check_and_update_playlists_cache() # if not trusted
autosave(-1)



log_dict = {}
delta = 1
modifying_delta = 0
for playlist in playlists:
    print(f"\nChecking order of playlist: {playlist}")
    start_time = time.time()
    results = check_playlist_order(playlist)
    this_delta = (time.time() - start_time) / len(results)
    if this_delta > 0.02: # 20ms is way faster than this should possibly take-
        delta *= modifying_delta
        modifying_delta += 1
        delta += this_delta
        delta /= modifying_delta
    playlist_id = extract_playlist_id(playlist)
    log_dict[playlist_id] = results


last_diff = 0  # Initialize last_diff outside the loop if needed
for playlist_id, results in log_dict.items():
    print(f"\nResults for playlist {playlist_id}:")
    last_diff = None  # Reset last_diff for each playlist
    time.sleep(0.2)
    for result in results:
        if result.startswith(RED):
            match = re.search(r'diff: (-?\d+)', result)
            if match:
                current_diff = int(match.group(1))
                if current_diff == last_diff:
                    # If the current difference matches the last one, change RED to YELLOW
                    result = result.replace(RED, YELLOW)
                    # Trim the string after "diff:"
                    diff_index = result.find("diff:")
                    if diff_index != -1:
                        result = result[:diff_index]
                last_diff = current_diff
            else:
                last_diff = None

        print(result)




while True:
    time.sleep(1)