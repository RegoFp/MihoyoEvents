from datetime import datetime

from requests import get
from bs4 import BeautifulSoup

URL = "https://honkai-star-rail.fandom.com/wiki/Honkai:_Star_Rail_Wiki"
page = get(URL)

soup = BeautifulSoup(page.content, "html.parser")

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


startDate = datetime.strptime(time[0], startFormat)
endDate = datetime.strptime(time[1], endFormat)

# find image
img = results.find("img", {"alt": "Epochal Spectrum 2023-08-30"})
src = img.get("data-src")

# '2023-09-26 14:59:00'
imagen = src.split("scale")
imagenUrl = imagen[0]


def get_banner_image():
    return imagenUrl


def get_banner_start():
    return startDate


def get_banner_end():
    return endDate
