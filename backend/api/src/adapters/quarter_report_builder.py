import api.src.models as models
import api.src.db as db
import api.src.adapters as adapters
import psycopg2
import datetime
import csv

class QuarterReportBuilder:
    attributes = ['id', 'date', 'company_id', 'revenue', 'net_income', 'earnings_per_share']
    
    def run(self, info_row, sub_industry_id, conn, cursor):
        ticker = info_row['Ticker']
        if not db.find_by_ticker(models.Company, ticker, cursor):
            company_obj = self.make_company_obj(info_row)
        else:
            company_obj = db.find_by_ticker(models.Company, ticker, cursor)
        return company_obj

    def make_company_obj(row):
        name, year_founded, number_of_employees, hq_state = self.extract_col_values(row)
        values_vector = [name, ticker, sub_industry_id, year_founded, number_of_employees, hq_state]
        company_dict = dict(zip(self.attributes, values_vector))
        obj = models.Company(**company_dict)
        company_obj = db.save(obj, conn, cursor)
        return company_obj
    
    def extract_col_values(self, row):
        name = info_row['Security']
        year_founded = info_row['Founded']
        number_of_employees = info_row['Employees']
        hq_state = info_row['Headquarters Location'].split(', ')[1]
        return name, year_founded, number_of_employees, hq_state