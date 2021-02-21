from api.src.adapters.client import CompaniesClient

client = CompaniesClient()
sp500_wiki_data_filepath  = client.get_sp500_companies_info()

with open(sp500_wiki_data_filepath) as csv_file:
    n = 0
    for row in csv_file:
        if n == 0:
            assert row == ',Symbol,Security,SEC filings,GICS Sector,GICS Sub-Industry,Headquarters Location,Date first added,CIK,Founded,# Employees\n'
        elif n == 1:
            assert row == '0,MMM,3M Company,reports,Industrials,Industrial Conglomerates,"St. Paul, Minnesota",1976-08-09,66740,1902,96163\n'
        else: break
        n += 1
