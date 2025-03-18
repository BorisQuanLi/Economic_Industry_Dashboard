def query_all_sector_names_in_quarterly_reports_table(self):
    # self: SubIndustry class
    sql_str = f"""  SELECT DISTINCT({self.__table__}.sector_gics)
                    FROM {self.__table__} JOIN companies 
                    ON companies.sub_industry_id = {self.__table__}.id                    
                    JOIN quarterly_reports
                    ON quarterly_reports.company_id = companies.id;
                    """
    return sql_str

def sub_sector_names_in_sector_query_str():
    # returns all the sub_industries of a Sector that a sub_industry belongs to
    sql_str =  f"""
                SELECT DISTINCT(sub_industries.sub_industry_gics)
                FROM sub_industries
                WHERE sub_industries.sector_gics = %s;
                """
    return sql_str

def companies_within_sub_sector_str():
    # self: class Company
    sql_str = f"""
                SELECT companies.* FROM companies
                JOIN sub_industries
                ON sub_industries.id = companies.sub_industry_id
                WHERE sub_industries.sub_industry_gics = %s;
                """
    return sql_str

def sub_sector_avg_price_pe_history_query_str(self):
    sql_str = f"""  SELECT  sub_industry_gics,
                            EXTRACT(year from date::DATE) as year,
                            EXTRACT(quarter from date::DATE) as quarter,
                            ROUND(AVG(closing_price)::NUMERIC, 2) as avg_closing_price,
                            ROUND(AVG(price_earnings_ratio)::NUMERIC, 2) as avg_price_earnings_ratio
                    FROM prices_pe
                    JOIN companies 
                    ON companies.id = prices_pe.company_id
                    JOIN sub_industries
                    ON companies.sub_industry_id::INT = sub_industries.id
                    WHERE sub_industries.sub_industry_gics = %s
                    GROUP BY sub_industries.sub_industry_gics, year, quarter
                    ORDER BY year, quarter;
                """
    return sql_str

def sub_industry_avg_quarterly_financial_query_str(self):
    sql_str = f"""  SELECT  sub_industry_gics,
                            EXTRACT(year from date::DATE) as year,
                            EXTRACT(quarter from date::DATE) as quarter,
                            ROUND(AVG(revenue)::NUMERIC, 2) as avg_revenue,
                            ROUND(AVG(net_income)::NUMERIC, 2) as avg_net_income,
                            ROUND(AVG(earnings_per_share)::NUMERIC, 2) as avg_earnings_per_share,
                            ROUND(AVG(profit_margin)::NUMERIC, 2) as avg_profit_margin              
                    FROM quarterly_reports
                    JOIN companies 
                    ON companies.id = quarterly_reports.company_id
                    JOIN sub_industries
                    ON companies.sub_industry_id::INT = sub_industries.id
                    WHERE sub_industries.sub_industry_gics = %s
                    GROUP BY sub_industries.sub_industry_gics, year, quarter
                    ORDER BY year, quarter;
                """
    return sql_str

def sector_avg_price_pe_history_query_str(self):
    sql_str = f"""  SELECT  EXTRACT(year from date::DATE) as year,
                            EXTRACT(quarter from date::DATE) as quarter,
                            ROUND(AVG(closing_price), 2) as avg_closing_price,
                            ROUND(AVG(price_earnings_ratio), 2) as avg_quarterly_average         
                    FROM prices_pe
                    JOIN companies 
                    ON companies.id = prices_pe.company_id
                    JOIN sub_industries
                    ON companies.sub_industry_id::INT = sub_industries.id
                    WHERE sector_gics = %s
                    GROUP BY sub_industries.sector_gics, year, quarter
                    ORDER BY year, quarter;
                """
    return sql_str

def per_sector_avg_quarterly_financials_query_str(self): 
        sql_str = f"""  SELECT  sector_gics,
                                EXTRACT(year from date::DATE) as year,
                                EXTRACT(quarter from date::DATE) as quarter,
                                ROUND(AVG(revenue)::NUMERIC, 2) as avg_revenue,
                                ROUND(AVG(net_income)::NUMERIC, 2) as avg_net_income,
                                ROUND(AVG(earnings_per_share)::NUMERIC, 2) as avg_earnings_per_share,
                                ROUND(AVG(profit_margin)::NUMERIC, 2) as avg_profit_margin              
                        FROM quarterly_reports
                        JOIN companies 
                        ON companies.id = quarterly_reports.company_id
                        JOIN sub_industries
                        ON companies.sub_industry_id::INT = sub_industries.id
                        WHERE sector_gics = %s
                        GROUP BY sub_industries.sector_gics, year, quarter
                        ORDER BY year, quarter;
                    """
        return sql_str

def company_price_pe_history_query_str(self):
    sql_str = f"""  SELECT  companies.name,
                            EXTRACT(year from date::DATE) as year,
                            EXTRACT(quarter from date::DATE) as quarter,
                            closing_price,
                            price_earnings_ratio         
                    FROM prices_pe
                    JOIN companies 
                    ON companies.id = prices_pe.company_id
                    WHERE companies.name = %s;
                """
    return sql_str

def company_quarterly_financials_query_str(self): 
        sql_str = f"""  SELECT  companies.name,
                                EXTRACT(year from date::DATE) as year,
                                EXTRACT(quarter from date::DATE) as quarter,
                                revenue,
                                net_income,
                                earnings_per_share,
                                profit_margin            
                        FROM quarterly_reports
                        JOIN companies 
                        ON companies.id = quarterly_reports.company_id
                        WHERE companies.name = %s;
                    """
        return sql_str

def extract_single_financial_indicator(financial_indicator, full_range_fiancial_indicators_json):
    """
    returns in JSON format each sector's quarterly values of the financial_indicator passed in. 
    """
    return    {sector:[{'year': quarterly_dict['year'],
                        'quarter': quarterly_dict['quarter'],
                        f'{financial_indicator}': quarterly_dict[financial_indicator]} 
                                                            for quarterly_dict in quarterly_records] 
                                                                        for sector, quarterly_records in full_range_fiancial_indicators_json.items()}

