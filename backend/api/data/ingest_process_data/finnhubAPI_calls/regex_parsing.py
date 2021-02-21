import re
import pandas as pd
from api.data.ingest_process_data.finnhubAPI_calls.labels import quarterly_statements_labels, company_historical_financials, single_quarter_ic_labels_values
from api.data.ingest_process_data.finnhubAPI_calls.fin_statement_items_variations import FinStatementItemName, set_fin_statement_items_names

def company_labels_regex_extraction(ticker, labels, **regex_pattern):
    """
    params: labels:list, regex_pattern: a dictionary whose key/value pairs are based on the
    FinStatementItemName and/or its instance.

    https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.Series.str.extract.html

    from fin_statement_items_variations import FinStatementItemName, set_fin_statement_items_names
    # from db or models import FinStatementItemName?
    """
    labels_series = pd.Series(labels)
    fin_statement_items_category = list(regex_pattern.keys())[0]
    existing_labels = list(regex_pattern.values())[0] # a list
    regex_pattern = existing_labels # work out the pattern, assign it to a different varialbe from regex_pattern
    extracted_labels_df = labels_series.str.extract(rf"{regex_pattern}") 
    regex_labels_series = pd.Series(extracted_labels_df[0].notna())
    winnowed_labels = labels_series[regex_labels_series]
    return winnowed_labels, fin_statement_items_category, ticker


apple_quarterly_statements = quarterly_statements_labels('AAPL')
labels = apple_quarterly_statements['2020-03-28 AAPL']['labels']
winnowed_labels, fin_statement_items_category, ticker = company_labels_regex_extraction('AAPL', labels, **{'revenue': '(Revenue)'})
if not winnowed_labels.any():
    print(f"RegEx pattern '(Revenue)' not found in '{ticker}' labels")
print(winnowed_labels)

"""
This RegEx pattern worked, to a certain extent:
But how to work out a RegEx pattern based on the existing 

Need to work out in this script:

from fin_statement_items_variations import FinStatementItemName, set_fin_statement_items_names
# from db or models import FinStatementItemName?
"""
winnowed_labels, fin_statement_items_category, ticker = company_labels_regex_extraction('AAPL', labels, **{'revenue': '(sales)'})
print('-' * 20)
print(ticker, '\n', f"Found these matching labels in the financial statement's '{fin_statement_items_category}' category:", '\n', winnowed_labels)
breakpoint()


fin_statements = apple_quarterly_statements['2020-03-28 AAPL']['quarter_fin_statements']
a_quarter_ic_labels_values = single_quarter_ic_labels_values(fin_statements)
company_quarter = a_quarter_ic_labels_values.keys()[0]
labels_values_dict = a_quarter_ic_labels_values['AAPL Q2 2020-03-28']
keys_list = labels_values_dict.keys()

print(keys_list)
breakpoint()

"""
Next:
iterate over the keys_list to see if any label string is in the 4 list of
 "apple fin statement item names".

Google search "regex pattern two possibilities or"
https://www.google.com/search?client=safari&rls=en&q=regex+pattern+two+possibilities+or&ie=UTF-8&oe=UTF-8

Either|Or part of regex for matching two possibilities
https://stackoverflow.com/questions/46791416/eitheror-part-of-regex-for-matching-two-possibilities
"""
pass

