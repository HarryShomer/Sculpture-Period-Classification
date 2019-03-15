"""
This file creates the directory structure and needed to hold the files and scrapes everything.

Before you start download the catalog.csv file from the WGA database (https://www.wga.hu/index1.html 
go to database and then download). and place it in the scrape_wga directory
"""
import os
import scrape_nga
import scrape_wga
import scrape_wikiart


styles = periods = ["BAROQUE", "EARLY RENAISSANCE", "MEDIEVAL", "NEOCLASSICISM", "HIGH RENAISSANCE", "MINIMALISM",
                    "REALISM", "IMPRESSIONISM", "ROCOCO", "SURREALISM", "MANNERISM", "ROMANTICISM",
                    ]

file_dir = os.path.dirname(os.path.realpath(__file__))

# Create the directory structure if needed
if not os.path.isdir(os.path.join(file_dir, "../../sculpture_data")):
    os.mkdir(os.path.isdir(os.path.join(file_dir, "../../sculpture_data")))

    os.mkdir(os.path.isdir(os.path.join(file_dir, "../../sculpture_data/wga")))
    os.mkdir(os.path.isdir(os.path.join(file_dir, "../../sculpture_data/wga/sculptures")))
    os.mkdir(os.path.isdir(os.path.join(file_dir, "../../sculpture_data/wga/sculpture_images")))

    os.mkdir(os.path.isdir(os.path.join(file_dir, "../../sculpture_data/wikiart")))
    os.mkdir(os.path.isdir(os.path.join(file_dir, "../../sculpture_data/wikiart/sculptures")))
    os.mkdir(os.path.isdir(os.path.join(file_dir, "../../sculpture_data/wikiart/sculpture_images")))

    os.mkdir(os.path.isdir(os.path.join(file_dir, "../../sculpture_data/nga")))
    os.mkdir(os.path.isdir(os.path.join(file_dir, "../../sculpture_data/nga/sculptures")))
    os.mkdir(os.path.isdir(os.path.join(file_dir, "../../sculpture_data/nga/sculpture_images")))

    os.mkdir(os.path.isdir(os.path.join(file_dir, "../../sculpture_data/model_data")))
    os.mkdir(os.path.isdir(os.path.join(file_dir, "../../sculpture_data/model_data/classes_12")))

    for data_folder in ['train', 'validation', 'test']:
        for style in styles:
            os.mkdir(os.path.isdir(os.path.join(file_dir, "../../sculpture_data/model_data/classes_12",
                                                f"{data_folder}/{style}")))


# Can now scrape all the data
scrape_wikiart.scrape_sculptures.get_data()
scrape_wga.scrape_artist.convert_artists()
scrape_wga.process_sculptures.get_data()
scrape_nga.scrape_sculptures.get_data()





