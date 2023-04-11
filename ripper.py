import os
import pytube
from typing import Tuple, Callable
import asyncio
import time
import re

class Ripper:
    def __init__(self, dir: str, playlist_url: str):
        self.dir = dir
        self.playlist = pytube.Playlist(playlist_url)
        self.files_to_download : list[pytube.YouTube] = []
        self.files_in_folder : list[pytube.YouTube] = []
        self.files_age_restricted : list[pytube.YouTube] = []
        self.unaccessable_videos : list[pytube.YouTube] = []
        self.files_downloaded : list[pytube.YouTube] = []
    
    def is_valid_playlist(self):
        """True if playlist exists"""
        # try ... get length of playlist
        try:
            self.playlist.length
        # if NOT found ... return False
        except Exception:
            return False
        # if found ... return True
        else:
            return True
    
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
    
    def download_audio(self, 
                       on_complete_callback: Callable[[int, int], any],
                       on_progress_callback: Callable[[int, int], any],
                       on_done_callback):
        """Gets list of YouTube objects and coverts them to mp3.
        Also adds video id at the end of the title"""
        self.filter_playlist(on_progress_callback)
        # reset variables
        self.files_downloaded = []
        self.unaccessable_videos = []
        # for each video ...
        for i, video in enumerate(self.files_to_download):
            # amount of files to download
            amount_of_files = len(self.files_to_download)
            # register callback to when file finishes downloading
            video.register_on_complete_callback(lambda stream, file_path:
                                                on_complete_callback(len(self.files_downloaded) + 1, amount_of_files - len(self.unaccessable_videos)))
            try:
                # try create an audio stream
                audio = video.streams.filter(only_audio=True).first()
            except KeyError:
                # if error ... 
                # increment value
                self.unaccessable_videos.append(video)
                # skip to next video
                continue
            else:
                # get video id
                video_id = video.watch_url.split("=")[1]
                # download the file
                out_file = audio.download(self.dir)
                # add 1 to the amount of files downloded
                self.files_downloaded.append(video)

        on_done_callback(self)

    def filter_playlist(self, on_progress_callback: Callable[[int, int], any]) -> Tuple[pytube.YouTube, pytube.YouTube]:
        """Filters playlist into:
        a playlist of already in directory songs
        and playlist of other songs """

        # names of every file in directory
        filesNames = [f for f in os.listdir(self.dir) 
                    if os.path.isfile(os.path.join(self.dir, f))]
        # for video in playlist ...
        for i, video in enumerate(self.playlist.videos):
            # if in directory
            file_exists = self.file_exists_in_folder(video.watch_url, filesNames)
            # if in directory or restricted video...
            if file_exists:
                # add to files in folder list
                self.files_in_folder.append(video)
            # if file age restricted ...
            elif video.age_restricted:
                # add to age restricted list
                self.files_age_restricted.append(video)
            else:    
                # add to files to download list
                self.files_to_download.append(video)
            # get amount of videos in total that can be downloaded
            total_videos = len(self.playlist.videos) - len(self.files_in_folder) - len(self.files_age_restricted)
            # call callback function
            on_progress_callback(i, total_videos)


# url = 'https://www.youtube.com/playlist?list=PLo80Q9Yj8XHfHtCXfrp81qRw5-PtLP-TG'
# dir = "D:/ribby/Documents/Work/python/ripper/songs"

# files_in_folder, files_to_download = filter_playlist(url, dir)
# download_audio(files_to_download, dir)