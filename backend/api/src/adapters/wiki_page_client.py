import json
from api.data.ingest_sp500_info import ingest_sp500_stocks_info

def get_sp500_wiki_data():
    if not sp500_data_file_exists():
        sp500_wiki_data_filepath = ingest_sp500_stocks_info()
    else:
        sp500_wiki_data_filepath = sp500_data_file_exists()      
    return sp500_wiki_data_filepath

def sp500_data_file_exists():
    sp500_wiki_data_filepath = "./api/data/sp500/raw_data/sp500_stocks_wiki_info.csv"
    try: 
        existing_file = open(sp500_wiki_data_filepath, 'r')
        if existing_file:
            existing_file.close()
            return sp500_wiki_data_filepath
    except:
        return False