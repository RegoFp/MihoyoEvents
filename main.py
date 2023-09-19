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

print(HonkaiWikiScraper.get_banner_image())

# Press Mayús+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

bgColor = "#212325"
frameBgColor = "#2a2d2e"

# https://github.com/TomSchimansky/CustomTkinter swith to this
root = tkinter.Tk()
root.configure(bg=bgColor)
# root.minsize(1052,450)
# root.resizable(False,False)
root.title("Abyss")


def set_appwindow():  # to display the window icon on the taskbar,
    # even when using root.overrideredirect(True
    # Some WindowsOS styles, required for task bar integration
    GWL_EXSTYLE = -20
    WS_EX_APPWINDOW = 0x00040000
    WS_EX_TOOLWINDOW = 0x00000080
    # Magic
    hwnd = windll.user32.GetParent(root.winfo_id())
    stylew = windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
    stylew = stylew & ~WS_EX_TOOLWINDOW
    stylew = stylew | WS_EX_APPWINDOW
    res = windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, stylew)

    root.wm_withdraw()
    root.after(10, lambda: root.wm_deiconify())


def getPercetage(startDate, endDate):
    currentDate = datetime.now().replace(microsecond=0)

    totalTime = endDate - startDate
    remainingtime = endDate - currentDate

    percentage = (remainingtime.total_seconds() * 100) / totalTime.total_seconds()

    return percentage


def updateProgress(start,end, bar):
    percentage = getPercetage(start, end)
    bar.set((100 - percentage) / 100)
    if bar.get() < 1:
        root.after(3600000, updateProgress, start,end, bar)


# updates the timer every second
def countdown(widget, endDate):
    count = secsUntil(endDate)
    widget.configure(text=timedelta(seconds=count))
    if count > 0:
        # call countdown again after 1000ms (1s)
        root.after(1000, countdown, widget, endDate)


# Returns the time in seconds until the event
def secsUntil(date):
    daysUntil = date - datetime.now()
    return int(daysUntil.total_seconds())


def eventsPanel(frame):
    response = requests.get("https://raw.githubusercontent.com/Tibowl/HuTao/master/src/data/events.json")
    data = response.json()
    inGameEvents = []
    banners = []
    for event in data:

        currentDate = datetime.now().replace(microsecond=0)
        # currentDate = datetime.strptime("2022-09-02 10:00:00", "%Y-%m-%d %H:%M:%S")
        if "start" in event and "end" in event and currentDate > datetime.strptime(event["start"],
                                                                                   "%Y-%m-%d %H:%M:%S") - timedelta(
            hours=7) and currentDate < datetime.strptime(event["end"], "%Y-%m-%d %H:%M:%S"):
            if event["type"] == "In-game":
                inGameEvents.append(event)
            elif event["type"] == "Banner":
                banners.append(event)

    try:
        if len(banners) > 1:
            bannerFrame = customtkinter.CTkFrame(frame, corner_radius=10)
            bannerFrame.pack()

            try:
                bannerImage = ImageTk.PhotoImage(
                    Image.open(io.BytesIO(urlopen(banners[0]["img"]).read())).resize((300, 148),
                                                                                     Image.Resampling.LANCZOS))
                bannerImageLabel = customtkinter.CTkLabel(bannerFrame, image=bannerImage, text="")
                bannerImageLabel.image = bannerImage
                bannerImageLabel.pack(pady=10, padx=10)
            except:
                print("Error getting image")

            remainingtime = datetime.strptime(banners[0]["end"], "%Y-%m-%d %H:%M:%S") - currentDate

            start = datetime.strptime(banners[0]["start"], "%Y-%m-%d %H:%M:%S")
            end = datetime.strptime(banners[0]["end"], "%Y-%m-%d %H:%M:%S")

            percentage = getPercetage(start, end)

            print(percentage)
            bannerProgressbar = customtkinter.CTkProgressBar(bannerFrame, orientation='horizontal', mode='determinate')
            bannerProgressbar.pack(ipadx=10, pady=2)
            bannerProgressbar.set((100 - percentage) / 100)

            bannerTimer = customtkinter.CTkLabel(bannerFrame, text=remainingtime)
            bannerTimer.pack()

            root.after(1000, updateProgress, start,end, bannerProgressbar)  # updates the bar every hour
            root.after(0, countdown, bannerTimer, end)  # updates timer every second
    except:
        print("Error getting banner")

    for event in inGameEvents:
        # ttk.Separator(frame,orient='horizontal',bg="gray").pack(fill="x",padx=10,pady=10)
        eFrame = customtkinter.CTkFrame(frame, corner_radius=10)
        eFrame.pack(fill="x", pady=(10, 0))

        start = datetime.strptime(event["start"], "%Y-%m-%d %H:%M:%S")
        end = datetime.strptime(event["end"], "%Y-%m-%d %H:%M:%S")

        percentage = getPercetage(start, end)
        remainingtime = datetime.strptime(event["end"], "%Y-%m-%d %H:%M:%S") - currentDate

        customtkinter.CTkLabel(eFrame, text=event["name"].replace("Event", "").replace('"', "")).pack(pady=(5, 0))

        bar = customtkinter.CTkProgressBar(eFrame, orientation='horizontal', mode='determinate', width=120)
        bar.pack(ipadx=10, pady=2)
        bar.set((100 - percentage) / 100)
        timer = customtkinter.CTkLabel(eFrame, text=remainingtime)
        timer.pack(pady=(0, 5))
        print(event["name"])

        root.after(1000, updateProgress, start,end, bar)  # updates the bar every hour
        root.after(0, countdown, timer, end)  # updates timer every

    if len(banners) == 0 and len(inGameEvents) == 0:
        img = Image.open("img\Qiqi.png").resize((200, 200), Image.Resampling.LANCZOS)
        ph = ImageTk.PhotoImage(img)

        qiqiImage = customtkinter.CTkLabel(frame, image=ph)
        qiqiImage.image = ph
        qiqiImage.pack(pady=10, padx=10)

        tkinter.Label(frame, text="Nothing going on right now", bg=frameBgColor, fg="white").pack(pady=(0, 10))


