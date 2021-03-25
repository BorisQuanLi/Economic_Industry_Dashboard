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
        open(sp500_wiki_data_filepath)
        return sp500_wiki_data_filepath
    except:
        return False

# may not need to define these Classes:

class SubIndustryClient:
    sub_industries_by_sector_file_path = "./api/data/sp500/processed_data/sub_industries.json"
    with open(sub_industries_by_sector_file_path) as reader:
        json_str = reader.read()
        SECTOR_SUB_INDUSTRIES_DICT = json.loads(json_str)

    def get_sub_industries_by_sector(self, sector_name):
        sub_industries_names = self.SECTOR_SUB_INDUSTRIES_DICT[sector_name]
        return sector_name, sub_industries_names


class CompaniesBySubIndustryClient:
    companies_by_sub_industry_file_path =  "./api/data/sp500/processed_data/companies_by_sub_industry.json"
    # columns = ['id', 'name', 'ticker', 'sub_industry_id', 'year_founded', 'number_of_employees', 'HQ_state', 'country']
    with open(companies_by_sub_industry_file_path) as sub_industry_companies:
        sub_industry_companies_dict_str = sub_industry_companies.read()
        SUB_INDUSTRY_COMPANIES_DICT = json.loads(sub_industry_companies_dict_str)

    def get_companies_by_sub_industry(self, sub_industry_name):
        companies_in_sub_industry = self.SUB_INDUSTRY_COMPANIES_DICT[sub_industry_name]
        return companies_in_sub_industry