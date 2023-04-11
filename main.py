from tkinter import filedialog
import customtkinter as ctk
from ripper import Ripper
import os
import threading
from threadWithReturn import ThreadWithReturnValue
from error import *


# TODO create json save - recents/ key
# TODO stop crashing
#

app = ctk.CTk()

url_input = ctk.StringVar()

dir_input = ctk.StringVar()

error_message = ctk.StringVar()

lbl_file_load_progress_bar_text = ctk.StringVar()
def set_loading_files_data(files_loaded, amount_of_files):
    file_load_progress_bar.set(files_loaded / amount_of_files)
    return f"File Load Progress: {files_loaded} / {amount_of_files}"

lbl_all_files_progress_bar_text = ctk.StringVar()
def set_downloading_files_data(files_downloaded, amount_of_files):
    all_files_progress_bar.set(files_downloaded/ amount_of_files)
    return f"Download Progress: {files_downloaded} / {amount_of_files}"

# set initial values

url_input.set("https://www.youtube.com/playlist?list=PLo80Q9Yj8XHfHtCXfrp81qRw5-PtLP-TG")
dir_input.set("D:/ribby/Documents/Work/python/ripper/songs")

error_message.set("")
error_type : Error = None

# lbl_file_load_progress_bar_text.set(set_loading_files_data(0, 0))
# lbl_all_files_progress_bar_text.set(set_downloading_files_data(0, 0))


def on_file_loaded(files_loaded, amount_of_files):
    set_loading_files_data(files_loaded, amount_of_files)

def on_complete_callback(files_downloaded, amount_of_files):
    set_downloading_files_data(files_downloaded, amount_of_files)


def on_download():
    global error_type
    playlist_url = url_input.get()
    dir = dir_input.get()

    ripper = Ripper(dir, playlist_url)

    # if directory does NOT exist ...
    if not os.path.exists(dir):
        error_message.set("Please select a valid folder")
        error_type = Error.DirectoryError
        return
    
    try:
        threading.Thread(target=lambda:ripper.filter_playlist(on_file_loaded)).start()
    except KeyError:
        error_message.set("Please select a valid url")
        error_type = Error.URLError
        return
    else:
        threading.Thread(target=lambda:ripper.download_audio(on_complete_callback)).start()

def on_change_directory():
    dir_input_temp = filedialog.askdirectory()
    if dir_input_temp == "":
        return
    dir_input.set(dir_input_temp)
    if error_type == Error.DirectoryError:
        error_message.set("")

def on_url_change(e):
    if error_type == Error.URLError:
        error_message.set("")





ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

app.geometry("800x500")
app.title("YT Ripper")


main = ctk.CTkFrame(app)

lbl_url = ctk.CTkLabel(main, text="Playlist URL:")
ety_url = ctk.CTkEntry(main, textvariable=url_input, placeholder_text="https://www.youtube.com/playlist?list=", width=500, border_width=0)
ety_url.bind("<Key>", on_url_change)
ety_url.bind("<Return>", lambda e: on_download())

frm_dir = ctk.CTkFrame(main)
btn_open_dir = ctk.CTkButton(frm_dir, text="Open Folder", command=on_change_directory)
lbl_dir_title = ctk.CTkLabel(frm_dir, text=f"Output folder:")
lbl_dir = ctk.CTkLabel(frm_dir, textvariable=dir_input)

lbl_error_message = ctk.CTkLabel(main, textvariable=error_message, text_color="red")

lbl_file_load_progress_bar = ctk.CTkLabel(main, textvariable=lbl_file_load_progress_bar_text)
file_load_progress_bar = ctk.CTkProgressBar(main)
file_load_progress_bar.set(0)
lbl_all_files_progress_bar = ctk.CTkLabel(main, textvariable=lbl_all_files_progress_bar_text)
all_files_progress_bar = ctk.CTkProgressBar(main)
all_files_progress_bar.set(0)

btn_download = ctk.CTkButton(main, text="Start Download", command=lambda: on_download())

frm_dir.pack(fill=ctk.BOTH, padx=20, pady=(30, 0))
lbl_dir_title.grid(column=0, row=0, sticky=ctk.W, padx=(10, 0), pady=(10, 0))
lbl_dir.grid(column=0, row=1, sticky=ctk.W, padx=(10, 0))
btn_open_dir.grid(column=1, row=0, rowspan=2, sticky=ctk.NE, padx=(0, 10), pady=(10, 0))
frm_dir.columnconfigure(0, weight=1)
frm_dir.columnconfigure(1, weight=1)

lbl_url.pack(pady=(40,5), anchor=ctk.W, padx=(30,0))
ety_url.pack(padx=20, pady=(0,0))

lbl_error_message.pack(pady=5)
lbl_file_load_progress_bar.pack(anchor=ctk.W, padx=(30,0))
file_load_progress_bar.pack(fill=ctk.BOTH, padx=20, pady=(5, 15))
lbl_all_files_progress_bar.pack(anchor=ctk.W, padx=(30,0))
all_files_progress_bar.pack(fill=ctk.BOTH, padx=20, pady=5)

btn_download.pack(pady=(30,30))
main.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)

app.mainloop()