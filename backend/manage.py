import sys
from flask.cli import FlaskGroup
from api.src import create_app
from api.src.adapters.run_adapters import (BuildSP500Companies, 
                                           BuildQuarterlyReportsPricesPE)
import click

app = create_app()
cli = FlaskGroup(create_app=create_app)

# sp500_companies_info_runner = BuildSP500Companies() 
# sp500_companies_wiki_data = sp500_companies_info_runner.run()

quarterly_reports_runner = BuildQuarterlyReportsPricesPE()
# quarterly_reports_runner.run('Energy') # 23 companies
# quarterly_reports_runner.run('Health Care') # 63 companies

"""
figure out why PFE or JNJ's info has not been written in db after the above line,
and implement db.find_or_create methods.
"""

# instead of flask.cli, look into Airflow. 
breakpoint()

"""
Next step: use for-loop iteration over all the sectors/sub_industries to write all the
companies' rows.

Understand how cli = FlaskGroup(create_app=create_app) works.
"""

@cli.command("build_company")
@cli.argument("ticker")
def build_company(ticker):
    pass

# build objects of all the sub_industries within a given economic sector, based on S&P 500 classifcations
@cli.command('build_sub_industries')
@cli.argument('sector_name')
def build_sub_industries(sector_name):
    runner = RequestAndBuildSubIndustries()
    runner.run(sector_name)
    print(sector_name)
breakpoint()

# change to 'build_companies'
@cli.command('build_venues')
@click.argument('ll')
@click.argument('category')
def build_venues(ll, category):
    # "40.7,-74", "query": "tacos"
    runner = RequestAndBuild()
    runner.run(ll, category)
    print(ll, category)


if __name__ == "__main__":
    cli()
