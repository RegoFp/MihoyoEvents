import re
from datetime import datetime
import cProfile

from requests import get
from bs4 import BeautifulSoup
from dataclasses import dataclass

import time
import numpy as np

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

    # Gets the date from the inside url
    url = results.find("div", {"class": "gallery-image-wrapper accent"}).find("a").get("href")
    dates = get_exact_date(url)

    # find image
    img = results.find("img")
    src = img.get("data-src")
    imagen = src.split("scale")
    imagen_url = imagen[0]

    banner = Banner(
        imagen_url,
        dates[0],
        dates[1]
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

        # Gets the date from the inside url
        url = div.find("div", {"class": "gallery-image-wrapper accent"}).find("a").get("href")
        dates = get_exact_date(url)

        new_event = Event(
            name,
            dates[0],
            dates[1],
            event_img
        )

        # doesn't add the battle pass and the trials
        if new_event.name != "Nameless Honor":
            if new_event.name != "Aptitude Showcase":
                events_list.append(new_event)

    return events_list


def get_exact_date(url):
    times = []
    time_format = "%d %B, %Y %H:%M"

    url = "https://honkai-star-rail.fandom.com" + url

    page = get(url)
    soup = BeautifulSoup(page.content, "html.parser")

    data = soup.findAll('section', {
        "class": "pi-item pi-group pi-border-color"})

    dates = data[0].findAll("td")

    for d in dates:

        pattern = r"\d{1,2} \w+, \d{4} \d{2}:\d{2}"
        match = re.search(pattern, d.contents[1])

        if match:
            dt = datetime.strptime(match.group(), time_format)
            times.append(dt)

    return times
