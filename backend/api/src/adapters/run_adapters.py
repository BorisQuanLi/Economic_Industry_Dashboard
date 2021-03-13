import csv
import api.src.models as models
import api.src.db as db
from apir.src.adpaters.client import CompaniesClient, CompanyBuilder
import psycopg2

class RequestAndBuildSP500Companies:
    def __init__(self):
        self.client = CompaniesClient() # from adapter.client.py
        self.company_builder = CompanyBuilder()
        self.conn = db.conn
        self.cursor = self.conn.cursor()
    
    def generate_sub_industry_id(self, sub_industry_name, sector_name):
        sub_industry_dict = {'sub_industry_GICS': sub_industry_name, 'sector_GICS': sector_name}
        sub_industry_obj = models.SubIndustry(**sub_industry_dict)
        sub_industry_id = db.save(sub_industry_obj, self.conn, self.cursor).id
        return sub_industry_id 
        
    def run(self):
        sp500_wiki_data_filepath = self.client.get_sp500_companies_info()
        with open(sp500_wiki_data_filepath) as csv_file:
            reader = csv.DictReader(csv_file)
            sp500_companies_wiki_data = []
            for wiki_row in reader:
                sub_industry_name = wiki_row['GICS Sub-Industry']
                try:
                    sub_industry_obj = (models.SubIndustry
                                            .find_by_sub_industry_name(sub_industry_name, self.cursor))
                    sub_industry_id = sub_industry_obj.__dict__['id']
                except Exception as e:
                    print(e)
                    sector_name = wiki_row['GICS Sector']
                    sub_industry_id = self.generate_sub_industry_id(sub_industry_name, sector_name)
                # send wiki_row and sub_industry_id to a function to build a company object
                company_obj = self.company_builder.run(wiki_row, sub_industry_id, self.conn, self.cursor)
                sp500_companies_wiki_data.append(company_obj)
        return None # return a list of Company objects

class RequestAndBuildCompany:
    def __init__(self):
        self.client = CompanyClient() # from adapter/client.py
        self.company_builder = CompanyBuilder()
        self.conn = psycopg2.connect(database = 'investment_analysis', 
                                        user = 'postgres', 
                                        password = 'postgres')
        self.cursor = self.conn.cursor()


class RequestAndBuildSubIndustries:
    def __init__(self):
        self.client = SubIndustryClient() # from client.py
        self.sub_industry_builder = SubIndustryBuilder() # from sub_industries_builder.py
        self.conn = psycopg2.connect(database = 'investment_analysis', 
                                        user = 'postgres', 
                                        password = 'postgres')
        self.cursor = self.conn.cursor()

    def run(self, sector_name):
        """
        returns a list of sub-industry objects in the same sector passed in as the argument.
        """
        sector_name, sub_industries_names = self.client.get_sub_industries(sector_name)
        sub_industry_objs = []
        for sub_industry_name in sub_industries_names:
            sub_industry_obj = self.sub_industry_builder.run(sector_name, sub_industry_name,
                                                                self.conn, self.cursor)
            sub_industry_objs.append(sub_industry_obj)
        return sub_industry_objs

class RequestAndBuildCompaniesBySubIndustry:
    def __init__(self):
        self.client = CompanyClient()
        self.company_builder = CompanyBuilder()
        self.conn = psycopg2.connect(database = 'investment_analysis', 
                                        user = 'postgres', 
                                        password = 'postgres')
        self.cursor = self.conn.cursor()

    def run(self, sub_industry_name):
        # obtain values of al the Company from adpaters.client
        companies_in_sub_industry = self.client.get_companies_by_sub_industry(sub_industry_name)
        company_objs = []
        for company_info_sp500 in companies_in_sub_industry:
            company_obj = self.company_builder.run(company_info_sp500, sub_industry_name, self.conn, self.cursor)
            if type(company_obj) == str:
                print(company_obj)
                continue
            company_objs.append(company_obj)
        return company_objs

