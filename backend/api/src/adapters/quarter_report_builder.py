import psycopg2
from urllib.request import urlopen
import json
from datetime import datetime, timedelta
import csv
import api.src.models as models
import api.src.db as db
import api.src.adapters as adapters

class QuarterReportBuilder:
    attributes = ['date', 'company_id', 'revenue', 'net_income', 'earnings_per_share'] 
    API_KEY = "f269391116fc672392f1a2d538e93171" # to be saved in .env

    def run(self, ticker, company_id, conn, cursor):
        self.conn = conn
        self.cursor = cursor
        if not db.find(models.QuarterlyReport, company_id, cursor):
            recent_five_quarterly_report_records = self.get_quarterly_ic(ticker)
            self.save_quarterly_records(company_id, recent_five_quarterly_report_records)
        else:
            pass

    def get_quarterly_ic(self, ticker, api_key= API_KEY):
        response = urlopen(f"https://financialmodelingprep.com/api/v3/income-statement/{ticker}?period=quarter&apikey={api_key}")
        data = response.read().decode("utf-8")
        qtr_ic =  json.loads(data)
        breakpoint()
        recent_five_quarterly_report_records = qtr_ic[:5]
        return recent_five_quarterly_report_records

    def save_quarterly_records(self, company_id, quarterly_ic_records):
        quarterly_reports_objs = []
        for quarterly_ic_record in quarterly_ic_records:
            quarterly_report_obj = self.save_quarterly_record(company_id, quarterly_ic_record)
        return quarterly_reports_objs

    def save_quarterly_record(self, company_id, quarterly_ic_record):
        values_vector = self.get_values_vector(quarterly_ic_record, company_id)
        quarter_report_dict = dict(zip(self.attributes, values_vector))
        obj = models.QuarterlyReport(**quarter_report_dict)
        quarterly_report_obj = db.save(obj, self.conn, self.cursor)
        return quarterly_report_obj
    
    def get_values_vector(self, quarterly_ic_record, company_id):
        date = self.convert_to_sql_date(quarterly_ic_record['date'])
        values_vector = [date,
                         company_id,
                         quarterly_ic_record['revenue'],
                         quarterly_ic_record['netIncome'],
                         quarterly_ic_record['eps']]
        return values_vector

    def convert_to_sql_date(self, date_str:str):
        sql_str = f"""SELECT TO_DATE (cast({date_str} as TEXT), 'YYYY-MM-DD');"""
        self.cursor.execute(sql_str)
        return self.cursor.fetchone()