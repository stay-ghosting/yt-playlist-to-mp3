from copy import deepcopy
import os
import pytube
from pytube import exceptions
from typing import Tuple, Callable
import subprocess
import tempfile
import shutil
from threadQueue import ThreadQueue
from threading import Lock
from concurrent.futures import ThreadPoolExecutor, as_completed

# show songs you already have in logs

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
        self.debug_load_times = []
        self.lock = Lock()

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

    def video_id_in_list(self, video: pytube.YouTube, files_names: set[str]):
        """Returns True if video id exists in list
        by checking for video id at the end of the file name"""

        video_id = video.video_id
        video_id_formatted = f"[{video_id}]"

        for fileName in files_names:
            if fileName.endswith(video_id_formatted):
                return True

        return False


        

    def get_values_for_callback_download(self, song: pytube.YouTube, is_finished: bool):
        items_completed = len(self.files_downloaded)
        amount_of_items = len(self.files_to_download) - len(self.unaccessable_videos)
        if song is None:
            return (items_completed, amount_of_items, "", is_finished)
        try:
            title = song.title
        except exceptions.PytubeError:
            title = ""
        return (items_completed, amount_of_items, title, is_finished)

    def get_values_for_callback_load(self, song: pytube.YouTube, is_finished: bool):
        total_videos = (
            len(self.playlist.videos)
            - len(self.files_in_folder)
            - len(self.files_age_restricted)
        )
        amount_loaded = len(self.files_to_download)
        if song is None:
            return (amount_loaded, total_videos, "", is_finished)
        try:
            title = song.title
        except exceptions.PytubeError:
            title = ""
        return (amount_loaded, total_videos, title, is_finished)

    def download_all_audio(
        self,
        on_complete_callback: Callable[[int, int, str], any],
        on_progress_callback: Callable[[int, int, str], any],
        on_done_callback,
    ):
        """Gets list of YouTube objects and coverts them to mp3.
        Also adds video id at the end of the title"""
        self.stop = False
        self.filter_playlist(on_progress_callback)
        if self.stop == True:
            self.stop = False
            return
        
        self.files_downloaded = []
        self.unaccessable_videos = []
        temp_dir = os.path.join(tempfile.gettempdir(), "ripper")

        try:
            shutil.rmtree(temp_dir)
        except Exception:
            pass

        for i, video in enumerate(self.files_to_download):
            if self.stop == True:
                self.stop = False
                return
            on_complete_callback(*self.get_values_for_callback_download(video, False))
            try:
                audio = video.streams.filter(only_audio=True).first()
            except KeyError:
                self.unaccessable_videos.append(video)
                continue
            else:
                audio.download(temp_dir)
                original_file_path = os.path.join(temp_dir, audio.default_filename)
                filename = audio.default_filename.removesuffix(".mp4")
                new_file_path = f"{self.dir}/{filename} [{video.video_id}].mp3"
                subprocess.run(["ffmpeg", "-nostdin", "-i", original_file_path, new_file_path])
                try:
                    os.remove(original_file_path)
                except Exception:
                    pass
                self.files_downloaded.append(video)
                is_last_video = i == len(self.files_to_download) - 1
                if is_last_video:
                    on_complete_callback(*self.get_values_for_callback_download(video, False))
                
        try:
            shutil.rmtree(temp_dir)
        except Exception:
            pass

        on_complete_callback(*self.get_values_for_callback_download(None, True))
        on_done_callback(self)


    def filter_playlist(self, on_progress_callback: Callable[[int, int], any]) -> Tuple[pytube.YouTube, pytube.YouTube]:
        filesNames = {
            f for f in os.listdir(self.dir) if os.path.isfile(os.path.join(self.dir, f))
        }

        def process_video(video):
            values = self.get_values_for_callback_load(video, False)
            on_progress_callback(*values)
            file_exists = self.video_id_in_list(video, filesNames)
            if file_exists:
                self.files_in_folder.append(video)
            elif video.age_restricted:
                self.files_age_restricted.append(video)
            else:
                self.files_to_download.append(video)

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(process_video, video) for video in self.playlist.videos]

            for future in as_completed(futures):
                pass

        on_progress_callback(*self.get_values_for_callback_load(None, True))


# url = 'https://www.youtube.com/playlist?list=PLo80Q9Yj8XHfHtCXfrp81qRw5-PtLP-TG'
# dir = "D:/ribby/Documents/Work/python/ripper/songs"

# files_in_folder, files_to_download = filter_playlist(url, dir)
# download_audio(files_to_download, dir)
