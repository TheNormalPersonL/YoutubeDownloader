import customtkinter as Ctk
from yt_dlp import YoutubeDL
from PIL import Image
import requests
from io import BytesIO
import threading

App = Ctk.CTk()
App.title("Advanced YouTube Video Downloader")
App.geometry("600x500")

Ydl = None
VideoUrl = ""

Ctk.set_appearance_mode("dark")

ButtonStyle = {"corner_radius": 8, "height": 40, "width": 200}
LabelStyle = {"text_color": "white", "font": ("Arial", 14)}

UrlLabel = Ctk.CTkLabel(App, text="Video URL - ", **LabelStyle)
UrlLabel.pack(pady=(20, 5))
UrlEntry = Ctk.CTkEntry(App, width=500, height=35, border_width=2, corner_radius=10)
UrlEntry.pack(pady=5)

StatusLabel = Ctk.CTkLabel(App, text="", font=("Arial", 12), text_color="green")
StatusLabel.pack(pady=10)

ThumbnailLabel = Ctk.CTkLabel(App, text="")
ThumbnailLabel.pack(pady=10)

VideoTitleLabel = Ctk.CTkLabel(App, text="", **LabelStyle)
VideoTitleLabel.pack(pady=5)

ResolutionDropdown = Ctk.CTkComboBox(App, values=[], width=300, height=35, corner_radius=10)
ResolutionDropdown.pack_forget()

def ProgressHook(D):
    if D['status'] == 'downloading':
        Percentage = D['_percent_str'].strip().replace('%', '')
        Speed = D['_speed_str'].replace('KiB/s', 'KB/s').replace('MiB/s', 'MB/s').strip()
        StatusLabel.configure(text=f"Downloading • {Percentage}% • {Speed}")

    elif D['status'] == 'finished':
        StatusLabel.configure(text="Download Successful!", text_color="green")

def FetchVideoInfo():
    global Ydl, VideoUrl

    VideoUrl = UrlEntry.get()
    try:
        YdlOpts = {
            'format': 'best',
            'quiet': True,
        }
        Ydl = YoutubeDL(YdlOpts)
        Info = Ydl.extract_info(VideoUrl, download=False)
        
        StatusLabel.configure(text="Video information fetched successfully!", text_color="green")
        VideoTitleLabel.configure(text=f"Title - {Info['title']}")
        
        ThumbnailUrl = Info['thumbnail']
        Response = requests.get(ThumbnailUrl)
        ImgData = Response.content
        Img = Image.open(BytesIO(ImgData))
        Img.thumbnail((300, 300))
        
        ThumbnailImage = Ctk.CTkImage(dark_image=Img)
        ThumbnailLabel.configure(image=ThumbnailImage)
        ThumbnailLabel.image = ThumbnailImage

        Resolutions = [
            f"{FormatId['format']} - {FormatId['resolution']}" 
            for FormatId in Info['formats'] 
            if 'resolution' in FormatId and FormatId['resolution'] != 'audio only' and 'Unknown' not in FormatId['resolution']
        ]
        
        ResolutionDropdown.configure(values=Resolutions)
        ResolutionDropdown.pack(pady=10)

        DownloadButton.pack(pady=20)
    except Exception as E:
        StatusLabel.configure(text="An error occurred.", text_color="red")
        print(f"Error - {E}")
        with open("error_log.txt", "a") as LogFile:
            LogFile.write(f"Error occurred for URL - {VideoUrl} - {E}\n")

FetchButton = Ctk.CTkButton(App, text="Fetch Video Information", command=FetchVideoInfo, **ButtonStyle)
FetchButton.pack(pady=20)

def DownloadVideo():
    global VideoUrl
    try:
        SelectedFormat = ResolutionDropdown.get().split(" - ")[0]
        YdlOpts = {
            'format': SelectedFormat,
            'outtmpl': './Downloaded/%(title)s.%(ext)s',
            'progress_hooks': [ProgressHook]
        }
        with YoutubeDL(YdlOpts) as Ydl:
            Ydl.download([VideoUrl])
    except Exception as E:
        StatusLabel.configure(text="An error occurred during download.", text_color="red")
        print(f"Error - {E}")
        with open("error_log.txt", "a") as LogFile:
            LogFile.write(f"Error occurred during download for URL - {VideoUrl} - {E}\n")

def StartDownloadThread():
    download_thread = threading.Thread(target=DownloadVideo)
    download_thread.start()

DownloadButton = Ctk.CTkButton(App, text="Download Video", command=StartDownloadThread, **ButtonStyle)
DownloadButton.pack_forget()

App.mainloop()
