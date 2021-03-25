import csv
import api.src.models as models
import api.src.db as db
import api.src.adapters.client as client
from api.src.adapters.company_builder import CompanyBuilder
from api.src.adapters.quarter_report_builder import QuarterReportBuilder
import psycopg2

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

class IngestQuarterlyReports:
    API_KEY = "f269391116fc672392f1a2d538e93171" # to be saved in .env
    def __init__(self, ticker):
        self.ticker = ticker
        self.quarter_reports_builder = QuarterReportBuilder()
        self.conn = db.conn
        self.cursor = self.conn.cursor()

    def get_quarterly_reports(self, ticker):
        response = urlopen(f"https://financialmodelingprep.com/api/v3/income-statement/{ticker}?period=quarter&apikey={self.API_KEY}")
        data = response.read().decode("utf-8")
        qtr_ic = json.loads(data)
        recent_five_quarters = qtr_ic[:5]
        quarterly_reports = self.extract_col_values(recent_five_quarters)
        return quarterly_reports

    def extract_col_values(self, recent_five_quarters):
        quarterly_reports = list()
        for quarter in recent_five_quarters:
            quarterly_reports.append({'date': apple_qtr_ic[0]['date'],
                                    'revenue': apple_qtr_ic[0]['revenue'],
                                    'netIncome': apple_qtr_ic[0]['netIncome'],
                                    'eps': apple_qtr_ic[0]['eps']})
        return quarterly_reports

