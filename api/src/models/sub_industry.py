from api.src.db import db
import api.src.models as models
from functools import reduce
from datetime import datetime

class SubIndustry:
    __table__ = "sub_industries"
    columns = ['id', 'sub_industry_GICS', 'sector_GICS']

    def __init__(self, **kwargs):
        for key in kwargs.keys():
            if key not in self.columns:
                raise f"{key} is not in columns {self.columns}"
        for k, v in kwargs.items():
            setattr(self, k, v)

    @classmethod
    def find_by_sub_industry(self, sub_industry_id, cursor):
        sql_str = f"""SELECT * FROM {self.__table__}
                    WHERE sub_industry_GICS = %s"""
        print(self.__table__)
        cursor.execute(sql_str, (sub_industry_id,))
        record = cursor.fetchone()
        return db.build_from_record(SubIndustry, record)

    @classmethod
    def find_by_sector(self, sector_name, cursor):
        sql_str = f"""SELECT * FROM {self} 
                    WHERE sector_GICS = %s;"""
        cursor.execute(sql_str, (sector_name,))
        record = cursor.fetchone()
        return record

    #@classmethod
    def find_companies_by_sub_industry(self, sub_industry_id, cursor):
        """
        # a list of Company instances
        companies_list = db.build_from_records(models.Company, records)
        # passed to a Company method to calculate average financials, to be shown in Flask app only?
        # Or which ones are eye-cataching for front-end Streamlit presentation, other than company name,
        # ticker, stock price, p/e, number of employees, year founded?  
        return # object whose format can conform to streamlit for front-end presentation
        """

        sql_str = f"""SELECT companies.* FROM companies
                      JOIN sub_industries
                      ON sub_industries.id = companies.sub_industry_id
                      WHERE sub_industries.id = %s;
                    """
        cursor.execute(sql_str, (str(sub_industry_id),))
        records = cursor.fetchall() 
        return db.build_from_records(models.Company, records)

    def group_average(self, list_of_companies_financials):
        def reduced_4_quarter_dicts_list(financials_of_interest:list, list_of_companies_financials):
            reduced_dict_list = reduce(lambda x, y: [{f'{key}': 
                                                                (x[x.index(quarterly_fin_dict)][key] 
                                                               + y[x.index(quarterly_fin_dict)][key])
                                                                    for key in quarterly_fin_dict.keys() if key in financials_of_interest} 
                                                                        for quarterly_fin_dict in x],
                                                                                                list_of_companies_financials) 
            return reduced_dict_list

        reporting_dates_history = [quarter['date'].strftime("%Y-%m-%d") for quarter 
                                                        in list_of_companies_financials[0]['Quarterly financials']]
        final_dict = {}
        for reports_category in ['Quarterly financials', 'Quarterly Closing Price and P/E ratio']:
            if reports_category == 'Quarterly Closing Price and P/E ratio':
                company_financials_list = [company['Quarterly Closing Price and P/E ratio'] 
                                                        for company in list_of_companies_financials]
                financials_of_interest = ['closing_price', 'price_earnings_ratio']
            else:
                company_financials_list = [company['Quarterly financials'] 
                                                        for company in list_of_companies_financials]
                financials_of_interest = ['revenue', 'cost', 'net_income']
            final_dict[reports_category] = dict(zip(reporting_dates_history,
                                                    reduced_4_quarter_dicts_list(financials_of_interest, company_financials_list)))

        return final_dict  

    def average_financials_by_sub_industry(self, cursor):
        sql_str= f"""SELECT companies.* FROM companies
                     JOIN sub_industries
                     ON sub_industries.id = companies.sub_industry_id
                     WHERE sub_industries.id = %s;
                  """
        cursor.execute(sql_str, (self.id,))
        records = cursor.fetchall()
        companies_objs_list = db.build_from_records(models.Company, records)
        list_of_companies_financials = [obj.to_quarterly_financials_json(cursor) 
                                                                for obj in companies_objs_list]
        final_dict = self.group_average(list_of_companies_financials)
        return final_dict
    