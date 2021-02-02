/* prototyping sql queries, to be executed in a psql terminal */

SELECT sum(revenue) AS combined_revenue, 
       sum(cost) AS combined_cost, 
       sum(net_income) AS combined_net_income
FROM sub_industries JOIN companies 
ON sub_industries.id = companies.sub_industry_id
JOIN quarterly_reports
ON quarterly_reports.company_id = companies.id
WHERE sub_industries.id = 31;

