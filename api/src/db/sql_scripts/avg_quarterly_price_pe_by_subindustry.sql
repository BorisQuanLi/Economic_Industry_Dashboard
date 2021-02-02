/* prototyping the sql query script to be included in the Python psycopg methods.*/
SELECT sub_industries.sub_industry_gics,
       ROUND(AVG(closing_price)::numeric, 2) average_closing_price, 
       ROUND(AVG(price_earnings_ratio)::numeric, 2) average_price_earnings_ratio 
FROM sub_industries JOIN companies 
ON sub_industries.id = companies.sub_industry_id
JOIN prices_pe
ON prices_pe.company_id = companies.id
WHERE sub_industries.id = 31
GROUP BY sub_industries.id;