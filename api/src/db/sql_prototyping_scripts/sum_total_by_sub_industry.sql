/* prototyping sql queries, to be executed in a psql terminal */

SELECT sum(revenue) AS combined_revenue, 
       sum(cost) AS combined_cost, 
       sum(net_income) AS combined_net_income
FROM sub_industries JOIN companies 
ON sub_industries.id = companies.sub_industry_id
JOIN quarterly_reports
ON quarterly_reports.company_id = companies.id
WHERE sub_industries.id = 31;

/* random prototyping */

/* find a company_id of a company, any company, to be used
to get all the reporting dates 

Then run a for loop to iterate over the dates*/

select date from prices_pe where 
company_id = (select distinct company_id from prices_pe limit 1);
    date    
------------
 2020-06-27
 2020-03-28
 2019-12-28
 2019-09-28
(4 rows)


select distinct company_id from prices_pe limit 1;

select distinct company_id into one_id from prices_pe limit 1
select date from prices_pe where company_id = one_id;

select date from prices_pe where 
company_id = (select distinct company_id from prices_pe limit 1);

one_id := (select distinct company_id from prices_pe limit 1);




select MAX(prices_pe.date) from prices_pe
join companies on prices_pe.company_id = companies.id
join sub_industries on sub_industries.id = companies.sub_industry_id
where sub_industries.sub_industry_gics  = 'Pharmaceuticals'
group by sub_industries.sub_industry_gics;

