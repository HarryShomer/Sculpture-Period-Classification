"""
Scrape the artist info for the Web Gallery of Art database and deposit in a CSV (wga_artists.csv).
"""
from bs4 import BeautifulSoup
import pandas as pd
from fake_useragent import UserAgent
from helpers import *


def create_artist_url(art_period):
    """
    Create the url for the given query
    
    :param art_period: Period of art we are getting the artists for
    
    :return: url
    """
    return art_period.join(["https://www.wga.hu/cgi-bin/artist.cgi?Profession=any&School=any&Period=",
                            "&Time-line=any&from=00&max=50000&Sort=Name&letter=-"])


def parse_artist_page(page):
    """
    Parse the Artist Html page
    
    :param page: html with artist info
    
    :return: DataFrame of artist info for that page
    """
    # Encoding is different from individual sculpture pages
    soup = BeautifulSoup(page, "lxml", from_encoding="ISO-8859-1")

    # Only 1 of this table on page
    table = soup.find_all('table', {'style': 'border: 0;', 'border': "1", "cellpadding": "4", "width": "700"})[0]

    # First row are the cols
    trs = table.find_all('tr')[1:]

    # Get All Artists
    artists = []
    for tr in trs:
        tds = tr.find_all('td')
        artists.append({'Artist': tds[1].get_text(), 'Period': tds[3].get_text()})

    return pd.DataFrame(artists)


def convert_artists():
    """
    Convert the Artist Html pages to a Pandas DataFrame and save as file
    
    Cols -> Artist, Style/Period
    Saved -> wga_artists.csv
    
    :return: None
    """
    dfs = []

    periods = ["Medieval", "Early%20Renaissance", "Northern%20Renaissance", "High%20Renaissance", "Mannerism",
               "Baroque", "Rococo", "Neoclassicism", "Romanticism", "Realism", "Impressionism"]

    # Create the fake_user object
    fake_user = UserAgent(cache=True)

    for period in periods:
        print("Scraping", period)
        response = get_page(create_artist_url(period), fake_user)
        dfs.append(parse_artist_page(response.content))

    # Combine all individual DataFrames and reset
    artists_df = pd.concat(dfs)
    artists_df = artists_df.reset_index(drop=True)

    # Write to file -> wga_artists.csv
    artists_df.to_csv("../../sculpture_data/wga/sculptures/wga_artists.csv", sep=',')


def main():
    convert_artists()


if __name__ == "__main__":
    main()
