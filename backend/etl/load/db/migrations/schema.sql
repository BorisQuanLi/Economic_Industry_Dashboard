-- Database Schema for Economic Industry Dashboard

-- Sectors table
CREATE TABLE IF NOT EXISTS sectors (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT
);

-- Sub-industries table
CREATE TABLE IF NOT EXISTS sub_industries (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    sector_id INTEGER REFERENCES sectors(id),
    description TEXT,
    UNIQUE(name, sector_id)
);

-- Companies table
CREATE TABLE IF NOT EXISTS companies (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(10) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    sector_id INTEGER REFERENCES sectors(id),
    sub_industry_id INTEGER REFERENCES sub_industries(id),
    description TEXT,
    website VARCHAR(255),
    headquarters VARCHAR(100),
    founded INTEGER
);

-- Quarterly financial reports
CREATE TABLE IF NOT EXISTS quarterly_reports (
    id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id),
    date DATE NOT NULL,
    revenue NUMERIC,
    cost_of_revenue NUMERIC,
    gross_profit NUMERIC,
    operating_income NUMERIC,
    net_income NUMERIC,
    earnings_per_share NUMERIC,
    shares_outstanding NUMERIC,
    quarter VARCHAR(6),
    UNIQUE(company_id, date)
);

-- Price and P/E ratio history
CREATE TABLE IF NOT EXISTS prices_pe (
    id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id),
    date DATE NOT NULL,
    closing_price NUMERIC NOT NULL,
    price_earnings_ratio NUMERIC,
    earnings_per_share NUMERIC,
    UNIQUE(company_id, date)
);

-- Economic indicators
CREATE TABLE IF NOT EXISTS economic_indicators (
    id SERIAL PRIMARY KEY,
    indicator_type VARCHAR(50) NOT NULL,
    date DATE NOT NULL,
    value NUMERIC,
    description TEXT,
    UNIQUE(indicator_type, date)
);

-- Sector quarterly financials (aggregate view)
CREATE VIEW sector_quarterly_financials AS
SELECT 
    s.name AS sector_name,
    qr.date,
    AVG(qr.revenue) AS avg_revenue,
    AVG(qr.net_income) AS avg_net_income,
    AVG(qr.earnings_per_share) AS avg_eps,
    AVG(qr.net_income / NULLIF(qr.revenue, 0)) AS avg_profit_margin
FROM 
    quarterly_reports qr
JOIN 
    companies c ON qr.company_id = c.id
JOIN 
    sectors s ON c.sector_id = s.id
GROUP BY 
    s.name, qr.date
ORDER BY 
    s.name, qr.date DESC;

-- Sub-sector quarterly financials (aggregate view)
CREATE VIEW sub_sector_quarterly_financials AS
SELECT 
    si.name AS sub_sector_name,
    s.name AS sector_name,
    qr.date,
    AVG(qr.revenue) AS avg_revenue,
    AVG(qr.net_income) AS avg_net_income,
    AVG(qr.earnings_per_share) AS avg_eps,
    AVG(qr.net_income / NULLIF(qr.revenue, 0)) AS avg_profit_margin
FROM 
    quarterly_reports qr
JOIN 
    companies c ON qr.company_id = c.id
JOIN 
    sub_industries si ON c.sub_industry_id = si.id
JOIN 
    sectors s ON c.sector_id = s.id
GROUP BY 
    si.name, s.name, qr.date
ORDER BY 
    si.name, qr.date DESC;
