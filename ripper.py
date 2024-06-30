from copy import deepcopy
import os
import pytube
from pytube import exceptions
from typing import Tuple, Callable
import subprocess
import tempfile
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

class Ripper:
    def __init__(self, dir: str, playlist_url: str):
        self.dir = dir
        self.playlist = pytube.Playlist(playlist_url)
        self.files_to_download: list[pytube.YouTube] = []
        self.files_in_folder: list[pytube.YouTube] = []
        self.files_age_restricted: list[pytube.YouTube] = []
        self.unaccessible_videos: list[pytube.YouTube] = []
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
        amount_of_items = len(self.files_to_download) - len(self.unaccessible_videos)
        if song is None:
            return (items_completed, amount_of_items, "", is_finished)
        try:
            title = song.title
        except exceptions.PytubeError:
            title = ""
        return (items_completed, amount_of_items, title, is_finished)

    def get_values_for_callback_load(self, song: pytube.YouTube, is_finished: bool):
        total_videos = len(self.playlist.videos) - len(self.files_in_folder) - len(self.files_age_restricted)
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
        on_done_callback: Callable[[object], any],
    ):
        self.stop = False
        self.filter_playlist(on_progress_callback)
        if self.stop:
            return
        
        self.files_downloaded = []
        self.unaccessible_videos = []
        temp_dir = os.path.join(tempfile.gettempdir(), "ripper")

        try:
            shutil.rmtree(temp_dir)
        except Exception:
            pass

        start_time = time.time()

        def download_and_convert(video):
            try:
                audio = video.streams.filter(only_audio=True).first()
            except KeyError:
                self.unaccessible_videos.append(video)
                return
            
            on_complete_callback(*self.get_values_for_callback_download(video, False))
            
            try:
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
            except Exception as e:
                print(f"Error processing video {video.title}: {str(e)}")
            
            on_complete_callback(*self.get_values_for_callback_download(video, False))
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            # Make a copy of the list to avoid issues with generator execution
            videos_to_process = list(self.files_to_download)
            futures = [executor.submit(download_and_convert, video) for video in videos_to_process]
            
            # Wait for all tasks to complete
            for future in as_completed(futures):
                pass
        
        try:
            shutil.rmtree(temp_dir)
        except Exception:
            pass

        end_time = time.time()  # Record end time
        elapsed_time = end_time - start_time
        print(f"Total time taken: {elapsed_time:.2f} seconds")

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
            # Copy the generator output to a list to avoid concurrent access issues
            videos_to_process = list(self.playlist.videos)
            futures = [executor.submit(process_video, video) for video in videos_to_process]

            for future in as_completed(futures):
                pass

        on_progress_callback(*self.get_values_for_callback_load(None, True))

# Example usage:
if __name__ == "__main__":
    url = 'https://www.youtube.com/playlist?list=PLo80Q9Yj8XHfHtCXfrp81qRw5-PtLP-TG'
    dir = "D:/ribby/Documents/Work/python/ripper/songs"
    ripper = Ripper(dir, url)
    ripper.download_all_audio(
        on_complete_callback=lambda items_completed, amount_of_items, title, is_finished: None,
        on_progress_callback=lambda amount_loaded, total_videos, title, is_finished: None,
        on_done_callback=lambda ripper: None
    )
