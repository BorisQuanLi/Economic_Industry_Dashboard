from .. import db
from .company import Company
from .quarterly_report import QuarterlyReport
from .sub_industry import SubIndustry
from .price_pe import PricePE
from dataclasses import dataclass

@dataclass
class SubIndustry:
    id: int
    name: str
    sector: str