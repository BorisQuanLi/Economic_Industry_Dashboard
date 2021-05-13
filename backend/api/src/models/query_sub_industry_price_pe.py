from api.src.models.aggregation_by_quarter import QuarterlyPricePE

# from api.src.models.sub_industry import SubIndustry

"""
The "definitive version" in:
http://www.qtrac.eu/pyclassmulti.html
"""

class Mixin:
    def get_all_sector_names(self, cursor):
        sql_str = f"""  SELECT DISTINCT({self.__table__}.sector_gics)
                        FROM {self.__table__}
                        JOIN companies
                        ON companies.sub_industry_id::INT = {self.__table__}.id
                        JOIN quarterly_reports
                        ON quarterly_reports.company_id = companies.id;
                    """
        cursor.execute(sql_str)
        sector_names = cursor.fetchall()
        return sector_names

    def to_sector_quarterly_financials_json(self, sector_name, cursor):
        sector_price_pe_quarterly_records = self.get_sector_price_pe_quarterly_records(self, sector_name, cursor)
        quarterly_price_pe_objs = [self.build_quarterly_price_pe_obj(self, record, cursor)
                                                                        for record in sector_price_pe_quarterly_records]
        return quarterly_price_pe_objs

    def get_sector_price_pe_quarterly_records(self, sector_name, cursor):
        sql_str = self.sector_price_pe_history_query_str(self)
        cursor.execute(sql_str, (sector_name,))
        records = cursor.fetchall()
        return records

    def sector_price_pe_history_query_str(self):
        sql_str = f"""  SELECT  EXTRACT(year from date::DATE) as year,
                                EXTRACT(quarter from date::DATE) as quarter,
                                ROUND(AVG(closing_price)::NUMERIC, 2) as quarterly_average,
                                ROUND(AVG(price_earnings_ratio)::NUMERIC, 2) as quarterly_average         
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

    def build_quarterly_price_pe_obj(self, sector_price_pe_quarterly_record, cursor):
        attrs = ['year', 'quarter', 'closing_price', 'price_earnings_ratio']
        quarterly_obj = QuarterlyPricePE(**dict(zip(
                                                        attrs, sector_price_pe_quarterly_record)))
        return quarterly_obj.__dict__
