#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup, NavigableString

# Download the page
page = requests.get("https://www.chromium.org/chromium-os/developer-information-for-chrome-os-devices/")

soup = BeautifulSoup(page.content, 'html.parser')
table = soup.find_all("table")[-1]

SupportedBoards = ["asuka", "caroline", "cave", "chell", "glados", "kunimitsu", "lars", "sentry" "nami", "octopus", "volteer", "coral", "reef", "hatch", "puff"]

for child in table.children:
    try:
        #print(child.contents)
        if (child.contents[9].text.strip().lower() in SupportedBoards) or (child.contents[11].text.strip().lower() in SupportedBoards):
            # Newlines count as elements, so we use 5 instead of 3
            nameElement = child.contents[5]
            name = nameElement.a.text.strip()
            if name != "":
                print(f"* {name}")
    except AttributeError:
        continue