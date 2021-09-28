DROP TABLE IF EXISTS companies;
DROP TABLE IF EXISTS sub_industries;
DROP TABLE IF EXISTS prices_pe;
DROP TABLE IF EXISTS quarterly_reports;

CREATE TABLE IF NOT EXISTS companies (
  id serial PRIMARY KEY,
  name VARCHAR(64) NOT NULL,
  ticker VARCHAR(16) UNIQUE,
  sub_industry_id SMALLINT,
  year_founded VARCHAR(64),
  number_of_employees INTEGER,
  HQ_state VARCHAR(64)
);

CREATE TABLE IF NOT EXISTS sub_industries(
  id serial PRIMARY KEY,
  sub_industry_GICS VARCHAR(64),
  sector_GICS VARCHAR(64)
);

CREATE TABLE IF NOT EXISTS prices_pe(
	id serial PRIMARY KEY,
  date VARCHAR(16),
  company_id INTEGER,
	closing_price NUMERIC,
	price_earnings_ratio NUMERIC
	);

CREATE TABLE IF NOT EXISTS quarterly_reports (
  id serial PRIMARY KEY,
  date VARCHAR(16),
  company_id INTEGER,
  revenue BIGINT,
  net_income BIGINT,
  earnings_per_share NUMERIC,
  profit_margin NUMERIC
);

