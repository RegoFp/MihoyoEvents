# This is a sample Python script.
import colorsys
import datetime
import io
import time
import tkinter
from urllib.request import urlopen

import customtkinter as customtkinter
import requests as requests
from PIL import ImageTk, Image

from datetime import timedelta, datetime

from ctypes import windll

from colorthief import ColorThief

import bar

import HonkaiWikiScraper

bgColor = "#212325"
frameBgColor = "#2a2d2e"

root = tkinter.Tk()
root.configure(bg=bgColor)
# root.minsize(1052,450)
# root.resizable(False,False)
root.title("Abyss")


# TODO Maybe switch from the hu tao bot json and scrap my own data for genshin too


def change_color_lightness(hex_color, lightness, saturation):
    """
    Receives a hex color, changes its saturation and lightness, then returns it
    :param str hex_color:
    :param int lightness:
    :param int saturation:
    :return str:
    """

    lightness = lightness / 100
    saturation = saturation / 100

    hex_color = hex_color.lstrip('#')

    r, g, b = tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
    h, l, s = colorsys.rgb_to_hls(r, g, b)

    r, g, b = colorsys.hls_to_rgb(h, lightness, saturation)
    r, g, b = [x * 255.0 for x in (r, g, b)]
    hex_color = '#%02x%02x%02x' % (int(r), int(g), int(b))

    return hex_color


def get_color_from_image(image):
    # get the dominant color
    color_thief = ColorThief(image)
    dominant_color = color_thief.get_color(quality=50)

    # Convert it to HLS
    h, l, s = colorsys.rgb_to_hls(dominant_color[0], dominant_color[1], dominant_color[2])

    # Convert it to hex
    r, g, b = colorsys.hls_to_rgb(h, 50, s)
    hex_color = '#%02x%02x%02x' % (int(r), int(g), int(b))

    return hex_color


def update_window_position():
    # update is not the best way of doing this
    root.update()
    height = windll.user32.GetSystemMetrics(1) - root.winfo_height() - 70
    position = windll.user32.GetSystemMetrics(0) - root.winfo_width() - 30

    root.geometry("+" + str(position) + "+" + str(height))


def reset_frames(genshin, honkai):
    honkai.forget()
    honkai.destroy()

    genshin.forget()
    genshin.destroy()

    # Adds the genshin panel
    event_frame = GenshinPanel(mainWindow)
    event_frame.grid(column=0, row=0, padx=(10, 5), sticky="n")

    # Adds the Honkai panel
    vent_frame = HonkaiPanel(mainWindow)
    vent_frame.grid(column=1, row=0, padx=(5, 10), sticky="n")


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

    if count == 0:
        reset_frames(eventFrame, ventFrame)
    # Checks that the widget was not destroyed before trying to update it
    if widget.winfo_exists():
        widget.configure(text=timedelta(seconds=count))
        if count > 0:
            # call countdown again after 1000ms (1s)
            root.after(1000, countdown, widget, end_date)


# Returns the time in seconds until the event
def get_secs_until(date):
    days_until = date - datetime.now()
    return int(days_until.total_seconds())


