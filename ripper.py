from tkinter import *
from threading import Thread
from pyyoutube import Api
import sys
import os

# https://www.youtube.com/playlist?list=PLo80Q9Yj8XHfHtCXfrp81qRw5-PtLP-TG
# youtube-dl -x --audio-format mp3 <url>

API_KEY = os.getenv("API_KEY")

def get_playlist_id():
    # the get id/url of the playlist
    playlist_input = sys.argv[1]
    # the start of url
    playlist_prefix = "https://www.youtube.com/playlist?list="
    # remove prefix from input and return
    return playlist_input.strip(playlist_prefix)


def get_urls(playlist_id: str) -> list[str]:
    # create api object
    api = Api(api_key=API_KEY)
    # get the dictionary of items
    playlist_items = api.get_playlist_items(playlist_id=playlist_id, count=None, return_json=True)
    # list of all videos
    playlist = []
    # for each item ...
    for playlist_item in playlist_items['items']:
        # get url
        video_prefix = "https://www.youtube.com/watch?v="
        video_id = playlist_item['contentDetails']['videoId']
        video_url = video_prefix + video_id
        # add video url to playlist
        playlist.append(video_url)

    return playlist

def file_exists_in_folder(url: str):
    # get the title
    video_id = url.split("=")[1]
    video_id_formatted = f"[{video_id}]"
    # get names of every file in cwd
    filesNames = [f for f in os.listdir('.') if os.path.isfile(f)]
    # for each file ...
    for fileName in filesNames:
        # if file found in cwd ...
        if video_id_formatted in fileName:
            print(f"file already exists   id:{video_id}   title:{fileName}")
            # return true
            return True
    # if not found
    else:
        # return false
        return False
  
def download_audio(url: str):
    file_exists = file_exists_in_folder(url)
    # if file NOT in folder ...
    if not file_exists:
        # download the file
        os.system(f"yt-dlp -x --audio-format mp3 {url}")
        
playlist_id = get_playlist_id()
urls = get_urls(playlist_id)
for url in urls:
    download_audio(url)
print(urls)

# threading()