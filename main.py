import tkinter
import customtkinter
import subprocess
import threading

# TODO create json save - recents/ key
# TODO stop crashing
#

customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")

app = customtkinter.CTk()
app.geometry("800x240")
app.title("YT Ripper")

url_input = customtkinter.StringVar()

def on_download():
    url = url_input.get()
    subprocess.run(f"python ripper.py {url}")

# Use CTkButton instead of tkinter Button
main = customtkinter.CTkFrame(master=app)

lbl_url = customtkinter.CTkLabel(main, text="Playlist URL:")
ety_url = customtkinter.CTkEntry(main, textvariable=url_input, placeholder_text="https://www.youtube.com/playlist?list=", width=500)
btn_download = customtkinter.CTkButton(master=main, text="Start Download", command=lambda: on_download())

lbl_url.pack(pady=(20,10))
ety_url.pack(padx=20, pady=(0,20))
btn_download.pack(pady=(0,30))
main.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)

app.mainloop()