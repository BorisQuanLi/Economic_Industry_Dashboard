DROP TABLE IF EXISTS companies;
DROP TABLE IF EXISTS sectors;
DROP TABLE IF EXISTS prices;
DROP TABLE IF EXISTS financials;

CREATE TABLE IF NOT EXISTS companies (
  id serial PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  ticker VARCHAR(255) UNIQUE,
  sub_industry_id VARCHAR(255),
  year_founded VARCHAR(255),
  number_of_employees INTEGER,
  HQ_state VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS sub_industries(
  id serial PRIMARY KEY,
  sub_industry_GICS VARCHAR(255),
  sector_GICS VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS prices_pe(
	id serial PRIMARY KEY,
  company_id INTEGER,
	closing_price FLOAT4,
	price_earnings_ratio FLOAT4
	);

CREATE TABLE IF NOT EXISTS quarterly_reports (
  id serial PRIMARY KEY,
  date DATE,
  company_id INTEGER,
  closing_price FLOAT,
  revenue BIGINT,
  net_income BIGINT,
  earnings_per_share FLOAT4
);

