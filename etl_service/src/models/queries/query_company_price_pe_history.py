from etl_service.src.models.quarterly_aggregation_models.aggregation_by_quarter import QuarterlyPricePE
from etl_service.src.models.queries.sql_query_strings import companies_within_sub_sector_str, company_price_pe_history_query_str

class MixinCompanyPricePE:
    """mixin with class Company"""
    @classmethod
    def get_all_company_names_in_sub_sector(self, sub_sector_name, cursor):
        sql_str = companies_within_sub_sector_str()
        cursor.execute(sql_str, (sub_sector_name,))
        company_names = [company_name[1] for company_name in cursor.fetchall()]
        return company_names

    def to_quarterly_price_pe_json(self, company_name, cursor):
        sql_str = company_price_pe_history_query_str(self)
        cursor.execute(sql_str, (company_name,))
        objs_list = [self.create_price_pe_objs(record[1:]) for record in cursor.fetchall()]
        return objs_list

    def create_price_pe_objs(self, record):
        attr_record_dict = dict(zip(QuarterlyPricePE.attributes, 
                                    record))
        obj = QuarterlyPricePE(**attr_record_dict)
        return obj.__dict__