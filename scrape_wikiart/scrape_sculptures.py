""" 
Scrape the sculpture pages and info off of the WikiArt database
"""

from bs4 import BeautifulSoup
import json
import pandas as pd
from fake_useragent import UserAgent
from helpers import *


def parse_sculpture_page(sculpture_url, file_name, scraped_image_name, fake_user):
    """
    Parse the page for the sculpture
    
    :param sculpture_url: Url for the sculpture
    :param file_name: Given file_name for the new image
    :param scraped_image_name: Name of the file for the Small wikiart image we already have
    :param fake_user: Fake User object
    
    :return: style - String
    """
    soup = BeautifulSoup(get_page(sculpture_url, fake_user).content, "lxml")

    # Get Style of Sculpture
    style = soup.findAll("li", {"class": "dictionary-values"})[0].text
    style = style[style.find(":") + 1:].strip()
    print(style)

    # Get the link to the original image
    image_links = soup.findAll("main", {"ng-controller": "ArtworkViewCtrl"})[0]['ng-init']

    # Dict of different types of images...there's a semicolon at the end
    string_dict = image_links[image_links.find("=") + 2:-1]
    image_dict = json.loads(string_dict)

    # We want the image marked 'original'
    original_image_link = [url for url in image_dict["ImageThumbnailsModel"][0]["Thumbnails"] if url['Name'] == 'Original'][0]

    # Get & save image - using file_num
    # Only scrape if not saved already
    scrape_image(file_name, original_image_link['Url'], fake_user, "wikiart")

    # Fix name for wikiart image...if not fixed yet (so needs to exist)
    if os.path.isfile(os.path.join("../../sculpture_data/wikiart/wikiart_images/", scraped_image_name)):
        os.rename(os.path.join("../../sculpture_data/wikiart/wikiart_images/", scraped_image_name),
                  os.path.join("../../sculpture_data/wikiart/wikiart_images/", file_name))

    return style


def parse_sculpture_list():
    """
    Parse the basic shit for every sculpture. Includes: 
    1. Artist
    2. Title
    3. Image Link
    4. Link to Sculpture Page
    
    Note: The file I'm scraping from is already downloaded on my machine. 
    Here's the link - https://www.wikiart.org/en/paintings-by-genre/sculpture?select=featured#!#filterName:featured,viewType:masonry
    You need to load all the images b4 downloading
    
    :return: Dict - with the lists of 4 pieces of info above
    """
    file = open("../../sculpture_data/wikiart/WikiArt.html").read()
    soup = BeautifulSoup(file, "lxml")

    # Get name of artists
    artists = soup.findAll("a", {"target": "_self", "class": "artist-name ng-binding"})
    artists = [artist.text[:artist.text.find('\xa0•')].strip() for artist in artists]

    # Get name of title and link to the page for the sculpture
    titles = soup.findAll("a", {"target": "_self", "class": "artwork-name ng-binding"})
    sculpt_titles = [title.text.strip() for title in titles]
    sculpt_links = [title['href'] for title in titles]

    # Get image name
    lis = soup.findAll("li", {"class": "ng-scope"})
    images = [li.find("img")['ng-src'] for li in lis]

    # Just take image name from hyperlink we just scraped (from last backslash)
    images = [image[image.rfind("/") + 1:] for image in images]

    return {'artists': artists, 'titles': sculpt_titles, "links":  sculpt_links, 'images': images}


def get_data():
    """
    Scrape all the data for the wikiart database. Includes scraping all the individual pages and getting all the
    images. 
    
    :return: CSV with full dataset
    """
    sculptures_raw = parse_sculpture_list()

    # Create the fake_user object
    fake_user = UserAgent(cache=True)

    # Counter for determining file_name
    # e.g. 0005, 0050, 0467, 2350...etc.
    file_num = 0

    # Load data already processed
    processed_sculptures = json.loads(open("../../sculpture_data/wikiart/sculptures/wikiart_sculpture_data.json", 'r').read())['data']

    # Get files already processed - can easily look if scraped
    files_processed = [x['file'] for x in processed_sculptures]

    for index in range(len(sculptures_raw['images'])):
        file_name = "".join(["wikiart_", format(file_num, '04d'), ".jpg"])

        # If we already parsed and scraped - don't bother
        if file_name not in files_processed:
            print(file_name)

            # Parse and append
            style = parse_sculpture_page(sculptures_raw['links'][index], file_name, sculptures_raw['images'][index], fake_user)
            processed_sculptures.append({'Author': sculptures_raw['artists'][index],
                                         "title": sculptures_raw['titles'][index],
                                         'file': file_name,
                                         'url': sculptures_raw['links'][index],
                                         'Period': style})

            # Dump over new json to file
            # Can take a while so can start up easier
            with open("../../sculpture_data/wikiart/sculptures/wikiart_sculpture_data.json", "w+") as file:
                json.dump({"data": processed_sculptures}, file)

        file_num += 1

    return pd.DataFrame(processed_sculptures)


def main():
    df = get_data()

if __name__ == "__main__":
    main()
