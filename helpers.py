"""
Collections of shared functions relevant to both more than one file in either or both projects (wga & wikiart)
"""
import requests
import time
import os
from PIL import Image
from io import BytesIO


def get_page(url, fake_user):
    """
    Retrieve the contents for this page

    :param url: Link to the page
    :param fake_user: Fake user agent object 

    :return: response object
    """
    response = None

    try:
        response = requests.get(url, headers={'User-Agent': fake_user.random}, timeout=5)
        response.raise_for_status()
    except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
        # If anything goes wrong we log the url
        print("Error getting ", url)
        with open("../url_error_log.txt", "w") as file:
            file.write(url)

    # We'll give them 3 seconds
    time.sleep(3)

    return response


def if_image_exists(file, db):
    """
    If the image file exists we skip scraping that page

    :param file: file name
    :param db: wikiart, nga, or wga

    :return: Boolean - True if exists already
    """
    return os.path.isfile(f"../../sculpture_data/{db}/sculpture_images/{file}")


def save_image(image_response, file_name, db):
    """
    Saves the image as a given name. 

    :param image_response: response from requests
    :param file_name: Name of file
    :param db: wikiart, nga, or wga

    :return: None
    """
    # Idk....
    if db != "nga":
        img = Image.open(BytesIO(image_response))
        img.save(f"../../sculpture_data/{db}/sculpture_images/{file_name}")
    else:
        file = open(f"../../sculpture_data/{db}/sculpture_images/{file_name}", 'wb')
        file.write(image_response)
        file.close()


def scrape_image(file_name, url, fake_user, db):
    """
    Scrape the given image if it hasn't been scraped yet and store in the appropriate directory
    
    :return: None
    """
    # Get & save image - using file_num
    # Only scrape if not saved already
    if not if_image_exists(file_name, db):
        image_response = get_page(url, fake_user).content
        save_image(image_response, file_name, db)
