from datetime import datetime

from requests import get
from bs4 import BeautifulSoup
from dataclasses import dataclass

URL = "https://honkai-star-rail.fandom.com/wiki/Honkai:_Star_Rail_Wiki"
page = get(URL)

soup = BeautifulSoup(page.content, "html.parser")


@dataclass
class Event:
    name: str
    start: datetime
    end: datetime
    img: str


# BANNERS
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

start_format = "From %B %d, %Y"
end_format = "\xa0%B %d, %Y"

Start_date = datetime.strptime(time[0], start_format).replace(hour=13)
End_date = datetime.strptime(time[1], end_format).replace(hour=13)

# find image
img = results.find("img")
src = img.get("data-src")

# '2023-09-26 14:59:00'
imagen = src.split("scale")
imagenUrl = imagen[0]


# Returns a list of the current events
def get_events():
    events = soup.findAll('div', {
        "class": "hidden wikia-gallery-position-center wikia-gallery-spacing-small wikia-gallery-border-none "
                 "wikia-gallery-caption-size-large wikia-gallery wikia-gallery-caption-below "
                 "wikia-gallery-position-left wikia-gallery-spacing-medium wikia-gallery-border-small "
                 "wikia-gallery-captions-center wikia-gallery-caption-size-medium"})

    events_list = []

    # Every div is an event
    for div in events[1].findAll("div", style="width:225px"):

        # Gets the url of the image
        event_img = div.find("img").get("data-src").split("scale")[0]

        # Gets the name of the event
        name = div.find("div", {"class": "gallery-image-wrapper accent"}).find("a").get("title").split("/")[0]

        # Gets the start and finish date and formats it
        event_date = div.find("div", {"class": "lightbox-caption"})

        time1 = event_date.contents[0]
        time2 = event_date.contents[2]

        event_start_format = "From %B %d, %Y"
        event_end_format = "to\xa0%B %d, %Y"

        # If it has "since" it's a permanent event, no reason to add it
        if "since" in time1:
            print("permanent event")
        else:
            new_event = Event(
                name,
                datetime.strptime(str(time1), event_start_format).replace(hour=13),
                datetime.strptime(str(time2), event_end_format).replace(hour=13),
                event_img
            )

            # doesn't add the battle pass and the trials
            if new_event.name != "Nameless Honor":
                if new_event.name != "Aptitude Showcase":
                    events_list.append(new_event)

    return events_list


def get_banner_image():
    return imagenUrl


def get_banner_start():
    return Start_date


def get_banner_end():
    return End_date
