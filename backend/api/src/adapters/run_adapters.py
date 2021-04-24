import csv
import pandas as pd
import api.src.models as models
import api.src.db as db
from .client import get_sp500_wiki_data
from .companies_builder import CompanyBuilder
from .quarterly_financials_prices_pe_builder import QuarterFinancialsPricePEBuilder

class BuildSP500Companies: # to be refactored
    def __init__(self):
        self.sp500_wiki_data_filepath = get_sp500_wiki_data()
        self.company_builder = CompanyBuilder()
        self.conn = db.conn
        self.cursor = self.conn.cursor()
        
    def run(self): # to be refactored, using Pandas?
        with open(self.sp500_wiki_data_filepath) as csv_file: # user pandas.read_csv() instead?
            reader = csv.DictReader(csv_file)
            for wiki_row in reader:
                company_obj = self.process_row_data(wiki_row)              

    def process_row_data(self, wiki_row):
        sub_industry_name = wiki_row['GICS Sub-Industry']
        sub_industry_obj = (models.SubIndustry
                                .find_by_sub_industry_name(sub_industry_name, self.cursor))
        sub_industry_id = self.get_sub_industry_id(sub_industry_obj, sub_industry_name, wiki_row)
        company_obj = self.company_builder.run(wiki_row, sub_industry_id, self.conn, self.cursor)
        return company_obj

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
        companies_objs = self.get_sector_companies_objs(sector_name)
        for company_obj in companies_objs:            
            if not models.QuarterlyReport.find_by_company_id(company_obj.id, self.cursor):
                financials_prices_pe_builder = QuarterFinancialsPricePEBuilder(company_obj.ticker, self.conn, self.cursor)
                financials_prices_pe_builder.run(company_obj.id, sector_name)
            else: continue
        
    def get_sector_companies_objs(self, sector_name):
        sql_str = f"""SELECT * FROM companies
                        JOIN sub_industries 
                        ON companies.sub_industry_id::INT = sub_industries.id
                        WHERE sub_industries.sector_gics = '{sector_name}';
                    """
        self.cursor.execute(sql_str)
        companies_records = self.cursor.fetchall()
        companies_objs = db.build_from_records(models.Company, companies_records)
        return companies_objs
    