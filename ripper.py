import os
import pytube
from typing import Tuple, Callable

# https://www.youtube.com/playlist?list=PLo80Q9Yj8XHfHtCXfrp81qRw5-PtLP-TG
def file_exists_in_folder(url: str, dir: str):
    """Returns True if file exists in folder 
    by checking for video id in the title"""
    # get the title
    video_id = url.split("=")[1]
    video_id_formatted = f"[{video_id}]"
    # video = pytube.YouTube(url) TODO
    # video.video_id
    # get names of every file in directory
    filesNames = [f for f in os.listdir(dir) 
                  if os.path.isfile(os.path.join(dir, f))]
    # for each file ...
    for fileName in filesNames:
        # if file found in directory ...
        if video_id_formatted in fileName:
            print(f"file already exists   id:{video_id}   title:{fileName}")
            # return true
            return True
    # if not found
    else:
        # return false
        return False
  
def download_audio(videos: list[pytube.YouTube], dir: str, 
                   on_progress_callback: Callable[[any, int], None],
                   on_complete_callback: Callable[[int, int], None]):
    """Gets list of YouTube objects and coverts them to mp3.
    Also adds video id at the end of the title"""
    # for each video ...
    for i, video in enumerate(videos):
        files_downloaded = i + 1
        amount_of_files = len(videos)
        video.register_on_progress_callback(lambda stream, chunk, bytes_remaining: 
                                            on_progress_callback(stream, bytes_remaining))
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
            # add it to the title and set it to mp3 file
            new_name = video.title.replace('"', '') + f"[{video_id}].mp3"
            # download the file
            audio.download(dir, filename=new_name)
        

def filter_playlist(playlist_url: str, dir:str) -> Tuple[pytube.YouTube, pytube.YouTube]:
    """Filters playlist into:
    a playlist of already in directory songs
    and playlist of other songs """

    # get playlist
    playlist = pytube.Playlist(playlist_url)
    # file lists to populate
    files_to_download = []
    files_in_folder = []
    # for video in playlist ...
    for video in playlist.videos:
        # if in directory already ...
        if file_exists_in_folder(video.watch_url, dir) or video.age_restricted == True:
            # add to files in folder list
            files_in_folder.append(video)
        else:
            # add to files to download list
            files_to_download.append(video)
    # return files list in tuple
    return files_in_folder, files_to_download


# url = 'https://www.youtube.com/playlist?list=PLo80Q9Yj8XHfHtCXfrp81qRw5-PtLP-TG'
# dir = "D:/ribby/Documents/Work/python/ripper/songs"

# files_in_folder, files_to_download = filter_playlist(url, dir)
# download_audio(files_to_download, dir)