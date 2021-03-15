import api.src.models as models
import api.src.db as db
import api.src.adapters as adapters
import psycopg2
import datetime
import csv

class CompanyBuilder:
    attributes = ['name', 'ticker', 'sub_industry_id', 'year_founded', 'number_of_employees', 'HQ_state']

    def run(self, info_row, sub_industry_id, conn, cursor):
        ticker = info_row['Ticker']
        if not db.find_by_ticker(models.Company, ticker, cursor):
            name = info_row['Security']
            year_founded = info_row['Founded']
            number_of_employees = info_row['Employees']
            hq_state = info_row['Headquarters Location'].split(', ')[1]
            values_vector = [name, ticker, sub_industry_id, year_founded, number_of_employees, hq_state]

            company_dict = dict(zip(self.attributes, values_vector))
            obj = models.Company(**company_dict)
            company_obj = db.save(obj, conn, cursor)
        else:
            company_obj = db.find_by_ticker(models.Company, ticker, cursor)
        return company_obj