"""
neo4j/seed.py
-------------
Neo4jLoader class  +  entry-point runner.

Reads company, quarterly-financials, and price/PE data from the etl_service
PostgreSQL pipeline and writes it into the Neo4j graph as a second write
destination.  Run from the project root:

    python -m neo4j.seed

or inside the neo4j container after `docker compose up neo4j`.
"""
import sys
import os
import logging

# Resolve etl_service from the project root regardless of cwd
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from neo4j import GraphDatabase
import etl_service.src.models as models
import etl_service.src.db as db

logger = logging.getLogger(__name__)


class Neo4jLoader:
    def __init__(self, uri="bolt://neo4j:7687", auth=("neo4j", "password")):
        self.driver = GraphDatabase.driver(uri, auth=auth)

    def close(self):
        self.driver.close()

    def load_company(self, company_obj, sub_industry_name, sector_name):
        with self.driver.session() as session:
            session.run(
                """
                MERGE (s:Sector {name: $sector})
                MERGE (si:SubIndustry {name: $sub_industry})
                MERGE (si)-[:IN_SECTOR]->(s)
                MERGE (c:Company {ticker: $ticker})
                SET c.name = $name,
                    c.hq_state = $hq_state,
                    c.year_founded = $year_founded,
                    c.number_of_employees = $number_of_employees
                MERGE (c)-[:BELONGS_TO]->(si)
                """,
                sector=sector_name,
                sub_industry=sub_industry_name,
                ticker=company_obj.ticker,
                name=company_obj.name,
                hq_state=getattr(company_obj, "HQ_state", None),
                year_founded=str(getattr(company_obj, "year_founded", "")),
                number_of_employees=int(getattr(company_obj, "number_of_employees", 0) or 0),
            )

    def load_quarterly_report(self, report_obj, ticker):
        with self.driver.session() as session:
            session.run(
                """
                MATCH (c:Company {ticker: $ticker})
                MERGE (q:QuarterlyReport {date: $date, ticker: $ticker})
                SET q.revenue = $revenue,
                    q.net_income = $net_income,
                    q.eps = $eps,
                    q.profit_margin = $profit_margin
                MERGE (c)-[:REPORTED]->(q)
                """,
                ticker=ticker,
                date=str(report_obj.date),
                revenue=float(report_obj.revenue or 0),
                net_income=float(report_obj.net_income or 0),
                eps=float(report_obj.earnings_per_share or 0),
                profit_margin=float(report_obj.profit_margin or 0),
            )

    def load_price_pe(self, price_pe_obj, ticker):
        with self.driver.session() as session:
            session.run(
                """
                MATCH (c:Company {ticker: $ticker})
                MERGE (p:PricePE {date: $date, ticker: $ticker})
                SET p.closing_price = $closing_price,
                    p.price_earnings_ratio = $pe_ratio
                MERGE (c)-[:TRADED_AT]->(p)
                """,
                ticker=ticker,
                date=str(price_pe_obj.date),
                closing_price=float(price_pe_obj.closing_price or 0),
                pe_ratio=float(price_pe_obj.price_earnings_ratio or 0),
            )


def run(neo4j_uri="bolt://neo4j:7687"):
    conn = db.get_db()
    cursor = conn.cursor()
    loader = Neo4jLoader(uri=neo4j_uri)

    try:
        # Iterate every company already persisted in PostgreSQL
        cursor.execute("SELECT c.*, si.sub_industry_GICS, si.sector_GICS FROM companies c JOIN sub_industries si ON c.sub_industry_id = si.id;")
        rows = cursor.fetchall()
        company_columns = models.Company.columns + ["sub_industry_GICS", "sector_GICS"]

        for row in rows:
            row_dict = dict(zip(company_columns, row))
            company_obj = models.Company(**{k: v for k, v in row_dict.items() if k in models.Company.columns})
            sub_industry_name = row_dict["sub_industry_GICS"]
            sector_name = row_dict["sector_GICS"]

            loader.load_company(company_obj, sub_industry_name, sector_name)
            logger.info(f"Loaded company: {company_obj.ticker}")

            # Quarterly financials
            for report_obj in models.QuarterlyReport.find_by_company_id(company_obj.id, cursor):
                loader.load_quarterly_report(report_obj, company_obj.ticker)

            # Price / PE
            for price_pe_obj in models.PricePE.find_by_company_id(company_obj.id, cursor):
                loader.load_price_pe(price_pe_obj, company_obj.ticker)

    finally:
        loader.close()
        cursor.close()
        conn.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    neo4j_uri = os.getenv("NEO4J_URI", "bolt://neo4j:7687")
    run(neo4j_uri=neo4j_uri)
