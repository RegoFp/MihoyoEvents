# This is a sample Python script.
import datetime
import io
import tkinter
from urllib.request import urlopen

import customtkinter as customtkinter
import requests as requests
from PIL import ImageTk, Image

from datetime import timedelta, datetime

from ctypes import windll

import bar

import HonkaiWikiScraper

bgColor = "#212325"
frameBgColor = "#2a2d2e"

root = tkinter.Tk()
root.configure(bg=bgColor)
# root.minsize(1052,450)
# root.resizable(False,False)
root.title("Abyss")


# TODO If there is no current banner, it will probably explode
# TODO Maybe switch from the hu tao bot json and scrap my own data for genshin too
# TODO make it appear in the bottom tight

def set_app_window():
    # to display the window icon on the taskbar,
    # even when using root.overrideredirect(True
    # Some WindowsOS styles, required for task bar integration
    gwl_ex_style = -20
    ws_ex_app_window = 0x00040000
    ws_ex_tool_window = 0x00000080

    hwnd = windll.user32.GetParent(root.winfo_id())
    style = windll.user32.GetWindowLongW(hwnd, gwl_ex_style)
    style = style & ~ws_ex_tool_window
    style | ws_ex_app_window

    windll.user32.SetWindowLongW(hwnd, gwl_ex_style, style)

    root.wm_withdraw()
    root.after(10, lambda: root.wm_deiconify())


def get_percentage(start_date, end_date):
    current_date = datetime.now().replace(microsecond=0)

    total_time = end_date - start_date
    remaining_time = end_date - current_date

    percentage = (remaining_time.total_seconds() * 100) / total_time.total_seconds()

    return percentage


def update_progress(start, end, current_bar):
    percentage = get_percentage(start, end)
    current_bar.set((100 - percentage) / 100)
    if current_bar.get() < 1:
        root.after(3600000, update_progress, start, end, current_bar)


# updates the timer every second
def countdown(widget, end_date):
    count = get_secs_until(end_date)
    widget.configure(text=timedelta(seconds=count))
    if count > 0:
        # call countdown again after 1000ms (1s)
        root.after(1000, countdown, widget, end_date)


# Returns the time in seconds until the event
def get_secs_until(date):
    days_until = date - datetime.now()
    return int(days_until.total_seconds())


class GenshinPanel(customtkinter.CTkFrame):
    def __init__(self, parent):
        customtkinter.CTkFrame.__init__(self, parent)

        # changes background color
        self.configure(fg_color=(bgColor, bgColor))

        response = requests.get("https://raw.githubusercontent.com/Tibowl/HuTao/master/src/data/events.json")
        data = response.json()

        in_game_events = []
        banners = []
        current_date = datetime.now().replace(microsecond=0)

        for event in data:

            # currentDate = datetime.strptime("2022-09-02 10:00:00", "%Y-%m-%d %H:%M:%S")
            if "start" in event and "end" in event and datetime.strptime(event["start"], "%Y-%m-%d %H:%M:%S") \
                    - timedelta(hours=7) < current_date < datetime.strptime(event["end"], "%Y-%m-%d %H:%M:%S"):
                if event["type"] == "In-game":
                    in_game_events.append(event)
                elif event["type"] == "Banner":
                    banners.append(event)

        try:
            if len(banners) > 1:
                banner_frame = customtkinter.CTkFrame(self, corner_radius=10)
                banner_frame.pack()

                try:
                    banner_image = ImageTk.PhotoImage(
                        Image.open(io.BytesIO(urlopen(banners[0]["img"]).read())).resize((300, 148),
                                                                                         Image.LANCZOS))
                    banner_image_label = customtkinter.CTkLabel(banner_frame, image=banner_image, text="")
                    banner_image_label.image = banner_image
                    banner_image_label.pack(pady=10, padx=10)
                except Exception:
                    print("Error getting image")

                remaining_time = datetime.strptime(banners[0]["end"], "%Y-%m-%d %H:%M:%S") - current_date

                start = datetime.strptime(banners[0]["start"], "%Y-%m-%d %H:%M:%S")
                end = datetime.strptime(banners[0]["end"], "%Y-%m-%d %H:%M:%S")

                percentage = get_percentage(start, end)

                banner_progress_bar = customtkinter.CTkProgressBar(banner_frame, orientation='horizontal',
                                                                   mode='determinate')
                banner_progress_bar.pack(ipadx=10, pady=2)
                banner_progress_bar.set((100 - percentage) / 100)

                banner_timer = customtkinter.CTkLabel(banner_frame, text=str(remaining_time))
                banner_timer.pack()

                root.after(1000, update_progress, start, end, banner_progress_bar)  # updates the bar every hour
                root.after(0, countdown, banner_timer, end)  # updates timer every second

        except Exception:
            print("Error getting banner")

        for event in in_game_events:
            # ttk.Separator(frame,orient='horizontal',bg="gray").pack(fill="x",padx=10,pady=10)
            event_frame = customtkinter.CTkFrame(self, corner_radius=10)
            event_frame.pack(fill="x", pady=(10, 0))

            start = datetime.strptime(event["start"], "%Y-%m-%d %H:%M:%S")
            end = datetime.strptime(event["end"], "%Y-%m-%d %H:%M:%S")

            percentage = get_percentage(start, end)
            remaining_time = datetime.strptime(event["end"], "%Y-%m-%d %H:%M:%S") - current_date

            customtkinter.CTkLabel(event_frame,
                                   text=event["name"].replace("Event", "").replace('"', "").replace(":", ":\n")).pack(
                pady=(5, 0))

            progress_bar = customtkinter.CTkProgressBar(event_frame, orientation='horizontal',
                                                        mode='determinate', width=120)
            progress_bar.pack(ipadx=10, pady=2)
            progress_bar.set((100 - percentage) / 100)

            timer = customtkinter.CTkLabel(event_frame, text=str(remaining_time))
            timer.pack(pady=(0, 5))

            root.after(1000, update_progress, start, end, progress_bar)  # updates the bar every hour
            root.after(0, countdown, timer, end)  # updates timer every

        if len(banners) == 0 and len(in_game_events) == 0:
            img = Image.open(r"img\Qiqi.png").resize((200, 200), Image.LANCZOS)
            ph = ImageTk.PhotoImage(img)

            qiqi_image = customtkinter.CTkLabel(self, image=ph)
            qiqi_image.image = ph
            qiqi_image.pack(pady=10, padx=10)

            tkinter.Label(self, text="Nothing going on right now", bg=frameBgColor, fg="white").pack(pady=(0, 10))


