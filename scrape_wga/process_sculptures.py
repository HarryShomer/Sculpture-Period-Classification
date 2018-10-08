"""
Process the data for the sculptures from the Web Gallery of Art Database. 
This includes:
1. Narrowing the total catalog down to what we want
2. Scraping the info off of the website and storing it
3. Merging with 'wga_authors.csv' to get the art period

Note: The catalog is downloaded from their website - https://www.wga.hu/index1.html (go to database and then download)
"""

# TODO: Get all duplicate titles (by author!!!!!) and pick the pic we want to go with
# TODO: OR do we keep them as alternate views (or at least some of them)????

import pandas as pd
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import json
from helpers import *


def fix_artist_name(name):
    """
    Fix the artist name. Some are misspelled. 
    
    :param name: Given Artists name
    
    :return: Same/Fixed Name
    """
    name_fixes = {
                   "BELLANO, Bartolommeo": "BELLANO, Bartolomeo",
                   "CARNERI, Mattia": "CARNERI, Matteo",
                   "GUILLAUME, Jean-Baptiste-Claude-Eugčne": "GUILLAUME, Jean-Baptiste-Claude-Eugène",
                   "HÉBERT, Pierre-Eugčne-Emile": "HÉBERT, Pierre-Eugène-Emile",
                   "HERNÁNDEZ ESTRADA, Jerónimo": "HERNANDEZ, Jeronimo",
                   "MASTER PAUL of Lőcse": "MASTER PAUL of Löcse",
                   "OUDINÉ, Eugčne André": "OUDINÉ, Eugène André",
                   "SIMONIS, Eugčne": "SIMONIS, Eugène",
                   "TURA, Cosmč": "TURA, Cosmè",
                   "VASSALLETTO, marble worker family": "VASSALLETTO, Pietro",
                   "VEYRIER, Christophe": "VEYRIER, Cristophe",
                   "VIOLLET-LE-DUC, Eugčne-Emmanuel": "VIOLLET-LE-DUC, Eugène-Emmanuel"
    }

    return name_fixes.get(name, name)


def parse_sculpture_page(url, fake_user, file_name):
    """
    Parse info from page:
    1. Get Name of artist (name's in catalog.csv have unicode issues)
    2. Save image
    
    :param url: url for given sculpture 
    :param fake_user: Fake user agent object
    
    :return: artist name for sculpture
    """
    # Get and soupify page
    soup = BeautifulSoup(get_page(url, fake_user).content, 'lxml')

    # Get Artist Name (name from catalog.csv is fucked up)
    name = soup.findAll("div", {"class": "INDEX2"})[0].text

    # Image Url
    # Only one matching td tag
    td = soup.findAll("td", {'width': "30%"})[0]
    image_url_base = td.find("a")["href"]
    url = ''.join(["https://www.wga.hu", image_url_base])

    # Check to see if we want to scrape and save the image
    scrape_image(file_name, url, fake_user, "wga")

    return name


def get_data():
    """
    Get The final dataset for wga.
    
    :return: CSV with data
    """
    art_df = pd.read_csv("../../sculpture_data/wga/sculptures/catalog.csv", sep=None)

    # Only read in relevant info
    # 1. Sculptures
    # 2. Not 'UNKNOWN MASTER'
    # 3. Author, title, and url
    art_df = art_df[(art_df.FORM == "sculpture") & (~art_df["AUTHOR"].str.contains('UNKNOWN MASTER'))]
    art_df = art_df[["AUTHOR", "TITLE", "URL"]]

    # Create the fake_user object
    fake_user = UserAgent(cache=True)

    # Counter for determining file_name
    # e.g. 0005, 0050, 0467, 2350...etc.
    file_num = 0

    # Load data already processed
    processed_sculptures = json.loads(open("../../sculpture_data/wga/sculptures/wga_sculpture_data.json", 'r').read())['data']

    # Get files already processed - can easily look if scraped
    files_processed = [x['file'] for x in processed_sculptures]

    # Iterate through data
    # Create new DataFrame and save data
    for sculpture in art_df.to_dict("records"):
        file_name = "".join(["wga_", format(file_num, '04d'), ".jpg"])

        # If we already parsed and scraped - don't bother
        if file_name not in files_processed:
            print(file_name)

            # Parse and append
            name = parse_sculpture_page(sculpture['URL'], fake_user, file_name)
            processed_sculptures.append({'Author': name, "title": sculpture['TITLE'], 'file': file_name, 'url': sculpture['URL']})

            # Dump over new json to file
            # Can take a while so can start up easier
            with open("../../sculpture_data/wga/sculptures/wga_sculpture_data.json", "w+") as file:
                json.dump({"data": processed_sculptures}, file)

        file_num += 1

    return pd.DataFrame(processed_sculptures)


def merge_sculpture_artist(sculpture_df):
    """
    Merge the DataFrame with the sculpture info with "wga_artists.csv" to get the period for each sculpture
    
    Deposit the end result in -> 'wgu_sculpture_periods.csv'
    
    :param sculpture_df: DataFrame of info for each sculpture
    
    :return: None
    """
    artist_df = pd.read_csv("../../sculpture_data/wga/sculptures/wga_artists.csv", index_col=0)
    artist_df = artist_df.rename(index=str, columns={"Artist": "Author"})

    # Deal with inconsistent names
    sculpture_df['Author'] = sculpture_df.apply(lambda row: fix_artist_name(row['Author']), axis=1)

    # Merge and drop the couple of duplicates (only 3 examples)
    df = pd.merge(sculpture_df, artist_df, how="left", on="Author")
    df = df.drop_duplicates(subset=['file'])

    # Can fill in Period for these though we don't know the name
    df['Period'] = df.apply(lambda row: "Medieval" if "MEDIEVAL" in row['Author'] else row['Period'], axis=1)

    #### Print Counts ####
    print("\nNumber of Sculptures by Period")
    print(df['Period'].value_counts())

    df.to_csv('../../sculpture_data/wga/sculptures/wgu_sculpture_periods.csv', sep=',')


def get_dup_sculptures():
    """
    Get the duplicate sculptures
    
    :return: None
    """
    df = pd.read_csv('../../sculpture_data/wga/sculptures/wgu_sculpture_periods.csv', sep=',')
    df2 = df[df.duplicated(subset=['Author', 'title'], keep=False)]

    df2.to_csv("../../sculpture_data/wga/sculptures/duplicate_sculptures.csv", sep=',')


def main():
    df = get_data()
    merge_sculpture_artist(df)
    #get_dup_sculptures()


if __name__ == "__main__":
    main()
