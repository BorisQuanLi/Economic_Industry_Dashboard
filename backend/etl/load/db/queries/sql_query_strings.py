"""
SQL query strings for database operations
"""

# Default query strings - These will be replaced with your actual queries
SECTOR_QUARTERLY_FINANCIALS = """
SELECT * FROM sector_quarterly_financials
WHERE sector_name = %s
ORDER BY date DESC
LIMIT %s
"""

SUB_SECTOR_QUARTERLY_FINANCIALS = """
SELECT * FROM sub_sector_quarterly_financials
WHERE sub_sector_name = %s
ORDER BY date DESC
LIMIT %s
"""

SECTOR_PRICE_PE = """
SELECT * FROM sector_price_pe
WHERE sector_name = %s
ORDER BY date DESC
LIMIT %s
"""

SUB_SECTOR_PRICE_PE = """
SELECT * FROM sub_sector_price_pe
WHERE sub_sector_name = %s
ORDER BY date DESC
LIMIT %s
"""

COMPANY_FINANCIALS = """
SELECT * FROM company_financials
WHERE ticker = %s
ORDER BY date DESC
LIMIT %s
"""

COMPANY_PRICE_HISTORY = """
SELECT * FROM company_price_history
WHERE ticker = %s {where_clause}
ORDER BY date DESC
LIMIT %s
"""

ECONOMIC_INDICATORS = """
SELECT * FROM economic_indicators
{where_clause}
ORDER BY date DESC
LIMIT %s
"""

GDP_GROWTH = """
SELECT * FROM gdp_growth
ORDER BY date DESC
LIMIT %s
"""

UNEMPLOYMENT_RATE = """
SELECT * FROM unemployment_rate
ORDER BY date DESC
LIMIT %s
"""

SECTOR_COMPARISON = """
SELECT date, sector_name, {metric} 
FROM sector_metrics
WHERE sector_name IN ({}) {where_clause}
ORDER BY date DESC
"""

METRIC_CORRELATION = """
SELECT 
    CORR(m1.value, m2.value) AS correlation
FROM
    (SELECT date, value FROM metrics WHERE name = %s AND period = %s {entity_clause}) m1
JOIN
    (SELECT date, value FROM metrics WHERE name = %s AND period = %s {entity_clause}) m2
ON m1.date = m2.date
"""

