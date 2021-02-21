/* prototyping the sql query script to be included in the Python psycopg methods.*/

/* show all the companies' closing_price and pe_ratio in two columns*/
psql -U postgres investment_analysis -c """SELECT ARRAY_AGG(closing_price) closing_price,
                                                    ARRAY_AGG(price_earnings_ratio) pe_ratio
                                            FROM sub_industries JOIN companies 
                                            ON sub_industries.id = companies.sub_industry_id
                                            JOIN prices_pe
                                            ON prices_pe.company_id = companies.id
                                            WHERE sub_industries.id = 31
                                            GROUP BY sub_industries.id, company_id;"""

/*
        closing_price         |         pe_ratio          
------------------------------+---------------------------
 {32.04,30.9,39.18,36.22}     | {12.56,10.88,13.42,12.4}
 {137.81,123.16,145.75,128.6} | {54.04,43.37,25.48,44.04}
*/

/* two-level groupby */
psql -U postgres investment_analysis -c """
                    WITH price_pe_table AS (
                        SELECT ARRAY_AGG(closing_price) closing_price,
                                ARRAY_AGG(price_earnings_ratio) pe_ratio
                        FROM sub_industries 
                        JOIN companies 
                        ON sub_industries.id = companies.sub_industry_id
                        JOIN prices_pe
                        ON prices_pe.company_id = companies.id
                        WHERE sub_industries.id = 31
                        GROUP BY sub_industries.id, company_id
                                        )
                    SELECT * FROM price_pe_table;
                                        """

/* create a table based on the result of the array_agg function, above.
 https://stackoverflow.com/questions/36434804/change-column-name-from-aggregate-function-default-postgresql

But create a new table has its drawbacks. 
*/

psql -U postgres investment_analysis -c """
                    CREATE TABLE price_pe_table AS (
                        SELECT ARRAY_AGG(closing_price) closing_price,
                                ARRAY_AGG(price_earnings_ratio) pe_ratio
                        FROM sub_industries 
                        JOIN companies 
                        ON sub_industries.id = companies.sub_industry_id
                        JOIN prices_pe
                        ON prices_pe.company_id = companies.id
                        WHERE sub_industries.id = 31
                        GROUP BY sub_industries.id, company_id
                                        )
                                        """

/* check if the new table has been created */
psql -U postgres investment_analysis -c "SELECT * FROM price_pe_table;" 

/* if needs to CREATE TABLE price_pe_table again: */
psql -U postgres investment_analysis -c "DROP TABLE price_pe_table;"

/* calculate the average of each column of the newly created price_pe_table. 
https://www.xspdf.com/resolution/53482792.html
example query:
#SELECT id, (SELECT SUM(s) FROM UNNEST(monthly_usage) s) as total_usage from users;
*/
psql -U postgres investment_analysis -c """
            ROUNDSELECT (SELECT ROUND:: numeric((AVG(price:: numeric), 2, 2)) FROM UNNEST(closing_price) price) AS average_closing_price,
            ROUND(SELECT ROUND((:: numericAVG(pe:: numeric), 2, 2)) FROM UNNEST(pe_ratio) pe) AS average_pe_ratio
                FROM price_pe_table;"""


/*
https://dba.stackexchange.com/questions/77982/postgresql-summing-arrays-by-index
create table t (
A double precision[5],
B double precision[5]);

insert into t values
('{3,2,0,3,1}', '{1,0,3,2,5}');

with c as(
select unnest(a) a, unnest(b) b from t)
select array_agg(a) a, array_agg(b) b, array_agg(a + b) c from c;
*/

psql -U postgres investment_analysis -c """
                    WITH c AS(
                        SELECT UNNEST(closing_price) cp, UNNEST(pe_ratio) pe FROM price_pe_table)
                    SELECT ARRAY_AGG(cp), ARRAY_AGG(pe) FROM c;
                                        """

psql -U postgres investment_analysis -c """
                    WITH c AS(
                        SELECT UNNEST(closing_price) cp, UNNEST(pe_ratio) pe FROM price_pe_table)
                    ROUNDSELECT (AVG(cp:: numeric), AVG(pe) FROM, 2) c;
                                        """



/* */
WITH price_pe_table AS (
                        SELECT ARRAY_AGG(closing_price) closing_price,
                                ARRAY_AGG(price_earnings_ratio) pe_ratio
                        FROM sub_industries 
                        JOIN companies 
                        ON sub_industries.id = companies.sub_industry_id
                        JOIN prices_pe
                        ON prices_pe.company_id = companies.id
                        WHERE sub_industries.id = 31
                        GROUP BY sub_industries.id, company_id
                                        )
                    SELECT * FROM price_pe_table;

/* join the quarterly_report table
join operation is expensive
*/
SELECT MAX(companies.name), 
    ROUND(AVG(prices_pe.closing_price:: numeric), 2) avg_closing_price,
    ROUND(AVG(prices_pe.price_earnings_ratio:: numeric), 2) avg_pe_ratio,
    ROUND(AVG(quarterly_reports.revenue:: numeric), 2) avg_revenue,
    ROUND(AVG(quarterly_reports.cost:: numeric), 2) avg_cost,
    ROUND(AVG(quarterly_reports.net_income:: numeric), 2) avg_net_income
FROM sub_industries 
JOIN companies 
ON sub_industries.id = companies.sub_industry_id
JOIN prices_pe
ON prices_pe.company_id = companies.id
JOIN quarterly_reports
ON quarterly_reports.company_id = companies.id
WHERE sub_industries.sub_industry_gics  = 'Pharmaceuticals' AND prices_pe.date > '2020-01-01'
GROUP BY companies.id;

        max        |        avg         
-------------------+--------------------
 PFIZER INC        |  31.47000026702881
 JOHNSON & JOHNSON | 130.48500061035156
(2 rows)

# delete venv and deal with the git history issue

(base) localhost:project_folder borisli$ ls
Jigsaw_Python_SQL		console.py			project_presentation		seed.py
__init__.py			differences_dec24_jan_11.txt	requirements.txt		tests
api				frontend			run.py				venv


delete venv 
but it's still in git history
