from datetime import datetime

from requests import get
from bs4 import BeautifulSoup
from dataclasses import dataclass

URL = "https://honkai-star-rail.fandom.com/wiki/Honkai:_Star_Rail_Wiki"


def download_data():
    page = get(URL)
    soup = BeautifulSoup(page.content, "html.parser")

    return soup


@dataclass
class Event:
    name: str
    start: datetime
    end: datetime
    img: str


@dataclass
class Banner:
    img: str
    start: datetime
    end: datetime


# Returns the current banner
def get_banner():
    data = download_data()

    results = data.find('div', {
        "class": "hidden wikia-gallery-position-center wikia-gallery-spacing-small wikia-gallery-border-none "
                 "wikia-gallery-caption-size-large wikia-gallery wikia-gallery-caption-below "
                 "wikia-gallery-position-left "
                 "wikia-gallery-spacing-medium wikia-gallery-border-small wikia-gallery-captions-center "
                 "wikia-gallery-caption-size-medium"})

    # get start and finish date
    date = results.find("div", {"class": "lightbox-caption"})

    time1 = date.contents[0]
    time2 = date.contents[2]

    start_format = "From %B %d, %Y"
    end_format = "to\xa0%B %d, %Y"

    start_date = datetime.strptime(time1, start_format).replace(hour=12)
    end_date = datetime.strptime(time2, end_format).replace(hour=15)

    # find image
    img = results.find("img")
    src = img.get("data-src")
    imagen = src.split("scale")
    imagen_url = imagen[0]

    banner = Banner(
        imagen_url,
        start_date,
        end_date
    )

    return banner


# Returns a list of the current events
def get_events():
    data = download_data()

    events = data.findAll('div', {
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
                # It's 4 am, but we live in Spain, so +1, obv this sucks
                datetime.strptime(str(time1), event_start_format).replace(hour=5),
                datetime.strptime(str(time2), event_end_format).replace(hour=5),
                event_img
            )

            # doesn't add the battle pass and the trials
            if new_event.name != "Nameless Honor":
                if new_event.name != "Aptitude Showcase":
                    events_list.append(new_event)

    return events_list

def get_exact_date(url):

    return urls
