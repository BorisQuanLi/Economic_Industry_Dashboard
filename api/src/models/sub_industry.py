from api.src.db import db
import api.src.models as models
from functools import reduce
from datetime import datetime
from collections import defaultdict

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
    def find_by_sub_industry_name(self, sub_industry_name, cursor):
        sql_str = f"""SELECT * FROM {self.__table__}
                    WHERE sub_industry_GICS = %s"""
        cursor.execute(sql_str, (sub_industry_name,))
        record = cursor.fetchone()
        return db.build_from_record(SubIndustry, record)

    @classmethod
    def find_by_sector(self, sector_name, cursor):
        sql_str = f"""SELECT * FROM {self.__table__} 
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
        number_of_companies = len(list_of_companies_financials)
        final_dict = {}

        companies_records = defaultdict(list)
        for company in list_of_companies_financials:
            for reports_category in ['Quarterly Closing Price and P/E ratio', 'Quarterly financials']:
                companies_records[reports_category].append(company[reports_category])
        
        for reports_category in ['Quarterly Closing Price and P/E ratio', 'Quarterly financials']:
            if reports_category == 'Quarterly Closing Price and P/E ratio':
                financials_of_interest = ['closing_price', 'price_earnings_ratio']
            else:
                financials_of_interest = ['revenue', 'cost', 'net_income']
            company_financials_list = companies_records[reports_category]
            quarterly_sum_totals = reduced_4_quarter_dicts_list(financials_of_interest, company_financials_list)
            quarterly_averages = map(lambda x: {k: v/number_of_companies for k, v in x.items()}, 
                                                                                        quarterly_sum_totals)
            final_dict["Avg. " + f"{reports_category}"] = dict(zip(reporting_dates_history, quarterly_averages))

        print("*" * 20)
        print("final_dict from new function:")
        print(final_dict)
        return final_dict
        breakpoint()
        
        
        for reports_category in ['Quarterly Closing Price and P/E ratio', 'Quarterly financials']:
            if reports_category == 'Quarterly Closing Price and P/E ratio':
                company_financials_list = [company['Quarterly Closing Price and P/E ratio'] 
                                                        for company in list_of_companies_financials]
                financials_of_interest = ['closing_price', 'price_earnings_ratio']
            else:
                company_financials_list = [company['Quarterly financials'] 
                                                        for company in list_of_companies_financials]
                financials_of_interest = ['revenue', 'cost', 'net_income']
            quarterly_sum_totals = reduced_4_quarter_dicts_list(financials_of_interest, company_financials_list)
        print("-" * 20)
        print("quarterly_sum_totals from old function, without defaultdict(list):")
        print(quarterly_sum_totals)
        breakpoint()

        for reports_category in ['Quarterly Closing Price and P/E ratio', 'Quarterly financials']:
            if reports_category == 'Quarterly Closing Price and P/E ratio':
                company_financials_list = [company['Quarterly Closing Price and P/E ratio'] 
                                                        for company in list_of_companies_financials]
                financials_of_interest = ['closing_price', 'price_earnings_ratio']
            else:
                company_financials_list = [company['Quarterly financials'] 
                                                        for company in list_of_companies_financials]
                financials_of_interest = ['revenue', 'cost', 'net_income']
            quarterly_sum_totals = reduced_4_quarter_dicts_list(financials_of_interest, company_financials_list)
            quarterly_averages = map(lambda x: {k: v/number_of_companies 
                                                        for k, v in x.items()}, quarterly_sum_totals)
            final_dict["Avg. " + f"{reports_category}"] = dict(zip(reporting_dates_history, quarterly_averages))

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
    