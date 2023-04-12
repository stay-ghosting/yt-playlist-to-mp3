import os
import pytube
from pytube import exceptions
from typing import Tuple, Callable
import time
import subprocess
import tempfile
from threading import Thread
from multiThread import *
import shutil
from oneFunctionThead import OneFunctionThread

from threadQueue import ThreadQueue


class Ripper:
    def __init__(self, dir: str, playlist_url: str):
        self.dir = dir
        self.playlist = pytube.Playlist(playlist_url)
        self.files_to_download: list[pytube.YouTube] = []
        self.files_in_folder: list[pytube.YouTube] = []
        self.files_age_restricted: list[pytube.YouTube] = []
        self.unaccessable_videos: list[pytube.YouTube] = []
        self.files_downloaded: list[pytube.YouTube] = []
        self.stop = False

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

    def stop_download(self):
        self.stop = True

    def video_id_in_list(self, video_url: str, files_names: list[str]):
        """Returns True if video id exists in list
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

    def get_values_for_callback_download(self, song: pytube.YouTube, is_finished: bool):
        # amount of files downloaded
        items_completed = len(self.files_downloaded)
        # files downloaded + files able to download
        amount_of_items = len(self.files_to_download) - len(self.unaccessable_videos)
        # if song not given ...
        if song is None:
            # return without song
            return (items_completed, amount_of_items, "", is_finished)
        # try get title
        try:
            title = song.title
        # if error ...
        except exceptions.PytubeError:
            # set title to empty string
            title = ""
        # return values to use
        return (items_completed, amount_of_items, title, is_finished)

    def get_values_for_callback_load(self, song: pytube.YouTube, is_finished: bool):
        # get amount of videos in total that can be downloaded
        total_videos = (
            len(self.playlist.videos)
            - len(self.files_in_folder)
            - len(self.files_age_restricted)
        )
        # amount of videos loaded already
        amount_loaded = len(self.files_to_download)
        # if song not given ...
        if song is None:
            # return values to use
            return (amount_loaded, total_videos, "", is_finished)
        # try get title
        try:
            title = song.title
        # if error ...
        except exceptions.PytubeError:
            title = ""
        # return values to use
        return (amount_loaded, total_videos, title, is_finished)

    # 1671.7863901999954 seconds
    def download_all_audio(
        self,
        on_complete_callback: Callable[[int, int, str], any],
        on_progress_callback: Callable[[int, int, str], any],
        on_done_callback,
    ):
        """Gets list of YouTube objects and coverts them to mp3.
        Also adds video id at the end of the title"""
        start_time = time.perf_counter()
        self.stop = False
        self.filter_playlist(on_progress_callback)
        # if stop button pressed ...
        if self.stop == True:
            # stop script
            self.stop = False
            return
        # reset variables
        self.files_downloaded = []
        self.unaccessable_videos = []
        temp_dir = os.path.join(tempfile.gettempdir(), "ripper")
        # create thread objects
        multi_thread = MultiThread()
        callback_thread = OneFunctionThread()
        # for each video ...
        for i, video in enumerate(self.files_to_download):
            def download():
                # if stop button pressed ...
                if self.stop == True:
                    # stop script
                    return
                # call callback
                callback_thread.set_function(lambda:on_complete_callback(*self.get_values_for_callback_download(video, False)))
                # register callback to when file finishes downloading
                try:
                    # try create an audio stream
                    audio = video.streams.filter(only_audio=True).first()
                except KeyError:
                    # if error ...
                    # increment value
                    self.unaccessable_videos.append(video)
                    # call callback
                    callback_thread.set_function(lambda:on_complete_callback(*self.get_values_for_callback_download(video, False)))
                    # skip to next video
                    return
                else:
                    # download the file
                    audio.download(temp_dir)
                    # get the path
                    original_file_path = os.path.join(temp_dir, audio.default_filename)
                    # filename without extention
                    filename = audio.default_filename.removesuffix(".mp4")
                    # creates new file name
                    new_file_path = f"{self.dir}/{filename} [{video.video_id}].mp3"
                    # convert to mp3
                    subprocess.run(["ffmpeg", "-i", original_file_path, new_file_path])
                    # delete original file
                    os.remove(original_file_path)
                    # add to list of files downloded
                    self.files_downloaded.append(video)
                    # call callback function
                    callback_thread.set_function(lambda:on_complete_callback(*self.get_values_for_callback_download(video, False)))
            # add download to thread
            multi_thread.add(download)

        # wait for all downloads to finish
        while multi_thread.is_alive(): 
            continue

        # remove temp file
        try:
            shutil.rmtree(temp_dir)
        except FileNotFoundError:
            pass

        # stop script stop is True
        if self.stop == True:
            self.stop = False
            return

        # call callbacks
        on_complete_callback(*self.get_values_for_callback_download(None, True))
        on_done_callback(self)

        end_time = time.perf_counter()
        print(end_time - start_time)

    def filter_playlist(
        self, on_progress_callback: Callable[[int, int], any]
    ) -> Tuple[pytube.YouTube, pytube.YouTube]:
        """Filters playlist into:
        a playlist of already in directory songs
        and playlist of other songs"""

        # names of every file in directory
        filesNames = [
            f for f in os.listdir(self.dir) if os.path.isfile(os.path.join(self.dir, f))
        ]
        # create thread objects
        multi_thread = MultiThread()
        callback_thread = OneFunctionThread()

        # for video in playlist ...
        for i, video in enumerate(self.playlist.videos):
            def filter():
                if self.stop == True:
                    return
                # call callback
                callback_thread.set_function(lambda:on_progress_callback(*self.get_values_for_callback_load(video, False)))
                # if in directory
                file_exists = self.video_id_in_list(video.watch_url, filesNames)
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
                # call callback
                callback_thread.set_function(lambda:on_progress_callback(*self.get_values_for_callback_load(video, False)))
            multi_thread.add(filter)
        # wait fot filtering to finish
        while multi_thread.is_alive(): 
            continue
        # call callback
        callback_thread.set_function(lambda:on_progress_callback(*self.get_values_for_callback_load(None, True)))


# url = 'https://www.youtube.com/playlist?list=PLo80Q9Yj8XHfHtCXfrp81qRw5-PtLP-TG'
# dir = "D:/ribby/Documents/Work/python/ripper/songs"

# files_in_folder, files_to_download = filter_playlist(url, dir)
# download_audio(files_to_download, dir)
