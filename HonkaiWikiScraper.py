import re
from datetime import datetime
from requests import get
from bs4 import BeautifulSoup
from dataclasses import dataclass

from multiprocessing import Pool

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
    img_url = img.get("data-src")
    img_url.replace("scale-to-width-down/225", "scale-to-width-down/400")

    # Create banner object and return it
    banner = Banner(
        img_url,
        dates[0],
        dates[1]
    )

    return banner


def search_table(row):

    row = BeautifulSoup(row, 'html.parser')

    # Date pattern to remove it from the name
    pattern = r'\d{4}-\d{2}-\d{2}'
    # Gets the url of the image

    event_img = "https://static.wikia.nocookie.net/houkai-star-rail/images/0/07/Aptitude_Showcase_-_Jingliu%2C_Tingyun%2C_Qingque%2C_Sampo.png/revision/latest/scale-to-width-down/250?cb=20231011230608"

    try:
        event_img = row.find("img").get("src").split("scale")[0]
    except:
        print("fuck")

    # Gets the name of the event and removes the date from it
    name = str(row.findAll("a")[1].contents[0])
    name = re.sub(pattern, '', name)

    # Only adds relevant events that are in game
    if name != "Nameless Honor" and "Aptitude Showcase" not in name and row.findAll("td")[2].contents[0] == "In-Game":
        # Gets the dates from the inside url
        url = row.findAll("a")[0].get("href")
        dates = get_exact_date(url)

        # Saves all events have an available date
        if dates:
            new_event = Event(
                name,
                dates[0],
                dates[1],
                event_img
            )

            # doesn't add the battle pass and the trials
            return new_event


# Returns a list of the current events
def get_events():

    page = get("https://honkai-star-rail.fandom.com/wiki/Events")
    soup = BeautifulSoup(page.content, "html.parser")

    events = soup.findAll('table', {
        "style": "width:100%;text-align:center"})

    try:
        print("events its not down")
        # Gets the current events and futures events tables and turns them into one
        tables = events[0].find_all('tr', class_=None)[1:] + events[1].find_all('tr', class_=None)[1:]

        div_texts = [str(row) for row in tables]

        with Pool(len(div_texts)) as pool:
            events_list = pool.map(func=search_table, iterable=div_texts)

        events_list = list(filter(None, events_list))
    except:

        # Gets the events from the main page is case the usual one is down
        print("The events page is down, info is less reliable")
        events_list = get_events_in_error()


    return events_list




def get_exact_date(url):
    times = []
    time_format = "%d %B, %Y %H:%M"

    url = "https://honkai-star-rail.fandom.com" + url

    # Enters the page to find the url
    page = get(url)
    soup = BeautifulSoup(page.content, "html.parser")

    data = soup.findAll('section', {
        "class": "pi-item pi-group pi-border-color"})

    dates = data[0].findAll("td")

    # gets the date from the text
    for d in dates:

        pattern = r"\d{1,2} \w+, \d{4} \d{2}:\d{2}"
        match = re.search(pattern, d.contents[1])

        if match:
            dt = datetime.strptime(match.group(), time_format)
            times.append(dt)

    return times


# In case the events page is down, it takes the events from the main page, that is less precise
def get_events_in_error():
    page = get("https://honkai-star-rail.fandom.com/wiki/Honkai:_Star_Rail_Wiki")
    data = BeautifulSoup(page.content, "html.parser")

    events = data.findAll('div', {
        "class": "hidden wikia-gallery-position-center wikia-gallery-spacing-small wikia-gallery-border-none "
                 "wikia-gallery-caption-size-large wikia-gallery wikia-gallery-caption-below "
                 "wikia-gallery-position-left wikia-gallery-spacing-medium wikia-gallery-border-small "
                 "wikia-gallery-captions-center wikia-gallery-caption-size-medium"})

    events_list = []

    # Every div is an event
    for div in events[1].findAll("div", style="width:225px"):

        try:
            # Gets the url of the image
            event_img = div.find("img").get("data-src").split("scale")[0]
        except:
            print("fucj you")

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