
import csv
import pandas as pd

master_file_path = 'api/data/sp500/processed_data/fin_statement_item_name_variations.csv'

def master_file_available():
    with open(master_file_path) as csv_file:
        reader = [i for i in csv.DictReader(csv_file)]
        if len(reader) > 0:
            return True
        else:
            return False

def extend_names_variations(**kwargs: dict):
    names_df = pd.read_csv(master_file_path)
    empty_names_df = names_df.empty
    if not empty_names_df:
        # delete the master_file_available function definition (ab0ve)
    if master_file_available():
        with open(master_file_path, newline='') as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                kwargs['revenues_name_variations'] = row['revenues_name_variations'] + kwargs['revenues_name_variations']
                kwargs['net_income_name_variations'] = row['net_income_name_variations'] + kwargs['net_income_name_variations']
                kwargs['earnings_per_share_name_variations'] = row['earnings_per_share_name_variations'] + kwargs['earnings_per_share_name_variations']
                kwargs['closing_price_name_variations'] = row['closing_price_name_variations'] + kwargs['closing_price_name_variations']
    return kwargs  

def save_names_variations(**kwargs: dict):
    """
    kwargs: a dictionary, needs to be of equal length.
    
    """
    mapping_dict = dict(zip(['revenue', 'net_income', 'earnings_per_share', 'closing_price'],
                            ['revenues_name_variations', 'net_income_name_variations', 'earnings_per_share_name_variations', 'closing_price_name_variations'],
                            ))

    with open(master_file_path, 'w', newline='') as csv_file:
        fieldnames = list(mapping_dict.values())
        writer = csv.DictWriter(csv_file, fieldnames= fieldnames)
        writer.writeheader()
        tuples = zip([kwargs[mapping_dict[k]] for k 
                                        in ['revenue', 'net_income', 'earnings_per_share', 'closing_price']])
        for tupl in tuples:
            writer.writerow({'revenue': tupl[0],
                            'net_income': tupl[1],
                            'earnings_per_share': tupl[2],
                            'closing_price': tupl[3]})
     

class FinStatementItemName:
    categories = ['revenues_name_variations',
                   'net_income_name_variations',
                   'earnings_per_share_name_variations',
                   'closing_price_name_variations']
    def __init__(self, ticker, **kwargs):
        """
        params: kwargs -> a dictionary whose keys are the categories in 
        the class attributes; each of their corresponding values is a list names variations.
        """
        # to programmatically find out all the fin-statement terms of a company
        # quarter_statements_labels, ticker = quarterly_statements_labels(ticker)
        
        # need to move this to the db, in a new table fin_statement_items_names, and use
        # db.build_records method to load all the attributes to the instance.

        kwargs  = extend_names_variations(**kwargs)

        for key in kwargs.keys():
            if key not in self.categories:
                raise f"{key} not in Class attributes {self.categories}"
        
        for key, value in kwargs.items():
            setattr(self, key, value)

        save_names_variations(**kwargs)    

def set_fin_statement_items_objs(company_ticker, 
                                    revenues_name_variations: list, 
                                    net_income_name_variations: list, 
                                    earning_per_share_name_variations: list,
                                    closing_price_name_variations: list = []):
    fin_statement_item_name_variations = {}
    fin_statement_item_name_variations[
                                'revenues_name_variations'] = revenues_name_variations
    fin_statement_item_name_variations[
                                'net_income_name_variations'] = net_income_name_variations
    fin_statement_item_name_variations[
                                'earnings_per_share_name_variations'] = earning_per_share_name_variations
    fin_statement_item_name_variations[
                                'closing_price_name_variations'] = closing_price_name_variations
    company_obj_pair = {}
    company_obj_pair[company_ticker] = FinStatementItemName(company_ticker, **fin_statement_item_name_variations)
    return company_obj_pair


apple_rev_names = ['Net sales', 'Revenue, Net', 'Revenue']
apple_net_income_names = ['Earnings Per Share, Basic',
                         'Basic (in dollars per share)',
                         'Basic earnings per share (in dollars per share)']
apple_earning_per_share_name_variations = ['Numerator:',
                                 'Net income',
                                 'Comprehensive Income (Loss), Net of Tax, Attributable to Parent']

apple_fin_statement_items_names = set_fin_statement_items_objs('AAPL',
                    apple_rev_names, apple_net_income_names, apple_earning_per_share_name_variations)

print(apple_fin_statement_items_names['AAPL']
            .revenues_name_variations)

apple_fin_statement_terms_names = ['Net sales',
                                    'Revenue, Net',
                                    'Revenue',
                                    'Earnings Per Share, Basic',
                                    'Basic (in dollars per share)',
                                    'Basic earnings per share (in dollars per share)',
                                    'Numerator:',
                                    'Net income',
                                    'Comprehensive Income (Loss), Net of Tax, Attributable to Parent']