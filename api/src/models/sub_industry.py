from api.src.db import db
import api.src.models as models

class SubIndustry:
    __table__ = "sub_industries"
    columns = ['id', 'sub_industry_GICS', 'sector_GICS']

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    @classmethod
    def find_by_sub_industry(self, sub_industry_name, cursor):
        sql_str = f"""SELECT * FROM {self.__table__}
                    WHERE sub_industry_GICS = %s"""
        print(self.__table__)
        cursor.execute(sql_str, (sub_industry_name,))
        record = cursor.fetchone()
        return db.build_from_record(SubIndustry, record)

    @classmethod
    def find_by_sector(self, sector_name, cursor):
        sql_str = f"""SELECT * FROM {self} 
                    WHERE sector_GICS = %s;"""
        cursor.execute(sql_str, (sector_name,))
        record = cursor.fetchone()
        return record

    
    