class HonkaiPanel(customtkinter.CTkFrame):
    def __init__(self, parent):
        customtkinter.CTkFrame.__init__(self, parent)

        # changes background color
        self.configure(fg_color=(bgColor, bgColor))

        # creates a frame for the banner
        banner_frame = customtkinter.CTkFrame(self, corner_radius=10)
        banner_frame.pack()

        # Gets the banner details from the scraper
        banner = HonkaiWikiScraper.get_banner()

        # get image from url
        url = banner.img
        banner_image = ImageTk.PhotoImage(Image.open(io.BytesIO(urlopen(url).read())).resize((300, 148), Image.LANCZOS))
        banner_image_label = customtkinter.CTkLabel(banner_frame, image=banner_image, text="")
        banner_image_label.image = banner_image
        banner_image_label.pack(pady=10, padx=10)

        # gets remaining banner time in %
        current_date = datetime.now().replace(microsecond=0)
        percentage = get_percentage(banner.start, banner.end)

        # creates the progress bar
        banner_progress_bar = customtkinter.CTkProgressBar(banner_frame, orientation='horizontal', mode='determinate')
        banner_progress_bar.pack(ipadx=10, pady=2)
        banner_progress_bar.set((100 - percentage) / 100)

        remaining_time = banner.end - current_date

        # adds the remaining time in text
        banner_timer = customtkinter.CTkLabel(banner_frame, text=remaining_time)
        banner_timer.pack()

        root.after(1000, update_progress, banner.start, banner.end,
                   banner_progress_bar)  # updates the bar every hour
        root.after(0, countdown, banner_timer, banner.end)  # updates timer every second

        # gets list of the current events
        events = HonkaiWikiScraper.get_events()

        for event in events:
            # creates frames for event
            event_frame = customtkinter.CTkFrame(self, corner_radius=10)
            event_frame.pack(fill="x", pady=(10, 0))

            start = event.start
            end = event.end

            # adds event name
            customtkinter.CTkLabel(event_frame, text=event.name).pack(pady=(5, 0))

            # gets remaining time in %
            percentage = get_percentage(start, end)

            # adds the progress bar
            progress_bar = customtkinter.CTkProgressBar(event_frame, orientation='horizontal',
                                                        mode='determinate', width=120)
            progress_bar.pack(ipadx=10, pady=2)
            progress_bar.set((100 - percentage) / 100)

            # adds the remaining time
            remaining_time = end - current_date
            timer = customtkinter.CTkLabel(event_frame, text=remaining_time)
            timer.pack(pady=(0, 5))

            root.after(1000, update_progress, start, end, progress_bar)  # updates the bar every hour
            root.after(0, countdown, timer, end)  # updates timer every second


# Removes the top bar and the icon in the task bar
root.overrideredirect(True)

# Adds the custom top bar from bar.py
top_bar = bar
top_bar.Bar(root).pack(fill="x")

# Crates main frame, the panels will be on
mainWindow = tkinter.Frame(bg=bgColor)
mainWindow.pack(pady=(10, 10))

# Adds the genshin panel
eventFrame = GenshinPanel(mainWindow)
eventFrame.grid(column=0, row=0, padx=(10, 5), sticky="n")

# Adds the Honkai panel
ventFrame = HonkaiPanel(mainWindow)
ventFrame.grid(column=1, row=0, padx=(10, 5), sticky="n")

# Show the windows bar icon
root.after(10, set_app_window)

# Start
root.mainloop()
