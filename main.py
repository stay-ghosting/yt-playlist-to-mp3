from tkinter import filedialog
import customtkinter as ctk
from ripper import Ripper
import os
import threading
from error import *
from threadWithError import ThreadWithError


# TODO create json save - recents/ key
# TODO stop crashing
#
class main():
    def __init__(self):
        self.app = ctk.CTk()
        self.initilaise_variables()
        self.draw_screen()
        self.app.mainloop()



    def initilaise_variables(self):
        self.debug_url_input = ("https://www.youtube.com/playlist?list=PLo80Q9Yj8XHfHtCXfrp81qRw5-PtLP-TG")
        self.debug_dir_input = ("D:/ribby/Documents/Work/python/ripper/songs")

        self.url_input = ctk.StringVar()
        self.url_input.set(self.debug_url_input)
        self.dir_input = ctk.StringVar()
        self.dir_input.set(self.debug_dir_input)

        self.error_message = ctk.StringVar()
        self.error_type : Error = None

        self.lbl_file_load_progress_bar_text = ctk.StringVar()
        self.lbl_file_load_progress_bar_value = ctk.DoubleVar()
        self.on_file_loaded = self.progress("File Load Progress:", 
                                            self.lbl_file_load_progress_bar_text,
                                            self.lbl_file_load_progress_bar_value)
        self.on_file_loaded(0, 0)

        self.lbl_all_files_progress_bar_text = ctk.StringVar()
        self.lbl_all_files_progress_bar_value = ctk.DoubleVar()
        self.on_file_downloaded = self.progress("Download Progress:",
                                                self.lbl_all_files_progress_bar_text,
                                                self.lbl_all_files_progress_bar_value)
        self.on_file_downloaded(0, 0)


    def progress(self, message: str, text: ctk.StringVar, progress: ctk.DoubleVar):
        def progressAndMessage(items_completed: int, amount_of_items: int):
            if items_completed + amount_of_items <= 0:
                value = 0
                text.set(message)
            else:
                value = round(items_completed / amount_of_items, 2)
                text.set(f"{message} {items_completed} / {amount_of_items}")

            progress.set(value)
        return progressAndMessage


    # def on_file_loaded(self, files_loaded, amount_of_files):
    #     if files_loaded + amount_of_files <= 0:
    #         value = 0
    #         message = f"File Load Progress:"
    #     else:
    #         value = round(files_loaded / amount_of_files * 100)
    #         message = f"File Load Progress: {files_loaded} / {amount_of_files}"

    #     self.lbl_file_load_progress_bar_text.set(message)
    #     self.lbl_file_load_progress_bar_value.set(value)



    # def on_file_downloaded(self, files_downloaded, amount_of_files):
    #     if files_downloaded + amount_of_files <= 0:
    #         value = 0
    #         self.lbl_all_files_progress_bar_text.set(f"Download Progress:")
    #     else:
    #         value = files_downloaded / amount_of_files
    #         self.lbl_all_files_progress_bar_text.set(f"Download Progress: {files_downloaded} / {amount_of_files}")

    #     self.lbl_all_files_progress_bar_value.set(value)


    def download_all(self):
        playlist_url = self.url_input.get()
        dir = self.dir_input.get()

        ripper = Ripper(dir, playlist_url)

        # if directory does NOT exist ...
        if not os.path.exists(dir):
            self.error_message.set("Please select a valid folder")
            self.error_type = Error.DirectoryError
            return
        
        try:
            t = ThreadWithError(target=lambda:ripper.download_audio(self.on_file_downloaded, self.on_file_loaded))
            t.start()
        except KeyError:
            self.error_message.set("Please select a valid url")
            self.error_type = Error.URLError
            return
        # else:
        #     print("ran")
        #     threading.Thread(target=lambda:ripper.download_audio(self.on_file_downloaded)).start()

    def on_change_directory(self):
        dir_input_temp = filedialog.askdirectory()
        if dir_input_temp == "":
            return
        self.dir_input.set(dir_input_temp)
        if self.error_type == Error.DirectoryError:
            self.error_message.set("")

    def on_url_change(self, e):
        if self.error_type == Error.URLError:
            self.error_message.set("")

    def draw_screen(self):
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.app.geometry("800x500")
        self.app.title("YT Ripper")

        main = ctk.CTkFrame(self.app)

        lbl_url = ctk.CTkLabel(main, text="Playlist URL:")
        ety_url = ctk.CTkEntry(main, textvariable=self.url_input, placeholder_text="https://www.youtube.com/playlist?list=", width=500, border_width=0)
        ety_url.bind("<Key>", self.on_url_change)
        ety_url.bind("<Return>", lambda e: self.download_all())

        frm_dir = ctk.CTkFrame(main)
        btn_open_dir = ctk.CTkButton(frm_dir, text="Open Folder", command=self.on_change_directory)
        lbl_dir_title = ctk.CTkLabel(frm_dir, text=f"Output folder:")
        lbl_dir = ctk.CTkLabel(frm_dir, textvariable=self.dir_input)

        lbl_error_message = ctk.CTkLabel(main, textvariable=self.error_message, text_color="red")

        lbl_file_load_progress_bar = ctk.CTkLabel(main, textvariable=self.lbl_file_load_progress_bar_text)
        file_load_progress_bar = ctk.CTkProgressBar(main, variable=self.lbl_file_load_progress_bar_value)
        file_load_progress_bar.set(0)
        lbl_all_files_progress_bar = ctk.CTkLabel(main, textvariable=self.lbl_all_files_progress_bar_text)
        all_files_progress_bar = ctk.CTkProgressBar(main, variable=self.lbl_all_files_progress_bar_value)
        all_files_progress_bar.set(0)

        btn_download = ctk.CTkButton(main, text="Start Download", command=lambda: self.download_all())

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

main()