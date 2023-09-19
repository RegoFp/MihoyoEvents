from datetime import datetime

from requests import get
from bs4 import BeautifulSoup
from dataclasses import dataclass
import re

URL = "https://honkai-star-rail.fandom.com/wiki/Honkai:_Star_Rail_Wiki"
page = get(URL)

soup = BeautifulSoup(page.content, "html.parser")


@dataclass
class event:
    name: str
    start: datetime
    end: datetime
    img: str


## BANNERS
# find banner
results = soup.find('div', {
    "class": "hidden wikia-gallery-position-center wikia-gallery-spacing-small wikia-gallery-border-none "
             "wikia-gallery-caption-size-large wikia-gallery wikia-gallery-caption-below wikia-gallery-position-left "
             "wikia-gallery-spacing-medium wikia-gallery-border-small wikia-gallery-captions-center "
             "wikia-gallery-caption-size-medium"})

# get texts
date = results.find("div", {"class": "lightbox-caption"})

time = date.text.split("(")
time = time[0].split("to")

startFormat = "From %B %d, %Y"
endFormat = "\xa0%B %d, %Y"

startDate = datetime.strptime(time[0], startFormat).replace(hour=13)
endDate = datetime.strptime(time[1], endFormat).replace(hour=13)

print(endDate)

# find image
img = results.find("img")
src = img.get("data-src")

# '2023-09-26 14:59:00'
imagen = src.split("scale")
imagenUrl = imagen[0]


# Returns a list of the current events
def getEvents():
    events = soup.findAll('div', {
        "class": "hidden wikia-gallery-position-center wikia-gallery-spacing-small wikia-gallery-border-none wikia-gallery-caption-size-large wikia-gallery wikia-gallery-caption-below wikia-gallery-position-left wikia-gallery-spacing-medium wikia-gallery-border-small wikia-gallery-captions-center wikia-gallery-caption-size-medium"})

    eventsList = []

    for div in events[1].findAll("div", style="width:225px"):
        img = div.find("img").get("data-src").split("scale")[0]

        name = div.find("div", {"class": "gallery-image-wrapper accent"}).find("a").get("title").split("/")[0]

        date = div.find("div", {"class": "lightbox-caption"})

        time1 = date.contents[0]
        time2 = date.contents[2]

        startFormat = "From %B %d, %Y"
        endFormat = "to\xa0%B %d, %Y"

        if "since" in time1:
            print("permanent event")
        else:
            thisone = event(
                name,
                datetime.strptime(time1, startFormat).replace(hour=13),
                datetime.strptime(time2, endFormat).replace(hour=13),
                img
            )

            # doesnt add the battlepass and the trials
            if thisone.name != "Nameless Honor":
                if thisone.name != "Aptitude Showcase":
                    eventsList.append(thisone)

    return eventsList


getEvents()


def get_banner_image():
    return imagenUrl


def get_banner_start():
    return startDate


def get_banner_end():
    return endDate
