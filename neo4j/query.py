"""
neo4j/query.py
--------------
Cypher query functions against the populated S&P 500 graph.
Demonstrates MATCH/RETURN aggregation and Neo4j GDS algorithm calls.

Usage (from project root, with neo4j container running and graph seeded):

    python -m neo4j.query
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from neo4j import GraphDatabase


def _driver(uri=None, auth=("neo4j", "password")):
    uri = uri or os.getenv("NEO4J_URI", "bolt://neo4j:7687")
    return GraphDatabase.driver(uri, auth=auth)


def get_sector_avg_revenue(sector_name: str, uri=None) -> dict:
    """Cross-sector revenue aggregation — mirrors SubIndustry.find_avg_quarterly_financials_by_sector()."""
    with _driver(uri).session() as session:
        result = session.run(
            """
            MATCH (:Sector {name: $sector})<-[:IN_SECTOR]-(:SubIndustry)
                  <-[:BELONGS_TO]-(c:Company)-[:REPORTED]->(q:QuarterlyReport)
            RETURN avg(q.revenue) AS avg_revenue, count(q) AS report_count
            """,
            sector=sector_name,
        )
        return result.single().data()


def get_top_companies_by_pe(sub_industry_name: str, limit: int = 5, uri=None) -> list[dict]:
    """Intra-sub-industry P/E benchmarking — mirrors Company.find_company_quarterly_price_pe()."""
    with _driver(uri).session() as session:
        result = session.run(
            """
            MATCH (:SubIndustry {name: $sub_industry})<-[:BELONGS_TO]-(c:Company)
                  -[:TRADED_AT]->(p:PricePE)
            RETURN c.ticker AS ticker, c.name AS name, avg(p.price_earnings_ratio) AS avg_pe
            ORDER BY avg_pe DESC LIMIT $limit
            """,
            sub_industry=sub_industry_name,
            limit=limit,
        )
        return result.data()


def run_pagerank(uri=None, top_n: int = 10) -> list[dict]:
    """
    PageRank over the Company-SubIndustry-Sector graph via Neo4j GDS.
    Requires the graph-data-science plugin (NEO4J_PLUGINS in docker-compose.yml).

    Projects an in-memory graph named 'companyGraph' on first call;
    subsequent calls reuse it.
    """
    with _driver(uri).session() as session:
        # Create the in-memory projected graph if it doesn't exist
        existing = session.run(
            "CALL gds.graph.exists('companyGraph') YIELD exists RETURN exists"
        ).single()["exists"]

        if not existing:
            session.run(
                """
                CALL gds.graph.project(
                    'companyGraph',
                    ['Company', 'SubIndustry', 'Sector'],
                    ['BELONGS_TO', 'IN_SECTOR', 'REPORTED', 'TRADED_AT']
                )
                """
            )

        result = session.run(
            """
            CALL gds.pageRank.stream('companyGraph')
            YIELD nodeId, score
            RETURN gds.util.asNode(nodeId).ticker AS ticker,
                   gds.util.asNode(nodeId).name   AS name,
                   score
            ORDER BY score DESC LIMIT $top_n
            """,
            top_n=top_n,
        )
        return result.data()


if __name__ == "__main__":
    import json

    print("\n=== Sector avg revenue: Information Technology ===")
    print(json.dumps(get_sector_avg_revenue("Information Technology"), indent=2))

    print("\n=== Top 5 companies by avg P/E: Semiconductors ===")
    print(json.dumps(get_top_companies_by_pe("Semiconductors & Semiconductor Equipment"), indent=2))

    print("\n=== PageRank top 10 nodes ===")
    print(json.dumps(run_pagerank(), indent=2))
