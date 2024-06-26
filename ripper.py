from copy import deepcopy
import os
import pytube
from pytube import exceptions
from typing import Tuple, Callable
import subprocess
import tempfile
import shutil


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

    def is_valid_playlist(self):
        """True if playlist exists"""
        try:
            self.playlist.length
        except Exception:
            return False
        else:
            return True

    def stop_download(self):
        self.stop = True
        # TODO make sure download is not currupted when stoped half way through

    def video_id_in_list(self, video: pytube.YouTube, files_names: list[str]):
        """Returns True if video id exists in list
        by checking for video id in the title"""

        video_id = video.video_id
        video_id_formatted = f"[{video_id}]"
        # TODO change to check if its at the end of the song name
        for fileName in files_names:
            if video_id_formatted in fileName:
                return True
        else:
            return False
        

    def get_values_for_downloading_text(self, song: pytube.YouTube, is_finished: bool):
        items_completed = len(self.files_downloaded)
        amount_of_items = len(self.files_to_download) - len(self.unaccessable_videos)
        if song is None:
            return (items_completed, amount_of_items, "", is_finished)
        try:
            title = song.title
        except exceptions.PytubeError:
            title = ""
        return (items_completed, amount_of_items, title, is_finished)

    def get_values_for_loading_text(self, song: pytube.YouTube, is_finished: bool):
        total_videos_to_download = (
            len(self.playlist.videos)
            - len(self.files_in_folder)
            - len(self.files_age_restricted)
        )
        total_videos_loaded = len(self.files_to_download)
        if song is None:
            return (total_videos_loaded, total_videos_to_download, "", is_finished)
        try:
            title = song.title
        except exceptions.PytubeError:
            title = ""
        return (total_videos_loaded, total_videos_to_download, title, is_finished)

    def download_all_audio(
        self,
        update_downloading_text_cb: Callable[[int, int, str], any],
        update_loading_text_cb: Callable[[int, int, str], any],
        show_download_complete_message_cb,
    ):
        """Gets list of YouTube objects and coverts them to mp3.
        Also adds video id at the end of the title"""
        self.stop = False
        self.filter_playlist(update_loading_text_cb)
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
            update_downloading_text_cb(*self.get_values_for_downloading_text(video, False))
            try:
                audio = video.streams.filter(only_audio=True).first()
            except KeyError:
                self.unaccessable_videos.append(video)
                continue
            else:
                audio.download(temp_dir)
                audio_temp_file_path = os.path.join(temp_dir, audio.default_filename)
                filename = audio.default_filename.removesuffix(".mp4")
                new_file_path = f"{self.dir}/{filename} [{video.video_id}].mp3"
                subprocess.run(["ffmpeg", "-nostdin", "-i", audio_temp_file_path, new_file_path])
                try:
                    os.remove(audio_temp_file_path)
                except Exception:
                    pass
                self.files_downloaded.append(video)
                is_last_video = i == len(self.files_to_download) - 1
                if is_last_video:
                    update_downloading_text_cb(*self.get_values_for_downloading_text(video, False))
        try:
            shutil.rmtree(temp_dir)
        except Exception:
            pass

        update_downloading_text_cb(*self.get_values_for_downloading_text(None, True))
        show_download_complete_message_cb(self)


    def filter_playlist(
        self, update_loading_text_cb: Callable[[int, int], any]
    ) -> Tuple[pytube.YouTube, pytube.YouTube]:
        """Filters playlist into:
        a playlist of already in directory songs
        and playlist of other songs"""

        file_names_in_out_dir = [
            f for f in os.listdir(self.dir) if os.path.isfile(os.path.join(self.dir, f))
        ]

        for video in self.playlist.videos:
            if self.stop == True:
                return
            values_for_loading_text = self.get_values_for_loading_text(video, False)
            update_loading_text_cb(*values_for_loading_text)
            file_exists = self.video_id_in_list(video, file_names_in_out_dir)
            
            if file_exists:
                self.files_in_folder.append(video)
            elif video.age_restricted:
                self.files_age_restricted.append(video)
            else:
                self.files_to_download.append(video)

        values_for_loading_text = self.get_values_for_loading_text(None, True)
        update_loading_text_cb(*values_for_loading_text)
