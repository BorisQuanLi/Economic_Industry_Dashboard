import api.src.models as models
import api.src.db as db
import api.src.adapters as adapters
from api.data.data_ingestion_processing.get_companies_info import via_intrinio_api
import psycopg2
import datetime

class CompanyBuilder:
    attributes = ['name', 'ticker', 'sub_industry_id', 'year_founded', 'number_of_employees', 'HQ_state', 'country']
    
    def run(self, company_info_sp500, sub_industry_name, conn, cursor):
        year_founded = company_info_sp500['Founded']
        sub_industry_name = company_info_sp500['GICS Sub-Industry']
        ticker = company_info_sp500['Symbol']
        sub_industry_obj = models.SubIndustry.find_by_sub_industry_name(sub_industry_name, cursor)
        sub_industry_id = sub_industry_obj.__dict__['id']
        company_info_dict = via_intrinio_api(ticker)
        if type(company_info_dict) == tuple:
            return f"{ticker} info not available from Intrinio API."
        name = company_info_dict['name']
        number_of_employees = company_info_dict['number_of_employees']
        HQ_state = company_info_dict['HQ_state']
        country = company_info_dict['country']

        values = [name, ticker, sub_industry_id, year_founded, number_of_employees, HQ_state, country]
        company_dict = dict(zip(self.attributes, values))
        company_obj = models.Company(**company_dict)
        company_obj = db.save(company_obj, conn, cursor)
        return company_obj