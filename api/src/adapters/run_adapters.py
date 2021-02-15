import api.src.models as models
import api.src.db as db
import api.src.adapters as adapters
import psycopg2

class RequestAndBuildSubIndustries:
    def __init__(self):
        self.client = adapters.SubIndustryClient() # from client.py
        self.sub_industry_builder = adapters.SubIndustryBuilder() # from sub_industries_builder.py
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

class RequestAndBuildCompanies:
    def __init__(self):
        self.client = adapters.CompanyClient()
        self.company_builder = adapters.CompanyBuilder()
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

