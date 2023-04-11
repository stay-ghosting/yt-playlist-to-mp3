import os
import pytube
from typing import Tuple, Callable
import asyncio
import time
import re
from threadWithReturn import ThreadWithReturnValue

class Ripper:
    def __init__(self, dir: str, playlist_url: str):
        self.dir = dir
        self.playlist = pytube.Playlist(playlist_url)
        self.files_to_download : list[pytube.YouTube] = []
        self.files_in_folder : list[pytube.YouTube] = []
    
    def file_exists_in_folder(self, video_url: str, files_names: list[str]):
        """Returns True if file exists in folder 
        by checking for video id in the title"""

        # get video ID
        video = pytube.YouTube(video_url)
        video_id = video.video_id
        video_id_formatted = f"[{video_id}]"
        
        # for each file ...
        for fileName in files_names:
            # if file found in directory ...
            if video_id_formatted in fileName:
                print(f"file already exists   id:{video_id}   title:{fileName}")
                # return true
                return True
        # if not found ...
        else:
            print(f"video added: {video_id}")
            # return false
            return False
    
    def download_audio(self, on_complete_callback: Callable[[int, int], None]):
        """Gets list of YouTube objects and coverts them to mp3.
        Also adds video id at the end of the title"""
        # for each video ...
        for i, video in enumerate(self.files_to_download):
            files_downloaded = i + 1
            amount_of_files = len(self.files_to_download)
            video.register_on_complete_callback(lambda stream, file_path:
                                                on_complete_callback(files_downloaded, amount_of_files))
            try:
                # try create an audio stream
                audio = video.streams.filter(only_audio=True).first()
            except KeyError:
                # if error ... skip to next video
                continue
            else:
                # get video id
                video_id = video.watch_url.split("=")[1]
                # download the file
                out_file = audio.download(self.dir)
            

    def filter_playlist(self, on_progress_callback: Callable[[int, int], any]) -> Tuple[pytube.YouTube, pytube.YouTube]:
        """Filters playlist into:
        a playlist of already in directory songs
        and playlist of other songs """

        # names of every file in directory
        filesNames = [f for f in os.listdir(self.dir) 
                    if os.path.isfile(os.path.join(self.dir, f))]
        # for video in playlist ...
        for i, video in enumerate(self.playlist.videos):
            file_exists = self.file_exists_in_folder(video.watch_url, filesNames)
            on_progress_callback(i, len(self.playlist.videos))
            # if in directory or restricted video...
            if file_exists or video.age_restricted:
                # add to files in folder list
                self.files_in_folder.append(video)
            else:    
                # add to files to download list
                self.files_to_download.append(video)


# url = 'https://www.youtube.com/playlist?list=PLo80Q9Yj8XHfHtCXfrp81qRw5-PtLP-TG'
# dir = "D:/ribby/Documents/Work/python/ripper/songs"

# files_in_folder, files_to_download = filter_playlist(url, dir)
# download_audio(files_to_download, dir)