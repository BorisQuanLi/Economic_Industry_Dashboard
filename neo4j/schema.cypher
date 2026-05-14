// Uniqueness constraints — also create an index automatically
CREATE CONSTRAINT company_ticker IF NOT EXISTS FOR (c:Company) REQUIRE c.ticker IS UNIQUE;
CREATE CONSTRAINT sub_industry_name IF NOT EXISTS FOR (si:SubIndustry) REQUIRE si.name IS UNIQUE;
CREATE CONSTRAINT sector_name IF NOT EXISTS FOR (s:Sector) REQUIRE s.name IS UNIQUE;

// Indexes for frequent lookup patterns
CREATE INDEX quarterly_report_date IF NOT EXISTS FOR (q:QuarterlyReport) ON (q.date);
CREATE INDEX price_pe_date IF NOT EXISTS FOR (p:PricePE) ON (p.date);
