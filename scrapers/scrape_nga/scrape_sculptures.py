"""
Scrape the sculpture pages and info off of the NGA database
NOTE: Robots.txt specifies 10 seconds 
"""
import pandas as pd
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import json
from helpers import *

# Selenium bullshit - 2nd/3rd line is for custom User-Agent
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
opts = Options()


def parse_sculpture(sculpt):
    """
    Get info for a particular sculpture
    
    :param sculpt: <li> tag with info

    :return: name, title, image_url
    """
    # Image link
    image_url = sculpt.find("img")['src']

    # Get Name and Title of Sculpture
    dt_tags = sculpt.find_all("dt")
    name = dt_tags[0].text
    title = dt_tags[1].text

    # Fix image url -> To get bigger image
    image_url = image_url[:image_url.find("primary-0") + len("primary-0") + 1] + "440x400.jpg"
    if "iiif/" in image_url:
        image_url = image_url[:image_url.find("iiif/")] + image_url[image_url.find("iiif/") + len("iiif/"):]

    return name, title, image_url


def parse_page(style, page_num, fake_user):
    """
    Get the basic stuff needed for a given style/page
    
    :param style: Style to be scraped
    :param page_num: Page #
    :param fake_user: Fake User Object
    
    :return: list of <li> tags
    """
    url = f"{style}".join(["https://www.nga.gov/collection-search-result.html?artobj_imagesonly=Images_online&artobj_"
                           "classification=sculpture&artobj_style=", f"&pageNumber={page_num+1}&lastFacet=artobj_style"])

    # Custom User-Agent
    opts.add_argument(fake_user.random)

    # Get given url and html
    # To deal with dynamic content
    browser = webdriver.Chrome(chrome_options=opts)
    browser.get(url)

    # Pass for 10 seconds
    time.sleep(10)

    soup = BeautifulSoup(browser.page_source, "lxml")

    # Destroy the object
    browser.quit()

    # List of sculptures
    return soup.findAll("li", {"class": "art"})


def parse_styles(fake_user):
    """
    Parse the content for a each of the 3 styles
    Styles -> Minimalist, Impressionist, Realist
    
    :param fake_user: Fake User Object
    
    :return: List of info for each
    """
    sculptures = []

    # My name, NGA name, and # of pages
    styles = [["Minimalism", "Minimalist", 3], ["Realism", "Realist", 4], ["Impressionism", "Impressionist", 4]]

    for style in styles:
        for page_num in range(style[2]):
            print(f"Scraping {style[1]} page {page_num+1}")
            li_tags = parse_page(style[1], page_num, fake_user)

            # Iterate through sculptures on given page
            for sculpt in li_tags:
                name, title, image_url = parse_sculpture(sculpt)
                sculptures.append({"Period": style[0], "Author": name, "title": title, "url": image_url})

    return sculptures


def get_data():
    """
    Scrape all the data for the wikiart database. Includes scraping all the individual pages and getting all the
    images. 

    :return: CSV with full dataset
    """
    # Create the fake_user object
    fake_user = UserAgent(cache=True)

    # Counter for determining file_name
    # e.g. 0005, 0050, 0467, 2350...etc.
    file_num = 0

    # Load data already processed
    processed_sculptures = json.loads(open("../../../sculpture_data/nga/sculptures/nga_sculpture_data.json", 'r').read())['data']

    # Get files already processed - can easily look if scraped
    files_processed = [x['file'] for x in processed_sculptures]

    # Raw data for each sculpture
    raw_data = parse_styles(fake_user)

    for sculpture in raw_data:
        file_name = "".join(["nga_", format(file_num, '04d'), ".jpg"])

        # If we already parsed and scraped - don't bother
        if file_name not in files_processed:
            print(file_name)

            # Scrape and Save image
            scrape_image(file_name, sculpture['url'], fake_user, "nga")

            # Add to master list
            processed_sculptures.append({'Author': sculpture['Author'],
                                         "title": sculpture['title'],
                                         'file': file_name,
                                         'url': sculpture['url'],
                                         'Period': sculpture['Period']})

            # Dump over new json to file
            with open("../../../sculpture_data/nga/sculptures/nga_sculpture_data.json", "w+") as file:
                json.dump({"data": processed_sculptures}, file)

        file_num += 1

    df = pd.DataFrame(processed_sculptures)
    df.to_csv('../../../sculpture_data/nga/sculptures/nga_sculpture_periods.csv', sep=',')

    return df


def main():
    df = get_data()


if __name__ == "__main__":
    main()