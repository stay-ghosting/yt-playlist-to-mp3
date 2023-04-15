#https://www.youtube.com/watch?v=jM5tLsf6ivc
#D:\ribby\Documents\Work\python\ripper\songs

from pytube import YouTube
import ffmpeg

# yt = YouTube("https://www.youtube.com/watch?v=jM5tLsf6ivc")
# stream = yt.streams.filter(only_audio=True).first()
# path = stream.download()

in1 = ffmpeg.input("https://www.youtube.com/watch?v=jM5tLsf6ivc")
ffmpeg.output(in1, "x.mp3")
