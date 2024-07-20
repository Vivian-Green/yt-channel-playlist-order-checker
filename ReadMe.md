# YouTube Playlist Checker

Python program to check the order of videos in YouTube series playlists. uses tools yt-dlp and pytube to fetch playlist data & fetch video titles

Vid of it running (slightly dated):
[![Watch the video](https://img.youtube.com/vi/l_Z6s7eh3QU/maxresdefault.jpg)](https://www.youtube.com/watch?v=l_Z6s7eh3QU)



## Features

- **Fetching Playlists**: Retrieves all playlists from a given YouTube channel URL.
- **Caching Mechanism**: Memoizes playlist and title data to optimize performance and avoid unnecessary API calls.
- **Multi-threaded Processing**: Utilizes threads to concurrently fetch video titles and check their order within playlists.
- **Dynamic Progress Updates**: Displays progress bars and ETA for overall progress and individual playlist progress.
- **Color-coded Output**: Outputs results in color-coded format for easy readability:
  - Green for expected part numbers.
  - Orange for titles containing "finale".
  - Yellow for titles missing expected part numbers.
  - Red for potentially incorrect part numbers.


- Video links from each playlist are cached for quick access and reduced API calls in future runs.

## Setup and Requirements

### Prerequisites

- **Python 3**: [python.org](https://www.python.org/downloads/).


- **Install Required Packages**:
   - Windows users: run `install_youtube_tools.bat`
   - This script will install `pytube3` and `yt-dlp` using `pip`
   - Alternatively, just do these two:
	 ```
	 pip install pytube3
	 pip install yt-dlp
	 ```

### Usage
   - Paste in a channel url and press enter

## Additional Notes
   - you may want to invalidate your cache to check playlists that were incomplete since the last check.
