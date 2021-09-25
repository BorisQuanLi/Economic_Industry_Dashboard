import csv
import pandas as pd
import api.src.models as models
import api.src.db as db
from .client import get_sp500_wiki_data
from .companies_builder import CompanyBuilder
from .quarterly_financials_builder import QuarterlyFinancialsBuilder
from .quarterly_price_pe_builder import QuarterlyPricePEBuilder

class BuildSP500Companies: 
    def __init__(self):
        """
        Iterate over the csv file extract from the Wikepedia web page with 
        name, ticker symbol, and other basic information of the S&P 500
        component stocks, and

        create models.Company object for each company and, if the models.SubIndustry
        object the company belongs to does not exist in the database, create a new  
        SubIndustry object.
        
        To be instantiated and called by
        backend $ python3 manage.py
        """
        self.sp500_wiki_data_filepath = get_sp500_wiki_data()
        self.company_builder = CompanyBuilder()
        self.conn = db.conn
        self.cursor = self.conn.cursor()
        
    def run(self): 
        with open(self.sp500_wiki_data_filepath) as csv_file:
            reader = csv.DictReader(csv_file)
            for wiki_row in reader:
                self.process_row_data(wiki_row)     

    def process_row_data(self, wiki_row):
        sub_industry_name = wiki_row['GICS Sub-Industry']
        sub_industry_obj = (models.SubIndustry
                                .find_by_sub_industry_name(sub_industry_name, self.cursor))
        sub_industry_id = self.get_sub_industry_id(sub_industry_obj, sub_industry_name, wiki_row)
        company_obj = self.company_builder.run(wiki_row, sub_industry_id, self.conn, self.cursor)

    def get_sub_industry_id(self, sub_industry_obj, sub_industry_name, wiki_row):
        if not sub_industry_obj:
            sector_name = wiki_row['GICS Sector']
            sub_industry_id = self.generate_sub_industry_id(sub_industry_name, sector_name)
        else:
            sub_industry_id = sub_industry_obj.__dict__['id'] 
        return sub_industry_id

    def generate_sub_industry_id(self, sub_industry_name, sector_name):
        """
        In the event that a new sub-industry is returned from the API call (its name
        has not been written into the db), create a new row in the sub_industries table,
        return its ID number.
        """
        sub_industry_dict = {'sub_industry_GICS': sub_industry_name, 'sector_GICS': sector_name}
        sub_industry_obj = models.SubIndustry(**sub_industry_dict)
        sub_industry_id = db.save(sub_industry_obj, self.conn, self.cursor).id
        return sub_industry_id 

class BuildQuarterlyReportsPricesPE:
    def __init__(self, conn, cursor):
        self.conn = conn
        self.cursor = cursor
        
    def run(self, sector_name:str): 
        companies_objs = db.find_company_objs_by_sector(models.Company, sector_name, self.cursor)
        for company_obj in companies_objs:            
            if not models.QuarterlyReport.find_by_company_id(company_obj.id, self.cursor):
                quarterly_financials_builder = QuarterlyFinancialsBuilder(company_obj.ticker, self.conn, self.cursor)
                quarterly_financials_builder.run(company_obj.id)
            if not models.PricePE.find_by_company_id(company_obj.id, self.cursor):
                quarterly_price_pe_builder = QuarterlyPricePEBuilder(company_obj.ticker, self.conn, self.cursor)
                quarterly_price_pe_builder.run(company_obj.id)
    