import logging
import asyncio

# Fixes reactor already installed error
try:
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
except:
    pass

import nest_asyncio
from pathlib import Path
from utils.scraper import scrape
from utils.downloaders import get_downloaders
import settings
from colorama import Fore, Style
import requests
import os
import re
import warnings
import readchar
import multiprocessing

logging.basicConfig(level=logging.DEBUG, filename='logs.log',
                    format='%(asctime)s:%(levelname)s:%(module)s:%(filename)s:%(lineno)d:%(message)s',
                    filemode='w')
warnings.filterwarnings("ignore", category=DeprecationWarning)

DOWNLOAD_FOLDER = settings.download_folder
CPU_COUNT = settings.threads if settings.threads != 0 else multiprocessing.cpu_count()


def log(text, style):
    # Log function for printing to command line
    print(style + str(text) + Style.RESET_ALL)


def clear():
    # Clears command window
    os.system('cls' if os.name == 'nt' else 'clear')


def version_check() -> None:
    response = requests.get("https://api.github.com/repos/Jules-WinnfieldX/CyberDropDownloader/releases/latest")
    latest_version = response.json()["tag_name"]
    current_version = "2.5.5"
    logging.debug(f"We are running version {current_version} of Cyberdrop Downloader")
    if latest_version != current_version:
        log("A new version of CyberDropDownloader is available\n"
            "Download it here: https://github.com/Jules-WinnfieldX/CyberDropDownloader/releases/latest\n", Fore.RED)
        input("To continue anyways press enter")
        clear()


def regex_links(urls) -> list:
    all_links = [x.group().replace(".md.", ".") for x in re.finditer(r"(?:http.*?)(?=('|$|\n|\r\n|\r)|\")", urls)]
    return all_links


async def main():
    nest_asyncio.apply()
    clear()
    version_check()
    if os.path.isfile("URLs.txt"):
        log("URLs.txt exists", Fore.WHITE)
    else:
        f = open("URLs.txt", "w+")
        log("URLs.txt created", Fore.WHITE)
        exit()

    file_object = open("URLs.txt", "r")
    urls = file_object.read()
    urls = regex_links(urls)
    cookies, content_object = scrape(urls)
    if not content_object:
        logging.error(f'ValueError No links: {content_object}')
        raise ValueError('No links found, check the URL.txt\nIf the link works in your web browser, please open an issue ticket with me.')
    clear()
    downloaders = get_downloaders(content_object, cookies=cookies, folder=Path(DOWNLOAD_FOLDER), max_workers=CPU_COUNT)

    for downloader in downloaders:
        await downloader.download_content()
    log('Finished scraping. Enjoy :)', Fore.WHITE)
    log('If you have ".download" files remaining, rerun this program. You most likely ran into download attempts limit', Fore.WHITE)
    repr(readchar.readchar())


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
