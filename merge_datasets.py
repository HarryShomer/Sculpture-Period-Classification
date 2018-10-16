"""
Merge all the different datasets into one: WGA + NGA + WikiArt
"""

import pandas as pd
import dedupe
import unicodedata

# Duplicate sculptures to be deleted from master
# This was done informally by me...I'm pretty sure I caught a vast majority of it though
# NOTE: See 'notes.txt' for more info
DUP_SCULPTURES = ["wikiart_0551.jpg", "wikiart_0411.jpg", "wga_3788.jpg", "wga_1084.jpg", "wga_1092.jpg", "wikiart_0320.jpg",
                  "wikiart_0319.jpg", "nga_0062.jpg", "nga_0063.jpg", "nga_0099.jpg", "nga_0064.jpg", "nga_0066.jpg",
                  "nga_0067.jpg", "nga_0069.jpg", "nga_0070.jpg", "nga_0076.jpg", "nga_0071.jpg", "nga_0073.jpg",
                  "nga_0075.jpg", "nga_0077.jpg", "nga_0078.jpg", "nga_0081.jpg", "wikiart_0277.jpg", "nga_0082.jpg",
                  "nga_0083.jpg", "nga_0085.jpg", "nga_0084.jpg", "nga_0092.jpg", "nga_0086.jpg", "nga_0087.jpg",
                  "nga_0088.jpg", "nga_0089.jpg", "nga_0090.jpg", "nga_0091.jpg", "nga_0094.jpg", "nga_0096.jpg",
                  "wga_0656.jpg", "wga_0657.jpg", "wga_1246.jpg", "wga_1328.jpg", "wga_1192.jpg", "wikiart_0020.jpg",
                  "wga_1175.jpg", "wikiart_0035.jpg", "wga_1322.jpg", "wga_0342.jpg", "wikiart_0110.jpg", "wikiart_0124.jpg",
                  "wikiart_0130.jpg", "wga_0388.jpg", "wga_0360.jpg", "wga_0379.jpg", "wikiart_0117.jpg", "wikiart_0137.jpg",
                  "wga_0363.jpg", "wga_0423.jpg", "wga_0425.jpg", "wikiart_0135.jpg", "wga_0419.jpg", "wga_1751.jpg",
                  "wikiart_0083.jpg", "wga_2838.jpg", "wikiart_0093.jpg", "wga_2840.jpg", "wga_2862.jpg", "wikiart_0085.jpg",
                  "wikiart_0103.jpg", "wga_2932.jpg", "wikiart_0107.jpg", "wikiart_0072.jpg", "wikiart_0067.jpg",
                  "wikiart_0068.jpg", "wikiart_0060.jpg", "wikiart_0061.jpg", "wikiart_0092.jpg", "wikiart_0078.jpg",
                  "wikiart_0076.jpg", "wikiart_0090.jpg", "wikiart_0089.jpg", "wikiart_0088.jpg", "wikiart_0086.jpg",
                  "wikiart_0082.jpg"
                  ]


def fix_name_nga(artist):
    """
    Fix the name for NGA 
    
    :param artist: artist name
    
    :return: Fixed name
    """
    if "sculptor" in artist:
        return artist[:artist.find("sculptor")].strip()
    else:
        return artist.strip()


def fix_name_wiki(artist):
    """
    Fix the name for WikiArt 
    
    :param artist: artist name
    
    :return: Fixed name
    """
    if "Alonzo Cano" in artist:
        return "Alonso Cano"
    if "Michelangelo" in artist:
        return "Michelangelo Buonarroti"
    return artist


def fix_name_wga(artist):
    """
    Fix the name for WGA

    :param artist: artist name

    :return: Fixed name
    """
    comma = artist.find(",")

    return " ".join([artist[comma + 1:].strip(), artist[:comma].strip()]) if comma != -1 else artist


def fix_text(text):
    """
    By 'fix' I mean deal with encoding, get rid of newlines, convert to uppercase, and strip of leading/trailing 
    
    :param text: Title or Artist name
    
    :return: 'Fixed' text
    """
    ''.join((c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn'))
    text = text.replace('\n', '')
    text = text.upper()

    return text.strip()


def merge_datasets():
    """
    Merge All the datasets into one
    
    :return: None
    """
    wga_df = pd.read_csv('../sculpture_data/wga/sculptures/wga_sculpture_periods.csv', index_col=0)
    wikiart_df = pd.read_csv('../sculpture_data/wikiart/sculptures/wikiart_sculpture_periods.csv', index_col=0)
    nga_df = pd.read_csv('../sculpture_data/nga/sculptures/nga_sculpture_periods.csv', index_col=0)

    ######## Fix name for WGA and WikiaRt ###########
    wga_df['Author'] = wga_df.apply(lambda x: fix_name_wga(x['Author']), axis=1)
    wikiart_df['Author'] = wikiart_df.apply(lambda x: fix_name_wiki(x['Author']), axis=1)
    nga_df['Author'] = nga_df.apply(lambda x: fix_name_nga(x['Author']), axis=1)

    ## Append
    df = pd.concat([wga_df, wikiart_df, nga_df], ignore_index=True)

    #### Fix Author and Ttile
    df['Author_Fixed'] = df.apply(lambda x: fix_text(x['Author']), axis=1)
    df['title_fixed'] = df.apply(lambda x: fix_text(x['title']), axis=1)

    # Fix Periods#
    periods = ["BAROQUE", "EARLY RENAISSANCE", "MEDIEVAL", "NEOCLASSICISM", "HIGH RENAISSANCE", "MANNERISM",
               "MINIMALISM", "REALISM", "ROCOCO", "IMPRESSIONISM", "ROMANTICISM"]
    df['Period'] = df.apply(lambda row: row['Period'].upper(), axis=1)
    #############

    #### Get Desired Periods
    df = df[df['Period'].isin(periods)]
    df = df.sort_values(['Author_Fixed', 'title_fixed'])

    print("Combined Drop Rows:", df.shape[0] - df.drop_duplicates(subset=['Author_Fixed', 'title_fixed']).shape[0])

    df = df.drop_duplicates(subset=['Author_Fixed', 'title_fixed'], keep='last')

    # Drop Duplicate Sculptures
    df = df[~df['file'].isin(DUP_SCULPTURES)]

    print(df['Period'].value_counts())

    # df.to_csv("combined_wga_wiki.csv", sep=',')


def main():
    merge_datasets()
    """
    print(df.iloc[0])
    print(df.iloc[6683])

    df_dict = df.to_dict('index')


    fields = [
        {'field': 'Author_Fixed', 'type': 'String'},
        {'field': 'title_fixed', 'type': 'String'}
    ]

    deduper = dedupe.Dedupe(fields)

    deduper.sample(df_dict)


    print('starting active labeling...')

    dedupe.consoleLabel(deduper)

    threshold = deduper.threshold(df_dict, recall_weight=1)

    print('clustering...')
    clustered_dupes = deduper.match(df_dict, threshold)

    print('# duplicate sets', len(clustered_dupes))


    print("************************")
    print("Combined Drop Rows:", df.shape[0] - df.drop_duplicates(subset=['Author', 'title']).shape[0])
    """


if __name__ == "__main__":
    main()
