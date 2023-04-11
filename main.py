from tkinter import filedialog, messagebox
import customtkinter as ctk
from ripper import Ripper
import os
from threadQueue import ThreadQueue


# TODO create json save - recents/ key
# TODO make logs
# TODO add tags to filenames so file_exists_in_folder can find it
# TODO convert to mp3
# TODO fix load bar when invalid loads come up

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

        self.error_message_url = ctk.StringVar()
        self.error_message_dir = ctk.StringVar()

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

    def download_all(self):
        playlist_url = self.url_input.get()
        dir = self.dir_input.get()

        ripper = Ripper(dir, playlist_url)

        has_error_occured = False
        if not ripper.is_valid_playlist():
            ripper = None
            self.error_message_url.set("Please select a valid url")
            has_error_occured = True

        # if directory does NOT exist ...
        if not os.path.exists(dir):
            self.error_message_dir.set("Please select a valid folder")
            has_error_occured = True

        if has_error_occured:
            return
        
        t = ThreadQueue()
        t.add(lambda:print(1))
        t.add(lambda:ripper.download_audio(self.on_file_downloaded, self.on_file_loaded, self.on_finish_downloading))
    
  
    def on_finish_downloading(self, ripper: Ripper):
        log = (
        (f"{len(ripper.files_downloaded)}/{ripper.playlist.length} file(s) downloaded")
            + ((f"\n{len(ripper.files_age_restricted)} file(s) was age restricred") if (len(ripper.files_age_restricted) > 0) else "")
            + ((f"\n{len(ripper.files_in_folder)} file(s) are in your folder alerady") if (len(ripper.files_in_folder) > 0) else "")
            + ((f"\n{ripper.unaccessable_videos} file(s) couldn't be downloaded") if (len(ripper.unaccessable_videos) > 0) else ""))
        
        messagebox.showinfo("Done!", log)
        

    def on_change_directory(self):
        dir_input_temp = filedialog.askdirectory()
        if dir_input_temp == "":
            return
        self.dir_input.set(dir_input_temp)
        self.error_message_dir.set("")

    def on_url_change(self, e):
        self.error_message_url.set("")

    def draw_screen(self):
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.app.geometry("800x500")
        self.app.title("YT Ripper")

        main = ctk.CTkFrame(self.app)

        frm_dir = ctk.CTkFrame(main)
        btn_open_dir = ctk.CTkButton(frm_dir, text="Open Folder", command=self.on_change_directory)
        lbl_dir_title = ctk.CTkLabel(frm_dir, text=f"Output folder:")
        lbl_dir = ctk.CTkLabel(frm_dir, textvariable=self.dir_input)
        lbl_error_message_dir = ctk.CTkLabel(main, textvariable=self.error_message_dir, text_color="red")

        lbl_url = ctk.CTkLabel(main, text="Playlist URL:")
        ety_url = ctk.CTkEntry(main, textvariable=self.url_input, placeholder_text="https://www.youtube.com/playlist?list=", width=500, border_width=0)
        ety_url.bind("<Key>", self.on_url_change)
        ety_url.bind("<Return>", lambda e: self.download_all())
        lbl_error_message_url = ctk.CTkLabel(main, textvariable=self.error_message_url, text_color="red")

        lbl_file_load_progress_bar = ctk.CTkLabel(main, textvariable=self.lbl_file_load_progress_bar_text)
        file_load_progress_bar = ctk.CTkProgressBar(main, variable=self.lbl_file_load_progress_bar_value)
        file_load_progress_bar.set(0)
        lbl_all_files_progress_bar = ctk.CTkLabel(main, textvariable=self.lbl_all_files_progress_bar_text)
        all_files_progress_bar = ctk.CTkProgressBar(main, variable=self.lbl_all_files_progress_bar_value)
        all_files_progress_bar.set(0)

        btn_download = ctk.CTkButton(main, text="Start Download", command=lambda: self.download_all())

        lbl_url.pack(pady=(20,5), anchor=ctk.W, padx=(30,0))
        ety_url.pack(padx=20, pady=(0,0))
        lbl_error_message_url.pack(pady=5)

        frm_dir.pack(fill=ctk.BOTH, padx=20, pady=(0, 0))
        lbl_dir_title.grid(column=0, row=0, sticky=ctk.W, padx=(10, 0), pady=(10, 0))
        lbl_dir.grid(column=0, row=1, sticky=ctk.W, padx=(10, 0))
        btn_open_dir.grid(column=1, row=0, rowspan=2, sticky=ctk.NE, padx=(0, 10), pady=(10, 0))
        frm_dir.columnconfigure(0, weight=1)
        frm_dir.columnconfigure(1, weight=1)
        lbl_error_message_dir.pack(pady=(4, 4))

        lbl_file_load_progress_bar.pack(anchor=ctk.W, padx=(30,0))
        file_load_progress_bar.pack(fill=ctk.BOTH, padx=20, pady=(5, 15))
        lbl_all_files_progress_bar.pack(anchor=ctk.W, padx=(30,0))
        all_files_progress_bar.pack(fill=ctk.BOTH, padx=20, pady=5)

        btn_download.pack(pady=(30,30))
        main.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)

main()