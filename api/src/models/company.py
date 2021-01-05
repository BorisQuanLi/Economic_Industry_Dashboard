from api.src.db import db
import api.src.models as models


class Company:
    __table__ = "companies"
    columns = ['id', 'name', 'ticker', 'sub_industry_id', 'year_founded', 'number_of_employees', 'HQ_state', 'country']

    def __init__(self, **kwargs):
        for key in kwargs.keys():
            if key not in self.columns:
                raise f'{key} not in {self.columns}'
        for k, v in kwargs.items():
            setattr(self, k, v)

    @classmethod
    def find_by_stock_ticker(self, stock_ticker, cursor):
        ticker_query = """SELECT * FROM companies WHERE ticker = %s;"""
        cursor.execute(ticker_query, (stock_ticker,))
        company_record = cursor.fetchone()
        return db.build_from_record(models.Company, company_record)

    @classmethod
    def find_by_company_id(self, company_id, cursor):
        sql_query = f"""SELECT * FROM {self.__table__}
                        WHERE id = %s;"""
        cursor.execute(sql_query, (company_id,))
        record = cursor.fetchone()
        return db.build_from_record(models.Company, record)

    def sub_industry(self, cursor):
        sql_query = f"""SELECT * FROM sub_industries 
                    WHEER sub_industries.id = %s;
                    """
        cursor.execute(sql_query, (self.sub_industry_id,))
        return db.build_from_record(models.SubIndustry, cursor.fetchone())
    
    def price_pe(self, cursor):
        pass

    def quarterly_reports(self, cursor):
        sql_query = f"""SELECT * FROM quarterly_reports
                    WHERE quarterly_reports.company_id = %s;"""
        cursor.execute(sql_query, (self.id,))
        records = cursor.fetchall()
        return db.build_from_records(models.QuarterlyReport, records) 
    
    def to_quarterly_reports_prices_pe_json_by_ticker(self, cursor):
        quarterly_reports_prices_pe_json = self.__dict__
        quarterly_reports_sql_query = f"""SELECT * from quarterly_reports
                                        JOIN companies
                                        ON companies.id = quarterly_reports.company_id
                                        WHERE companies.ticker = %s;
                                    """
        cursor.execute(quarterly_reports_sql_query, (self.ticker,))
        records = cursor.fetchall()
        quarterly_reports_obj = db.build_from_records(models.QuarterlyReport ,records)
        quarterly_reports_prices_pe_json['History of quarterly financials'] = [
                            report_obj.__dict__ for report_obj in quarterly_reports_obj]

        price_pe_sql_query = f"""SELECT * from prices_pe 
                                JOIN companies
                                ON companies.id = prices_pe.company_id
                                WHERE companies.ticker= %s;
                                """
        cursor.execute(price_pe_sql_query, (self.ticker,))
        records = cursor.fetchall()
        prices_pe_obj = db.build_from_records(models.PricePE, records)
        quarterly_reports_prices_pe_json['History of quarterly Closing Price and Price to Earnings ratios'] = [
                            price_pe_obj.__dict__ for price_pe_obj in prices_pe_obj]
        return quarterly_reports_prices_pe_json

    def search_quarterly_report_by_ticker(self, ticker_params, cursor):
        pass
        ticker = ticker_params.values()[0]
        company = find_by_stock_ticker(ticker)
        # check if company is a Company object?
        # company_id = company.
        return   quarterly_report()


    