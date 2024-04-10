from tkinter import filedialog
from datetime import timedelta
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk
import vlc


class ProgressBar(tk.Scale):
    def __init__(self, master, command, **kwargs):
        kwargs["showvalue"] = False
        super().__init__(
            master, # place a progress bar on the window (master)
            orient=tk.HORIZONTAL,
            length=800,
            command=command,
            **kwargs,
        )
        self.bind("<Button>", self.click)


    def click(self, e):
        if self.cget("state") == tk.NORMAL:
            val = (e.x / self.winfo_width()) * 100
            self.set(val)


# class with the player, that will be a master to everything
class Player(tk.Tk):

    # Create the window
    def __init__(self):
        super().__init__()
        self.geometry("1200x1000")
        self.configure(background="#b0c2b1")
        self.title("Player")
        ico = Image.open("media player\\assets\\icon.jpg")
        app_icon = ImageTk.PhotoImage(ico)
        self.wm_iconphoto(False, app_icon)
        self.initialize()


    # init the window
    def initialize(self):
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()
        self.current_file = None
        self.running_vid = False
        self.paused_video = False
        self.add_widgets()


    # add widgets to the window
    def add_widgets(self):
        self.media_canvas = tk.Canvas(
            self, 
            background="#000000", 
            width=1000, 
            height=600
        )
        self.media_canvas.pack(padx=5,pady=5, fill=tk.BOTH, expand=True)
        self.select_btn = tk.Button(
            self,
            text="Select Video",
            font=("Calibri", 20),
            command=self.select_video,
        )
        self.select_btn.pack(padx = 5, pady = 5)


        self.duration_info = tk.Label(
            self,
            text="00:00:00 / 00:00:00",
            font=("Calibri", 12, "bold"),
            foreground="#555555",
            background="#f0f0f0",
        )
        self.duration_info.pack(pady=5)


        # create buttons container which we will place on the master window
        self.btns_frame = tk.Frame(self, background="#b0c2b1")
        self.btns_frame.pack(pady=5)


        # create buttons
        self.play_btn = tk.Button(
            self.btns_frame,
            background="#a4ff59",
            foreground="#000000",
            font=("Calibri", 14),
            text="play",
            command=self.run_vid,
        )
        self.play_btn.pack(
            side=tk.LEFT, 
            padx=0, 
            pady=5
        )


        self.pause_btn = tk.Button(
            self.btns_frame,
            font=("Calibri", 14),
            text="pause",
            background="#f2ed5c",
            foreground="#000000",
            command=self.pause_vid,
        )
        self.pause_btn.pack(
            side=tk.LEFT, 
            padx=5, 
            pady=5
        )


        self.stop_btn = tk.Button(
            self.btns_frame,
            font=("Calibri", 14),
            background="#d65d4d",
            text="stop",
            foreground="#000000",
            command=self.stop,
        )
        self.stop_btn.pack(side=tk.LEFT, pady=5)


        self.skip_back_btn = tk.Button(
            self.btns_frame,
            font=("Calibri", 14),
            background="#7e7acc",
            text="skip back",
            foreground="#000000",
            command=self.rewind,
        )
        self.skip_back_btn.pack(
            side=tk.LEFT, 
            padx=5, 
            pady=5
        )


        self.skip_forward_btn = tk.Button(
            self.btns_frame,
            font=("Calibri", 14),
            background="#7e7acc",
            text="skip forward",
            foreground="#000000",
            command=self.forward,
        )
        self.skip_forward_btn.pack(
            side=tk.LEFT, 
            padx=0, 
            pady=5
        )

        # create the progress bar
        self.progress_bar = ProgressBar(
            self,
            self.set_video_timing, 
            background="#88bd8b", 
            highlightthickness=10,
            borderwidth=1,
            sliderlength=50
        )
        self.progress_bar.pack(
            fill=tk.X, 
            padx=5, 
            pady=5
        )

        
    # select a vid function
    def select_video(self):
        path = filedialog.askopenfilename(
            filetypes=[("Media Files", "*.mp4 *.avi")]
        )
        if path != None:
            self.current_file = path
            self.duration_info.config(text="00:00:00 / " + self.get_duration_string())
            self.run_vid()


    # get the duration by using timedelta function
    def get_duration_string(self):
        if self.running_vid:
            total_dur = self.player.get_length()
            duration_str = str(timedelta(milliseconds=total_dur))[:-3] # use slice to get miliseconds
            return duration_str
        return "00:00:00"


    # run a video
    def run_vid(self):
        if not self.running_vid:
            video = self.instance.media_new(self.current_file)
            self.player.set_media(video)
            self.player.set_hwnd(self.media_canvas.winfo_id())
            self.player.play()
            self.running_vid = True

    
    # pause the video
    def pause_vid(self):
        if self.running_vid:
            if self.paused_video:
                self.player.play()
                self.paused_video = False
                self.pause_btn.config(text="pause")
            else:
                self.player.pause()
                self.paused_video = True
                self.pause_btn.config(text="resume")

    # set video timing by progress bar
    def set_video_timing(self, val):
        if self.running_vid:
            total_dur = self.player.get_length()
            position = int((float(val) / 100) * total_dur)
            self.player.set_time(position)
    

    # move video timing forward by 30 seconds
    def forward(self):
        if self.running_vid:
            current_time = self.player.get_time() + 30000 # time is in miliseconds, so add 30000
            self.player.set_time(current_time)


    # move video timing back by 10 seconds
    def rewind(self):
        if self.running_vid:
            current_time = self.player.get_time() - 10000 # time is in miliseconds, so add 10000
            self.player.set_time(current_time)


    # stop the video completely
    def stop(self):
        if self.running_vid:
            self.player.stop()
            self.running_vid = False
        self.duration_info.config(text="00:00:00 / " + self.get_duration_string())


    # update the video 
    def update_video(self):
        if self.running_vid:
            total_dur = self.player.get_length()
            current_time = self.player.get_time()
            progress = (current_time / total_dur) * 100
            self.progress_bar.set(progress)
            cur_time_str = str(timedelta(milliseconds=current_time))[:-3] # use slice to get miliseconds
            duration_str = str(timedelta(milliseconds=total_dur))[:-3]
            self.duration_info.config(text=f"{cur_time_str} / {duration_str}")
        self.after(1000, self.update_video) # update video every second



if __name__ == "__main__":
    app = Player()
    app.update_video()
    app.mainloop()