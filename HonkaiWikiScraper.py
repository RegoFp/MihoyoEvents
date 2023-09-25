import re
from datetime import datetime
from requests import get
from bs4 import BeautifulSoup
from dataclasses import dataclass

URL = "https://honkai-star-rail.fandom.com/wiki/Honkai:_Star_Rail_Wiki"


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
    page = get(URL)
    data = BeautifulSoup(page.content, "html.parser")

    results = data.find('div', {
        "class": "hidden wikia-gallery-position-center wikia-gallery-spacing-small wikia-gallery-border-none "
                 "wikia-gallery-caption-size-large wikia-gallery wikia-gallery-caption-below "
                 "wikia-gallery-position-left "
                 "wikia-gallery-spacing-medium wikia-gallery-border-small wikia-gallery-captions-center "
                 "wikia-gallery-caption-size-medium"})

    # Gets the date from the inside url
    url = results.find("div", {"class": "gallery-image-wrapper accent"}).find("a").get("href")
    dates = get_exact_date(url)

    # find image
    img = results.find("img")
    src = img.get("data-src")
    imagen = src.split("scale")
    imagen_url = imagen[0]

    # Create banner object and return it
    banner = Banner(
        imagen_url,
        dates[0],
        dates[1]
    )

    return banner


# Returns a list of the current events
def get_events():
    page = get("https://honkai-star-rail.fandom.com/wiki/Events")
    soup = BeautifulSoup(page.content, "html.parser")

    events = soup.findAll('table', {
        "style": "width:100%;text-align:center"})

    events_list = []
    tables = events[0].find_all('tr', class_=None)[1:] + events[1].find_all('tr', class_=None)[1:]
    # all rows in the table except the head

    pattern = r'\d{4}-\d{2}-\d{2}'

    for row in tables:
        # Gets the url of the image
        event_img = row.find("img").get("src").split("scale")[0]

        # Gets the name of the event and removes the date from the name
        name = str(row.findAll("a")[1].contents[0])

        name = re.sub(pattern, '', name)

        # Gets the dates from the inside url
        url = row.findAll("a")[0].get("href")
        dates = get_exact_date(url)

        # Saves all events that are in game and have an available date
        if row.findAll("td")[2].contents[0] == "In-Game" and dates:
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
