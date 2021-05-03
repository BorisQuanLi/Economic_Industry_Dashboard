from api.src.models.sub_industry import SubIndustry

# check if this method should be, and can be, written as a separate module, instead of in sub_industry.py
@classmethod
def find_avg_quarterly_financials_by_sub_industry(self, sector_name:str, financial_item:str, cursor):
    """
    Within each chosen sector, calculate each sub_industry's average value of a chosen
    financial-statement item (revenue, net_profit, etc.) over the most recent 
    quarters (5 in total based on the API calls to this project's data source.

    Returns a list of dictionaries with the key being a list of attributes, incl. [sector_name,
    financial_item name, year, quarter], and their corresponding values stored in a list as 
    the dictionary value.
    """
    self.sector_name = sector_name
    self.financial_item = financial_item
    records = self.get_records(sector_name, financial_item, cursor) # don't use self as argument; Python pass through it automatically
    avg_financial_by_sub_industries_dict = self.store_records(records) # not need for self.store_records, then makes store_records a Class method
    avg_financial_dict_with_uniform_length = self.get_uniform_length_dicts(avg_financial_by_sub_industries_dict) 
    historical_financials_json_dict = self.to_historical_financials_json(sector_name, financial_item,
                                                                                avg_financial_dict_with_uniform_length)
    return historical_financials_json_dict

@classmethod
def get_records(self, sector_name, financial_item, cursor): 
    sql_str = self.sql_query_str(self, financial_item)
    cursor.execute(sql_str, (sector_name,))
    records = cursor.fetchall()
    return records

def sql_query_str(self, financial_item):
    sql_str = f"""select {self.__table__}.id, {self.__table__}.sub_industry_gics,
                        ROUND(AVG({financial_item})::NUMERIC, 2) as Average,
                        EXTRACT(year from quarterly_reports.date::DATE) as year,
                        EXTRACT(quarter from quarterly_reports.date::DATE) as quarter
                    FROM quarterly_reports
                    JOIN companies ON quarterly_reports.company_id::INTEGER = companies.id
                    JOIN {self.__table__} ON {self.__table__}.id = companies.sub_industry_id::INTEGER
                    WHERE {self.__table__}.sector_gics = %s
                    GROUP BY year, quarter, {self.__table__}.id, {self.__table__}.sub_industry_gics;
                """
    return sql_str

@classmethod
def store_records(self, records):    
    avg_financial_by_sub_industries_dict = {} 
    for record in records:
        sub_industry_id, sub_industry_name, financial_item_avg, year_quarter = self.unpack_record(record)
        if sub_industry_name not in avg_financial_by_sub_industries_dict:
            avg_financial_by_sub_industries_dict[sub_industry_name] = {}
        avg_financial_by_sub_industries_dict[sub_industry_name][
                                                            year_quarter] = (sub_industry_id, int(financial_item_avg))
    return avg_financial_by_sub_industries_dict

@classmethod
def unpack_record(self, record): # confusing
    sub_industry_id, sub_industry_name, financial_item_avg = record[0], record[1], record[2]
    year, quarter = int(record[3]), int(record[4])
    year_quarter = int(f"{year}0{quarter}") # use integer instead of string?
    return sub_industry_id, sub_industry_name, financial_item_avg, year_quarter

@classmethod    
def get_uniform_length_dicts(self, avg_financial_by_sub_industries_dict):
    uniformed_dicts = {}
    for k, v in avg_financial_by_sub_industries_dict.items():
        if len(v) > 5:
            irregular_length_dict = v
            uniform_length_keys = list(irregular_length_dict.keys())[-5:]
            uniform_length_dict = {k:v for k, v in irregular_length_dict.items()
                                                            if k in uniform_length_keys}
            v = uniform_length_dict
        uniformed_dicts[k] = v
    return uniformed_dicts

def get_uniform_length_dict(irregular_length_dict):
    uniform_length_keys = list(irregular_length_dict.keys())[-5:]
    uniform_length_dict = {k:v for k, v in irregular_length_dict.items()
                                                    if k in uniform_length_keys}
    return uniform_length_dict

@classmethod
def to_historical_financials_json(self, sector_name, financial_item, avg_financial_by_sub_industries_dict):        
    historical_financials_json_dict = {}
    for sub_industry, avg_financials_dict in avg_financial_by_sub_industries_dict.items():
        sub_industry_id, financial_item_avg_recent_quarters = self.unpack_avg_financials_dict(avg_financials_dict)
        historical_financials_json = self.get_historical_financials_json(sub_industry_id, sub_industry, financial_item_avg_recent_quarters) 
        historical_financials_json_dict[sub_industry] = historical_financials_json
    return historical_financials_json_dict

def unpack_avg_financials_dict(avg_financials_dict): # one example of no 'self' argument, and it worked.  Neither a class or instance method?
    sub_industry_id = list(avg_financials_dict.values())[0][0]
    financial_item_avg_recent_quarters = {k:avg_financials_dict[k][1] 
                                                    for k in sorted(avg_financials_dict.keys())} 
    return sub_industry_id, financial_item_avg_recent_quarters

@classmethod
def get_historical_financials_json(self, sub_industry_id, sub_industry, financial_item_avg_recent_quarters):
    sub_industry_dict = dict(zip(self.columns,[sub_industry_id, sub_industry, self.sector_name]))
    sub_industry_obj = models.SubIndustry(**sub_industry_dict)
    historical_financials_json = sub_industry_obj.__dict__
    financial_item_key = f'Avg_quarterly_{self.financial_item}'
    historical_financials_json[financial_item_key] = financial_item_avg_recent_quarters
    return historical_financials_json, financial_item_key