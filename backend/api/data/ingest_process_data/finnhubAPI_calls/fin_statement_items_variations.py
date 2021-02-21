
import csv

def save_names_variations(revenues_name_variations: list, 
                            net_income_name_variations: list, 
                            earning_per_share_name_variations: list):
    categories_zipped = zip(revenues_name_variations, 
                            net_income_name_variations, 
                            earning_per_share_name_variations)
    headerList = ['closing_price',
                    'revenue',
                    'net_income',
                    'earnings_per_share']
    with open('../../sp500/processed_data/fin_statement_item_name_variations.csv') as csv_file:
        writer = csv.DictWriter(csv_file, delimiter=',',
                                            fieldnames= headerList )
        writer.writeheader()
        for categories in categories_zipped:
            writer.writerow(categories)        

breakpoint()

class FinStatementItemName:

    categories = ['fin_statement_items_variations',
                  'revenues_name_variations',
                   'net_income_name_variations',
                   'earnings_per_share_name_variations']
    def __init__(self, ticker, **kwargs):
        """
        params: kwargs -> a dictionary whose keys are the categories in 
        the class attributes; their corresponding values are each a list.
        """
        # to programmatically find out all the fin-statement terms of a company
        # quarter_statements_labels, ticker = quarterly_statements_labels(ticker)
        
        # need to move this to the db, in a new table fin_statement_items_names, and use
        # db.build_records method to load all the attributes to the instance.

        # save them in a csv file
        self.revenues_name_variations = ['Net sales', 'Revenue, Net', 'Revenue']
        setattr(self, 'revenues_name_variations', self.revenues_name_variations)
        self.net_income_name_variations = ['Earnings Per Share, Basic',
                                            'Basic (in dollars per share)',
                                            'Basic earnings per share (in dollars per share)']
        setattr(self, 'net_income_name_variations', self.net_income_name_variations)
        self.earnings_per_share_names = ['Numerator:',
                                        'Net income',
                                        'Comprehensive Income (Loss), Net of Tax, Attributable to Parent']
        setattr(self, 'earnings_per_share_name_variations', self.earnings_per_share_names)
        self.fin_statement_items_variations = (self.revenues_name_variations
                                                + self.net_income_name_variations 
                                                + self.earnings_per_share_name_variations)
        setattr(self,'fin_statement_items_variations', self.fin_statement_items_variations)

        self.category_identifier = {'fin_statement_items_variations': self.fin_statement_items_variations,
                                    'revenues_name_variations': self.revenues_name_variations,
                                    'net_income_name_variations': self.net_income_name_variations,
                                    'earnings_per_share_name_variations': self.earnings_per_share_name_variations}

        for key in kwargs.keys():
            if key not in self.categories:
                raise f"{key} not in Class attributes {self.categories}"
        for key, value in kwargs.items():
            for name in value:
                if name not in self.category_identifier[key]:
                    self.category_identifier[key].append(name)
            setattr(self, key, self.category_identifier[key])
        # save the names variations to a csv file in a designated folder. 

def set_fin_statement_items_names(company_ticker, 
                                    revenues_name_variations: list, 
                                    net_income_name_variations: list, 
                                    earning_per_share_name_variations: list):
    names_variations_fin_statement_items = (revenues_name_variations
                                            + net_income_name_variations 
                                            + earning_per_share_name_variations)
    fin_statement_items_variations = {}
    fin_statement_items_variations[
                'fin_statement_items_variations'] = names_variations_fin_statement_items
    fin_statement_items_variations[
                'revenues_name_variations'] = revenues_name_variations
    fin_statement_items_variations[
                'net_income_name_variations'] = net_income_name_variations
    fin_statement_items_variations[
                'earnings_per_share_name_variations'] = earning_per_share_name_variations
    
    company_obj_pair = {}
    company_obj_pair[company_ticker] = FinStatementItemName(company_ticker, **fin_statement_items_variations)
    return company_obj_pair

apple_fin_statement_terms_names = ['Net sales',
                                    'Revenue, Net',
                                    'Revenue',
                                    'Earnings Per Share, Basic',
                                    'Basic (in dollars per share)',
                                    'Basic earnings per share (in dollars per share)',
                                    'Numerator:',
                                    'Net income',
                                    'Comprehensive Income (Loss), Net of Tax, Attributable to Parent']
apple_rev_names = ['Net sales', 'Revenue, Net', 'Revenue']
apple_net_income_names = ['Earnings Per Share, Basic',
                         'Basic (in dollars per share)',
                         'Basic earnings per share (in dollars per share)']
apple_earnings_per_share_names = ['Numerator:',
                                 'Net income',
                                 'Comprehensive Income (Loss), Net of Tax, Attributable to Parent']

apple_fin_statement_items_names = set_fin_statement_items_names('AAPL',
                    apple_rev_names, apple_net_income_names, apple_earnings_per_share_names)

print(apple_fin_statement_items_names['AAPL']
            .fin_statement_items_variations)
print(apple_fin_statement_items_names['AAPL']
            .revenues_name_variations)
