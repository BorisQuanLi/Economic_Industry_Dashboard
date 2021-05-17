def query_all_sector_records(self):
    sql_str = f"""  SELECT DISTINCT({self.__table__}.sector_gics)
                        FROM {self.__table__}
                        JOIN companies
                        ON companies.sub_industry_id::INT = {self.__table__}.id
                        JOIN quarterly_reports
                        ON quarterly_reports.company_id = companies.id;
                    """
    return sql_str

def sub_industry_names_in_sector_query_str():
    sql_str =  f"""
                SELECT DISTINCT(sub_industries.sub_industry_gics)
                FROM sub_industries
                JOIN companies 
                ON companies.sub_industry_id::INT = sub_industries.id
                WHERE sub_industries.sector_gics = %s;
                """
    return sql_str

def sub_industry_avg_price_pe_history_query_str(self):
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
                            ROUND(AVG(closing_price)::NUMERIC, 2) as avg_closing_price,
                            ROUND(AVG(price_earnings_ratio)::NUMERIC, 2) as avg_quarterly_average         
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
                        GROUP BY sub_industries.sector_gics, year, quarter
                        ORDER BY year, quarter;
                    """
        return sql_str

def select_financial_indicator_json(financial_indicator, full_range_json):
    return    {sector:[{'year': quarterly_dict['year'],
                        'quarter': quarterly_dict['quarter'],
                        f'{financial_indicator}': quarterly_dict[financial_indicator]} for quarterly_dict in quarterly_records] 
                                    for sector, quarterly_records in full_range_json.items()}

