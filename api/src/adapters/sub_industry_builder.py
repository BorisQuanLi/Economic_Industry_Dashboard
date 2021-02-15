import api.src.models as models
import api.src.db as db
import api.src.adapters as adapters
import psycopg2

class SubIndustryBuilder:
    attributes = ['sub_industry_GICS', 'sector_GICS']
    def run(self, sector_name, sub_industry_name, conn, cursor):
        sub_industries_objs = []
        sub_industry_dict = dict(zip(self.attributes, [sub_industry_name, sector_name]))
        sub_industry_obj = models.SubIndustry(**sub_industry_dict)
        sub_industry = db.save(sub_industry_obj, conn, cursor)
        return sub_industry
        
 