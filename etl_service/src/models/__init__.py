# etl_service.src.models package
# Import models lazily to avoid circular imports

def __getattr__(name):
    if name == "Company":
        from etl_service.src.models.company import Company
        return Company
    elif name == "SubIndustry":
        from etl_service.src.models.sub_industry import SubIndustry
        return SubIndustry
    elif name == "QuarterlyReport":
        from etl_service.src.models.quarterly_report import QuarterlyReport
        return QuarterlyReport
    elif name == "PricePE":
        from etl_service.src.models.price_pe import PricePE
        return PricePE
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
