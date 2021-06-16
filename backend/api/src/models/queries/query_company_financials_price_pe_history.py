from api.src.models.queries.sql_query_strings import companies_within_sub_industry_str, sub_industry_names_in_sector_query_str

class Mixin:
    """mixin with class Company"""
    def get_all_company_names_in_sub_industry(self, sub_industry_name, cursor):
        sql_str = companies_within_sub_industry_str(self)
        cursor.execute(sql_str, (sub_industry_name,))
        company_names = [company_name[0] for company_name in cursor.fetechall()]
        return company_names

    def get_all_sub_industry_names_in_sector(self, sector_name, cursor):
        sql_str = sub_industry_names_in_sector_query_str(self)
        cursor.execute(sql_str, (sector_name,))
        sub_industry_names = [sub_industry_name[0] for sub_industry_name in cursor.fetchall()]
        return sub_industry_names