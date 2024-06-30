import os
import pytube
from pytube import exceptions
import subprocess
import tempfile
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed


class Ripper:
    def __init__(self, dir: str, playlist_url: str):
        self.dir = dir
        self.playlist = pytube.Playlist(playlist_url)
        self.files_to_download = []
        self.files_in_folder = []
        self.files_age_restricted = []
        self.unaccessible_videos = []
        self.files_downloaded = []
        self.stop = False

    def is_valid_playlist(self):
        try:
            self.playlist.length
        except Exception:
            return False
        else:
            return True

    def stop_download(self):
        self.stop = True

    def video_id_in_list(self, video: pytube.YouTube, files_names: set):
        video_id_formatted = f"[{video.video_id}].mp3"
        return any(file_name.endswith(video_id_formatted) for file_name in files_names)

    def get_values_for_callback(self, callback_type: str, video: pytube.YouTube, is_finished: bool):
        if callback_type == 'download':
            items_completed = len(self.files_downloaded)
            amount_of_items = len(self.files_to_download) - len(self.unaccessible_videos)
        elif callback_type == 'load':
            items_completed = len(self.files_to_download)
            total_videos = len(self.playlist.videos) - len(self.files_in_folder) - len(self.files_age_restricted)
            amount_loaded = len(self.files_to_download)
            return (amount_loaded, total_videos, "", False)
        else:
            return (0, 0, "", False)

        title = video.title if video else ""
        return items_completed, amount_of_items, title, is_finished

    def download_all_audio(self, on_complete_callback, on_progress_callback, on_done_callback, on_cancel_callback):
        self.stop = False
        self.filter_playlist(on_progress_callback)
        if self.stop:
            on_cancel_callback()
            return

        self.files_downloaded = []
        self.unaccessible_videos = []
        temp_dir = os.path.join(tempfile.gettempdir(), "ripper")

        shutil.rmtree(temp_dir, ignore_errors=True)
        os.makedirs(temp_dir, exist_ok=True)

        def download_and_convert(video):
            try:
                if self.stop:
                    return

                audio = video.streams.filter(only_audio=True).first()
                if not audio:
                    self.unaccessible_videos.append(video)
                    return

                audio.download(temp_dir)
                original_file_path = os.path.join(temp_dir, audio.default_filename)
                new_file_path = os.path.join(self.dir, f"{audio.default_filename.removesuffix('.mp4')} [{video.video_id}].mp3")

                subprocess.run(["ffmpeg", "-nostdin", "-i", original_file_path, new_file_path], check=True)
                os.remove(original_file_path)

                self.files_downloaded.append(video)
                on_complete_callback(*self.get_values_for_callback('download', video, False))

            except (exceptions.PytubeError, subprocess.CalledProcessError) as e:
                print(f"Error processing video {video.title}: {str(e)}")
                self.unaccessible_videos.append(video)
                on_complete_callback(*self.get_values_for_callback('download', video, False))

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(download_and_convert, video) for video in self.files_to_download]

            for future in as_completed(futures):
                if self.stop:
                    executor.shutdown(wait=False)
                    on_cancel_callback()
                    break

        shutil.rmtree(temp_dir, ignore_errors=True)
        on_complete_callback(*self.get_values_for_callback('download', None, True))
        on_done_callback(self)

    def filter_playlist(self, on_progress_callback):
        files_names = {f for f in os.listdir(self.dir) if os.path.isfile(os.path.join(self.dir, f))}

        def process_video(video):
            if self.stop:
                return

            if self.video_id_in_list(video, files_names):
                self.files_in_folder.append(video)
            elif video.age_restricted:
                self.files_age_restricted.append(video)
            else:
                self.files_to_download.append(video)

            on_progress_callback(*self.get_values_for_callback('load', video, False))

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(process_video, video) for video in self.playlist.videos]

            for future in as_completed(futures):
                if self.stop:
                    executor.shutdown(wait=False)
                    break

        on_progress_callback(*self.get_values_for_callback('load', None, True))
