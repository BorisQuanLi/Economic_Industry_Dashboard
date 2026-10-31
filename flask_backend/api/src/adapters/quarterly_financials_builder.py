from urllib.request import urlopen
import json
import os


class QuarterlyFinancialsBuilder:
    financials_attributes = ['date', 'company_id', 'revenue', 'net_income', 'earnings_per_share', 'profit_margin']

    def __init__(self, ticker, conn, cursor):
        self.conn = conn
        self.cursor = cursor
        self.ticker = ticker
        self.recent_eight_quarterly_ic_statement_records = self.get_quarterly_financials(ticker)

    def get_quarterly_financials(self, ticker, number_of_quarters=8):
        api_key = os.getenv("API_KEY", "")
        response = urlopen(
            f"https://financialmodelingprep.com/api/v3/income-statement/{ticker}"
            f"?period=quarter&limit={number_of_quarters}&apikey={api_key}"
        )
        data = response.read().decode("utf8")
        quarterly_income_statements = json.loads(data)
        return [r for r in quarterly_income_statements if int(r['revenue']) != 0]

    def run(self, company_id):
        self.save_quarterly_financials_records(company_id)

    def save_quarterly_financials_records(self, company_id):
        for quarterly_record in self.recent_eight_quarterly_ic_statement_records:
            self.save_quarterly_record(company_id, quarterly_record)

    def save_quarterly_record(self, company_id, quarterly_record):
        values_vector = self.get_financials_vector(quarterly_record, company_id)
        _ = dict(zip(self.financials_attributes, values_vector))

    def get_financials_vector(self, quarterly_record, company_id):
        profit_margin = round(
            100 * quarterly_record['netIncome'] / quarterly_record['revenue'], 2
        )
        return [
            quarterly_record['date'],
            company_id,
            quarterly_record['revenue'],
            quarterly_record['netIncome'],
            round(quarterly_record['eps'], 2),
            profit_margin,
        ]
