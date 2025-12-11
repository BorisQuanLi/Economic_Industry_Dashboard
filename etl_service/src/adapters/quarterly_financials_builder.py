from urllib.request import urlopen
import json
import etl_service.src.models as models
import etl_service.src.db as db
from etl_service.settings import API_KEY

class QuarterlyFinancialsBuilder:
    financials_attributes = ['date', 'company_id', 'revenue', 'net_income', 'earnings_per_share', 'profit_margin'] 
    
    def __init__(self, ticker, conn, cursor):
        self.conn = conn
        self.cursor = cursor
        self.ticker = ticker
        self.recent_eight_quarterly_ic_statement_records = self.get_quarterly_financials(ticker)

    def get_quarterly_financials(self, ticker, number_of_quarters=8):
        response = urlopen(f"https://financialmodelingprep.com/api/v3/income-statement/{ticker}?period=quarter&limit={number_of_quarters}&apikey={API_KEY}")
        data = response.read().decode("utf8")
        quarterly_income_statements = json.loads(data)
        # skip record with an invalid revenue value of 0
        recent_eight_quarterly_ic_statement_records = [quarterly_record for quarterly_record in quarterly_income_statements
                                                                            if int(quarterly_record['revenue']) != 0]
        return recent_eight_quarterly_ic_statement_records

    def run(self, company_id):       
        self.save_quarterly_financials_records(company_id)

    def save_quarterly_financials_records(self, company_id):
        if not db.find(models.QuarterlyReport, company_id, self.cursor):
            for quarterly_record in self.recent_eight_quarterly_ic_statement_records:
                self.save_quarterly_record(company_id, quarterly_record)             

    def save_quarterly_record(self, company_id, quarterly_record):
        values_vector = self.get_financials_vector(quarterly_record, company_id)
        quarter_report_dict = dict(zip(self.financials_attributes, values_vector))
        obj = models.QuarterlyReport(**quarter_report_dict)
        db.save(obj, self.conn, self.cursor)
        
    def get_financials_vector(self, quarterly_record, company_id):
        profit_margin = round(100 * quarterly_record['netIncome']
                                / quarterly_record['revenue'], 2)
        values_vector = [quarterly_record['date'],
                         company_id,
                         quarterly_record['revenue'],
                         quarterly_record['netIncome'],
                         round(quarterly_record['eps'], 2),
                         profit_margin]
        return values_vector
