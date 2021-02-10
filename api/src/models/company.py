from api.src.db import db
import api.src.models as models


class Company:
    __table__ = "companies"
    columns = ['id', 'name', 'ticker', 'sub_industry_id', 'year_founded', 'number_of_employees', 'HQ_state', 'country']

    def __init__(self, **kwargs):
        # possible error: TypeError: exceptions must derive from BaseException
        """
        for key in kwargs.keys():
            if key not in self.columns:
                raise f'{key} not in {self.columns}'
        """
        for k, v in kwargs.items():
            setattr(self, k, v)

    @classmethod
    def find_by_stock_ticker(self, stock_ticker:str, cursor):
        """
        returns a Company object, with values in all the fields, based on its ticker.
        """
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
        """
        Returns the names of the sub_industry and sector that a company belongs to.
        """
        sql_query = f"""SELECT * FROM sub_industries 
                    WHERE sub_industries.id = %s;
                    """
        cursor.execute(sql_query, (self.sub_industry_id,))
        return db.build_from_record(models.SubIndustry, cursor.fetchone())

    def quarterly_prices_pe(self, cursor):
        sql_query = f"SELECT * FROM prices_pe WHERE prices_pe.company_id = %s;"
        cursor.execute(sql_query, (self.id,))
        record = cursor.fetchall()
        return db.build_from_records(models.PricePE, record)

    def quarterly_reports(self, cursor):
        sql_query = f"""SELECT * FROM quarterly_reports
                    WHERE quarterly_reports.company_id = %s;"""
        cursor.execute(sql_query, (self.id,))
        records = cursor.fetchall()
        return db.build_from_records(models.QuarterlyReport, records) 
    
    def to_quarterly_financials_json(self, cursor):
        quarterly_reports_prices_pe_json = self.__dict__
        quarterly_reports_obj = self.quarterly_reports(cursor)
        quarterly_reports_prices_pe_json['Quarterly financials'] = [
                            report_obj.__dict__ for report_obj in quarterly_reports_obj]

        prices_pe_obj = self.quarterly_prices_pe(cursor)
        quarterly_reports_prices_pe_json['Quarterly Closing Price and P/E ratio'] = [
                                                    price_pe_obj.__dict__ for price_pe_obj in prices_pe_obj]
        return quarterly_reports_prices_pe_json

    def group_average(self, list_of_companies_financials):
        """
        returns the average value of various financials of a group of companies, including:
        revenue, cost, earnings; stock price, price/earnings ratio
        """
        dates_vector = [company['Quarterly financials']['date'] 
                    for company in list_of_companies_financials][0]
        revenues_list = [company['Quarterly financials']['revenue'] for company in list_of_companies_financials]
        revenues_sum_list = list(map(sum, zip(*revenues_list)))
        print(revenues_sum_list)
        breakpoint()

    @classmethod
    def group_avg_financials_history(self, companies_fiancials_list, cursor):
        """
        param: companies_fiancials_list -> a list of Company instances

        returns in json a list of the averages of the various company financials. 
        """
        historical_financials = []
        for company in companies_fiancials_list:
            historical_financials.append(company.to_quarterly_financials_json(cursor))

        self.group_avg_financials_history(historical_financials)
        # call sub_industry_average (or a generic group_average) function
        # call a function (to be worked out) that calculates the average of a financial of companies in the same sector
            # from one table: price, pe; from another: revenue, cost, earnings,
        

    
    def search_quarterly_report_by_ticker(self, ticker_params, cursor):
        pass
        ticker = ticker_params.values()[0]
        company = find_by_stock_ticker(ticker)
        # check if company is a Company object?
        # company_id = company.
        return   quarterly_report()

    