class EventFrame(customtkinter.CTkFrame):
    def __init__(self, parent, event, color):
        customtkinter.CTkFrame.__init__(self, parent)

        self.configure(corner_radius=10)

        current_date = datetime.now().replace(microsecond=0)

        start = event.start
        end = event.end

        # adds event name
        customtkinter.CTkLabel(self, text=event.name).pack(pady=(5, 0))

        # gets remaining time in %
        percentage = get_percentage(start, end)

        # adds the progress bar
        progress_bar = customtkinter.CTkProgressBar(self, orientation='horizontal',
                                                    mode='determinate', width=120,
                                                    progress_color=color,
                                                    fg_color=change_color_lightness(color, 12, 60))
        progress_bar.pack(ipadx=10, pady=2)
        progress_bar.set((100 - percentage) / 100)

        # adds the remaining time
        remaining_time = end - current_date
        timer = customtkinter.CTkLabel(self, text=remaining_time)
        timer.pack(pady=(0, 5))

        root.after(1000, update_progress, start, end, progress_bar)  # updates the bar every hour
        root.after(0, countdown, timer, end)  # updates timer every second


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

            if "start" in event and "end" in event and datetime.strptime(event["start"], "%Y-%m-%d %H:%M:%S") \
                    - timedelta(hours=7) < current_date < datetime.strptime(event["end"], "%Y-%m-%d %H:%M:%S"):
                if event["type"] == "In-game":
                    in_game_events.append(event)
                elif event["type"] == "Banner":
                    banners.append(event)

        hex_color = bgColor

        try:
            banner_frame = customtkinter.CTkFrame(self, corner_radius=10)

            banner_frame.pack()

            try:
                banner_image = ImageTk.PhotoImage(
                    Image.open(io.BytesIO(urlopen(banners[0]["img"]).read())).resize((300, 169),
                                                                                     Image.LANCZOS))
                banner_image_label = customtkinter.CTkLabel(banner_frame, image=banner_image, text="")
                banner_image_label.image = banner_image
                banner_image_label.pack(pady=10, padx=10)

                hex_color = get_color_from_image(io.BytesIO(urlopen(banners[0]["img"]).read()))
                hex_color = change_color_lightness(hex_color, 19, 17)

                banner_frame.configure(fg_color=(hex_color, hex_color))

            except Exception:
                print("Error getting image")

            remaining_time = datetime.strptime(banners[0]["end"], "%Y-%m-%d %H:%M:%S") - current_date

            start = datetime.strptime(banners[0]["start"], "%Y-%m-%d %H:%M:%S")
            end = datetime.strptime(banners[0]["end"], "%Y-%m-%d %H:%M:%S")

            percentage = get_percentage(start, end)

            banner_progress_bar = customtkinter.CTkProgressBar(banner_frame, orientation='horizontal',
                                                               mode='determinate',
                                                               progress_color=change_color_lightness(hex_color, 50,
                                                                                                     50),
                                                               fg_color=change_color_lightness(hex_color, 12, 60))
            banner_progress_bar.pack(ipadx=10, pady=2)
            banner_progress_bar.set((100 - percentage) / 100)

            banner_timer = customtkinter.CTkLabel(banner_frame, text=str(remaining_time))
            banner_timer.pack()

            root.after(1000, update_progress, start, end, banner_progress_bar)  # updates the bar every hour
            root.after(0, countdown, banner_timer, end)  # updates timer every second

        except Exception:
            print("Error getting banner")

        for event in in_game_events:
            event_frame = customtkinter.CTkFrame(self, corner_radius=10)
            event_frame.pack(fill="x", pady=(10, 0))

            event_frame.configure(fg_color=(hex_color, hex_color))

            start = datetime.strptime(event["start"], "%Y-%m-%d %H:%M:%S")
            end = datetime.strptime(event["end"], "%Y-%m-%d %H:%M:%S")

            percentage = get_percentage(start, end)
            remaining_time = datetime.strptime(event["end"], "%Y-%m-%d %H:%M:%S") - current_date

            customtkinter.CTkLabel(event_frame,
                                   text=event["name"].replace("Event", "").replace('"', "").replace(":", ":\n")).pack(
                pady=(5, 0))

            progress_bar = customtkinter.CTkProgressBar(event_frame, orientation='horizontal',
                                                        mode='determinate', width=120,
                                                        progress_color=change_color_lightness(hex_color, 50,
                                                                                              50),
                                                        fg_color=change_color_lightness(hex_color, 12, 60))

            progress_bar.pack(ipadx=10, pady=2)
            progress_bar.set((100 - percentage) / 100)

            timer = customtkinter.CTkLabel(event_frame, text=str(remaining_time))
            timer.pack(pady=(0, 5))

            root.after(1000, update_progress, start, end, progress_bar)  # updates the bar every hour
            root.after(0, countdown, timer, end)  # updates timer every

        if len(banners) == 0 and len(in_game_events) == 0:
            img = Image.open(r"img\Qiqi.png").resize((200, 200), Image.LANCZOS)
            tk_image = ImageTk.PhotoImage(img)

            nothing_image = customtkinter.CTkLabel(self, image=tk_image)
            nothing_image.image = tk_image
            nothing_image.pack(pady=10, padx=10)

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
        banner_image = ImageTk.PhotoImage(Image.open(io.BytesIO(urlopen(url).read())).resize((300, 169), Image.LANCZOS))
        banner_image_label = customtkinter.CTkLabel(banner_frame, image=banner_image, text="")
        banner_image_label.image = banner_image
        banner_image_label.pack(pady=10, padx=10)

        # changes the color of the background to the dominant one in the image
        hex_color = get_color_from_image(io.BytesIO(urlopen(url).read()))
        banner_frame.configure(fg_color=(hex_color, hex_color))
        progress_bar_hex_color = change_color_lightness(hex_color, 50, 50)

        # gets remaining banner time in %
        current_date = datetime.now().replace(microsecond=0)
        percentage = get_percentage(banner.start, banner.end)

        # creates the progress bar
        banner_progress_bar = customtkinter.CTkProgressBar(banner_frame, orientation='horizontal', mode='determinate',
                                                           progress_color=progress_bar_hex_color,
                                                           fg_color=change_color_lightness(hex_color, 12, 60))
        banner_progress_bar.pack(ipadx=10, pady=2)
        banner_progress_bar.set((100 - percentage) / 100)

        # adds the remaining time in text
        remaining_time = banner.end - current_date
        banner_timer = customtkinter.CTkLabel(banner_frame, text=remaining_time)
        banner_timer.pack()

        # updates the bar every hour and every second
        root.after(1000, update_progress, banner.start, banner.end, banner_progress_bar)
        root.after(0, countdown, banner_timer, banner.end)

        start = time.time()

        # gets list of the current events
        events = HonkaiWikiScraper.get_events()

        if events:
            for event in events:
                # creates frames for event
                if get_secs_until(event.end) >= 0:
                    event_frame = EventFrame(self, event, progress_bar_hex_color)
                    event_frame.configure(fg_color=(hex_color, hex_color))
                    event_frame.pack(fill="x", pady=(10, 0))

            print('It took', time.time() - start, 'seconds.')

if __name__ == '__main__':
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
    ventFrame.grid(column=1, row=0, padx=(5, 10), sticky="n")

    reloadButton = top_bar.get_returnButton()
    reloadButton["command"] = lambda genshin=eventFrame, honkai=ventFrame: reset_frames(genshin, honkai)

    # Show the windows bar icon
    root.after(10, set_app_window)

    update_window_position()

    # Start
    root.mainloop()
