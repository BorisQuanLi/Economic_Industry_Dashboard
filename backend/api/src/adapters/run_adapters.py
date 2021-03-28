import csv
import pandas as pd
import api.src.models as models
import api.src.db as db
import api.src.adapters.client as client
from api.src.adapters.company_builder import CompanyBuilder
from api.src.adapters.quarter_report_builder import QuarterReportBuilder

class RequestAndBuildSP500Companies: # to be refactored
    def __init__(self):
        self.sp500_wiki_data_filepath = client.get_sp500_wiki_data()
        self.company_builder = CompanyBuilder()
        self.conn = db.conn
        self.cursor = self.conn.cursor()
        
    def run(self): # to be refactored, using Pandas?
        with open(self.sp500_wiki_data_filepath) as csv_file: # user pandas.read_csv() instead?
            reader = csv.DictReader(csv_file)
            sp500_companies_wiki_data = []
            for wiki_row in reader:
                company_obj = self.process_row_data(wiki_row)              
                sp500_companies_wiki_data.append(company_obj)
        return sp500_companies_wiki_data

    def process_row_data(self, wiki_row):
        sub_industry_name = wiki_row['GICS Sub-Industry']
        sub_industry_obj = (models.SubIndustry
                                .find_by_sub_industry_name(sub_industry_name, self.cursor))
        sub_industry_id = self.get_sub_industry_id(sub_industry_obj)
        company_obj = self.company_builder.run(wiki_row, sub_industry_id, self.conn, self.cursor)
        return company_obj

    def get_sub_industry_id(self, sub_industry_obj):
        if not sub_industry_obj:
            sector_name = wiki_row['GICS Sector']
            sub_industry_id = self.generate_sub_industry_id(sub_industry_name, sector_name)
        else:
            sub_industry_id = sub_industry_obj.__dict__['id'] 
        return sub_industry_id

    def generate_sub_industry_id(self, sub_industry_name, sector_name):
        sub_industry_dict = {'sub_industry_GICS': sub_industry_name, 'sector_GICS': sector_name}
        sub_industry_obj = models.SubIndustry(**sub_industry_dict)
        sub_industry_id = db.save(sub_industry_obj, self.conn, self.cursor).id
        return sub_industry_id 

class IngestBuildQuarterlyReports:
    API_KEY = "f269391116fc672392f1a2d538e93171" # to be saved in .env
    SP500_WIKI_DATA_FILEPATH = client.get_sp500_wiki_data()

    def __init__(self):
        self.quarter_reports_builder = QuarterReportBuilder()
        self.conn = db.conn
        self.cursor = self.conn.cursor()

    def run(self, number_api_calls = 3): # number_api_calls = 170
        sql_str = f"""SELECT * FROM companies 
                            LIMIT {number_api_calls}
                    """
        self.cursor.execute(sql_str)
        companies_records = self.cursor.fetchall()
        companies_objs = db.build_from_records(models.Company, companies_records)
        for company_obj in companies_objs:            
            ticker = company_obj.ticker
            company_id = company_obj.id
            self.quarter_reports_builder.run(ticker, company_id, self.conn, self.cursor)

    