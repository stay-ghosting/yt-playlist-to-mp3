from tkinter import filedialog, messagebox
import customtkinter as ctk
from ripper import Ripper
import os
from threadQueue import ThreadQueue
import threading


# TODO create json save - recents/ key
# TODO make logs
# TODO time elapsed
# TODO settings

class main:
    def __init__(self):
        self.app = ctk.CTk()
        self.ripper: Ripper = None
        self.initilaise_variables()
        self.draw_screen()
        self.app.mainloop()

    def initilaise_variables(self):
        self.debug_url_input = (
            # "https://youtube.com/playlist?list=PLo80Q9Yj8XHfU_yMt7PwYZd5SekX_Whh-&si=yIEnwfSvGfLzU3VM" # party
            "https://youtube.com/playlist?list=PLo80Q9Yj8XHfwXBQMv5qRXgyQ_KcrLRxs&si=E6UDfZZp80WrIm2y" # beats
        )
        self.debug_dir_input = os.path.join(os.getcwd(), "songs")

        self.url_input = ctk.StringVar()
        self.url_input.set(self.debug_url_input)
        self.dir_input = ctk.StringVar()
        self.dir_input.set(self.debug_dir_input)

        self.error_message_url = ctk.StringVar()
        self.error_message_dir = ctk.StringVar()

        self.lbl_file_load_progress_bar_text = ctk.StringVar()
        self.lbl_file_load_progress_bar_value = ctk.DoubleVar()
        self.on_file_loaded = self.progress(
            "Getting Songs:",
            self.lbl_file_load_progress_bar_text,
            self.lbl_file_load_progress_bar_value,
        )
        self.on_file_loaded(0, 0)

        self.lbl_all_files_progress_bar_text = ctk.StringVar()
        self.lbl_all_files_progress_bar_value = ctk.DoubleVar()
        self.on_file_downloaded = self.progress(
            "Downloading Songs:",
            self.lbl_all_files_progress_bar_text,
            self.lbl_all_files_progress_bar_value,
        )
        self.on_file_downloaded(0, 0)

    def progress(self, message: str, text: ctk.StringVar, progress: ctk.DoubleVar):
        def progressAndMessage(
            items_completed: int,
            amount_of_items: int,
            filename: str = "",
            is_finished=False,
        ):
            if is_finished:
                value = 1
                text.set(
                    f"{message} {items_completed} / {amount_of_items}\nDone!")
            elif items_completed + amount_of_items <= 0:
                value = 0
                text.set(f"{message}\n")
            else:
                value = round(items_completed / amount_of_items, 2)
                text.set(
                    f"{message} {items_completed} / {amount_of_items}\n{filename}"
                )
            self.app.update()

            progress.set(value)

        return progressAndMessage

    def download_all(self):
        playlist_url = self.url_input.get()
        dir = self.dir_input.get()

        self.ripper = Ripper(dir, playlist_url)

        has_error_occured = False
        if not self.ripper.is_valid_playlist():
            self.error_message_url.set("Please select a valid url")
            has_error_occured = True

        # if directory does NOT exist ...
        if not os.path.exists(dir):
            self.error_message_dir.set("Please select a valid folder")
            has_error_occured = True

        if has_error_occured:
            return

        threading.Thread(target=
            lambda: self.ripper.download_all_audio(
                self.on_file_downloaded, self.on_file_loaded, self.on_finish_downloading
            )
        ).start()

    def on_finish_downloading(self, ripper: Ripper):
        log = (
            (
                f"{len(ripper.files_downloaded)}/{ripper.playlist.length} file(s) downloaded"
            )
            + (
                (f"\n{len(ripper.files_age_restricted)} file(s) was age restricred")
                if (len(ripper.files_age_restricted) > 0)
                else ""
            )
            + (
                (f"\n{len(ripper.files_in_folder)} file(s) are in your folder alerady")
                if (len(ripper.files_in_folder) > 0)
                else ""
            )
            + (
                (f"\n{len(ripper.unaccessable_videos)} file(s) couldn't be downloaded")
                if (len(ripper.unaccessable_videos) > 0)
                else ""
            )
        )

        messagebox.showinfo("Done!", log)

    def on_cancel_download(self):
        if self.ripper is not None:
            self.ripper.stop_download()
            threading.Thread(target=lambda: self.on_file_loaded(0, 0)).start()
            threading.Thread(target=lambda: self.on_file_downloaded(0, 0)).start()

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

        self.app.geometry("1000x600")
        self.app.title("YT Ripper")

        main = ctk.CTkFrame(self.app)

        lbl_url = ctk.CTkLabel(main, text="Playlist URL:")
        ety_url = ctk.CTkEntry(
            main,
            textvariable=self.url_input,
            placeholder_text="https://www.youtube.com/playlist?list=",
            width=800,
            border_width=0,
        )
        ety_url.bind("<Key>", self.on_url_change)
        ety_url.bind("<Return>", lambda e: self.download_all())
        lbl_error_message_url = ctk.CTkLabel(
            main, textvariable=self.error_message_url, text_color="red"
        )

        lbl_dir_title = ctk.CTkLabel(main, text=f"Output folder:")
        frm_dir = ctk.CTkFrame(main, bg_color="#2B2A2A", fg_color="#353639")
        btn_open_dir = ctk.CTkButton(
            frm_dir, text="Open Folder", command=self.on_change_directory
        )
        lbl_dir = ctk.CTkLabel(frm_dir, textvariable=self.dir_input)
        lbl_error_message_dir = ctk.CTkLabel(
            main, textvariable=self.error_message_dir, text_color="red"
        )

        lbl_file_load_progress_bar = ctk.CTkLabel(
            main, textvariable=self.lbl_file_load_progress_bar_text, justify=ctk.LEFT
        )
        file_load_progress_bar = ctk.CTkProgressBar(
            main, variable=self.lbl_file_load_progress_bar_value, fg_color="#353639"
        )
        file_load_progress_bar.set(0)
        lbl_all_files_progress_bar = ctk.CTkLabel(
            main, textvariable=self.lbl_all_files_progress_bar_text, justify=ctk.LEFT,
        )
        all_files_progress_bar = ctk.CTkProgressBar(
            main, variable=self.lbl_all_files_progress_bar_value, fg_color="#353639"
        )
        all_files_progress_bar.set(0)

        frm_download_buttons = ctk.CTkFrame(main, fg_color="transparent")
        btn_stop_download = ctk.CTkButton(
            frm_download_buttons,
            text="Stop Download",
            command=lambda: self.on_cancel_download(),
        )
        btn_download = ctk.CTkButton(
            frm_download_buttons,
            text="Start Download",
            command=lambda: self.download_all(),
        )

        lbl_url.pack(pady=(20, 0), anchor=ctk.W, padx=(30, 0))
        ety_url.pack(padx=20, pady=(0, 0), ipady=7)
        lbl_error_message_url.pack(pady=5)

        lbl_dir_title.pack(pady=(0, 5), anchor=ctk.W, padx=(30, 0))
        frm_dir.pack(fill=ctk.BOTH, padx=20, pady=(0, 0))
        lbl_dir.pack(side=ctk.LEFT, padx=(10, 0))
        btn_open_dir.pack(side=ctk.RIGHT, padx=(0, 10), pady=(10, 10))
        lbl_error_message_dir.pack(pady=(4, 4))

        lbl_file_load_progress_bar.pack(anchor=ctk.W, padx=(30, 0))
        file_load_progress_bar.pack(fill=ctk.BOTH, padx=20, pady=(5, 30))
        lbl_all_files_progress_bar.pack(anchor=ctk.W, padx=(30, 0))
        all_files_progress_bar.pack(fill=ctk.BOTH, padx=20, pady=5)

        frm_download_buttons.pack(pady=(40, 30))
        btn_stop_download.pack(padx=10, side=ctk.LEFT)
        btn_download.pack(padx=10)
        main.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)


main()
