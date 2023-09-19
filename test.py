import io
import tkinter

import customtkinter
import requests
from datetime import datetime, timedelta
from urllib.request import urlopen
from PIL import ImageTk, Image

response = requests.get("https://raw.githubusercontent.com/Tibowl/HuTao/master/src/data/events.json")
data = response.json()
inGameEvents = []
banners = []

root = tkinter.Tk()


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

Imagen1 = Image.open(io.BytesIO(urlopen(banners[0]["img"]).read())).resize((300, 148),Image.Resampling.LANCZOS)
w,h = Imagen1.size
Imagen1 = Imagen1.crop((w-220,0,w-80,h))

Imagen2 = Image.open(io.BytesIO(urlopen(banners[1]["img"]).read())).resize((300, 148),Image.Resampling.LANCZOS)
w,h = Imagen2.size
Imagen2 = Imagen2.crop((w-220,0,w-80,h))

combined = Image.new('RGB',(280,h))
combined.paste(Imagen1,(0,0))
combined.paste(Imagen2,(140,0))


bannerImage = ImageTk.PhotoImage(combined)



bannerImageLabel = customtkinter.CTkLabel(root, image=bannerImage,text="")
bannerImageLabel.image = bannerImage
bannerImageLabel.grid(column=0,row=0)

root.mainloop()