from api.src.models.aggregation_by_quarter import QuarterlyReportResult

class Mixin:
    def sector_quarterly_financials_sql_query(self): 
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
 