class HonkaiPanel(customtkinter.CTkFrame):
    def __init__(self, parent):
        customtkinter.CTkFrame.__init__(self,parent)

        url = HonkaiWikiScraper.get_banner_image()
        bannerImage2 = ImageTk.PhotoImage(Image.open(io.BytesIO(urlopen(url).read())).resize((300, 148),Image.Resampling.LANCZOS))
        bannerImageLabel2 = customtkinter.CTkLabel(self, image=bannerImage2, text="")
        bannerImageLabel2.image = bannerImage2
        bannerImageLabel2.pack(pady=10, padx=10)

        currentDate = datetime.now().replace(microsecond=0)

        remainingtime = HonkaiWikiScraper.get_banner_end() - currentDate

        percentage = getPercetage(HonkaiWikiScraper.get_banner_start(),HonkaiWikiScraper.get_banner_end())

        bannerProgressbar = customtkinter.CTkProgressBar(self, orientation='horizontal', mode='determinate')
        bannerProgressbar.pack(ipadx=10, pady=2)
        bannerProgressbar.set((100 - percentage) / 100)

        remainingtime = HonkaiWikiScraper.get_banner_end() - currentDate

        bannerTimer = customtkinter.CTkLabel(self, text=remainingtime)
        bannerTimer.pack()

        root.after(1000, updateProgress, HonkaiWikiScraper.get_banner_start(), HonkaiWikiScraper.get_banner_end(), bannerProgressbar)  # updates the bar every hour
        root.after(0, countdown, bannerTimer, HonkaiWikiScraper.get_banner_end())  # updates timer every second

        print(remainingtime)

root.overrideredirect(True)

topbar = bar
topbar.Bar(root).pack(fill="x")

mainWindow = tkinter.Frame(bg=bgColor)
mainWindow.pack(pady=(10, 10))

eventFrame = customtkinter.CTkFrame(mainWindow, height=220, width=200, corner_radius=10, cursor="hand2",
                                    fg_color=(bgColor, bgColor))
eventsPanel(eventFrame)
eventFrame.grid(column=0, row=0, padx=(10, 5),sticky="n")

ventFrame = HonkaiPanel(mainWindow)
ventFrame.grid(column=1, row=0, padx=(10, 5),sticky="n")

root.after(10, set_appwindow)  # Show the windows bar icon

root.mainloop()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
