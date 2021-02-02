/* prototyping the sql query script to be included in the Python psycopg methods.*/
SELECT sub_industries.sub_industry_gics,
       ROUND(AVG(revenue)) AS average_revenue, 
       ROUND(AVG(cost)) AS average_cost, 
       ROUND(AVG(net_income)) AS average_net_income
FROM sub_industries JOIN companies 
ON sub_industries.id = companies.sub_industry_id
JOIN quarterly_reports
ON quarterly_reports.company_id = companies.id
WHERE sub_industries.id = 31
GROUP BY sub_industries.id;

/*
Next step, implement the SQL query through psycopg, incl.

"WHERE sub_industries.id = %d" in the sql_string

and

cursor.execute(sql_string, (31,))

Afterwards, the Python script that calculates aggregation and returns the json

*/