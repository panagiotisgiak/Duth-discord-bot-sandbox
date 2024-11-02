import requests
from bs4 import BeautifulSoup
import re

def fetchBearer():
    url = "https://kavala.citybus.gr/stops/live/1004"
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        script_tag = soup.find("script", string=lambda s: "token" in s if s else False)
        
        if script_tag:
            match = re.search(r"token\s*=\s*'([\w\.-]+)'", script_tag.string)
            if match:
                return match.group(1)
            else:
                print("Token not found in script.")
        else:
            print("Relevant script not found.")
    else:
        print("Failed to retrieve page.")