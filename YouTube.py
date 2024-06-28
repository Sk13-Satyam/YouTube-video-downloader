import os
import threading
import time
import re
from pytube import YouTube, Playlist
from tqdm import tqdm
import concurrent.futures
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

class YouTubeDownloader:
    def __init__(self, master):
        self.master = master
        master.title("Ultimate YouTube Downloader")
        master.geometry("600x400")

        self.url_label = ttk.Label(master, text="Enter YouTube URL:")
        self.url_label.pack(pady=5)

        self.url_entry = ttk.Entry(master, width=50)
        self.url_entry.pack(pady=5)

        self.output_label = ttk.Label(master, text="Output Directory:")
        self.output_label.pack(pady=5)

        self.output_entry = ttk.Entry(master, width=50)
        self.output_entry.pack(pady=5)

        self.browse_button = ttk.Button(master, text="Browse", command=self.browse_output)
        self.browse_button.pack(pady=5)

        self.is_playlist_var = tk.BooleanVar()
        self.playlist_check = ttk.Checkbutton(master, text="Is Playlist", variable=self.is_playlist_var)
        self.playlist_check.pack(pady=5)

        self.audio_only_var = tk.BooleanVar()
        self.audio_check = ttk.Checkbutton(master, text="Audio Only", variable=self.audio_only_var)
        self.audio_check.pack(pady=5)

        self.highest_quality_var = tk.BooleanVar()
        self.highest_quality_check = ttk.Checkbutton(master, text="Highest Quality", variable=self.highest_quality_var)
        self.highest_quality_check.pack(pady=5)

        self.download_button = ttk.Button(master, text="Download", command=self.start_download)
        self.download_button.pack(pady=10)

        self.progress = ttk.Progressbar(master, length=400, mode='determinate')
        self.progress.pack(pady=10)

        self.status_label = ttk.Label(master, text="")
        self.status_label.pack(pady=5)

    def browse_output(self):
        directory = filedialog.askdirectory()
        self.output_entry.delete(0, tk.END)
        self.output_entry.insert(0, directory)

    def start_download(self):
        url = self.url_entry.get()
        output_path = self.output_entry.get()
        is_playlist = self.is_playlist_var.get()
        audio_only = self.audio_only_var.get()
        highest_quality = self.highest_quality_var.get()

        if not url or not output_path:
            messagebox.showerror("Error", "Please enter both URL and output directory")
            return

        threading.Thread(target=self.download, args=(url, output_path, is_playlist, audio_only, highest_quality)).start()

    def download(self, url, output_path, is_playlist, audio_only, highest_quality):
        try:
            if is_playlist:
                self.download_playlist(url, output_path, audio_only, highest_quality)
            else:
                self.download_video(url, output_path, audio_only, highest_quality)
        except Exception as e:
            self.update_status(f"Error: {str(e)}")

    def download_playlist(self, url, output_path, audio_only, highest_quality):
        playlist = Playlist(url)
        self.update_status(f"Downloading playlist: {playlist.title}")
        for video_url in playlist.video_urls:
            self.download_video(video_url, output_path, audio_only, highest_quality)

    def download_video(self, url, output_path, audio_only, highest_quality):
        yt = YouTube(url, on_progress_callback=self.on_progress)
        self.update_status(f"Downloading: {yt.title}")

        if audio_only:
            stream = yt.streams.get_audio_only()
        elif highest_quality:
            stream = yt.streams.get_highest_resolution()
        else:
            stream = yt.streams.filter(progressive=True, file_extension="mp4").first()

        if not stream:
            self.update_status("No suitable stream found")
            return

        file_extension = "mp3" if audio_only else "mp4"
        filename = self.sanitize_filename(f"{yt.title}.{file_extension}")
        file_path = os.path.join(output_path, filename)

        stream.download(output_path=output_path, filename=filename)
        self.update_status(f"Downloaded: {filename}")

    def on_progress(self, stream, chunk, bytes_remaining):
        total_size = stream.filesize
        bytes_downloaded = total_size - bytes_remaining
        percentage = (bytes_downloaded / total_size) * 100
        self.progress['value'] = percentage
        self.master.update_idletasks()

    def update_status(self, message):
        self.status_label.config(text=message)
        self.master.update_idletasks()

    @staticmethod
    def sanitize_filename(filename):
        return re.sub(r'[^\w\-_\. ]', '_', filename)

if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeDownloader(root)
    root.mainloop()
