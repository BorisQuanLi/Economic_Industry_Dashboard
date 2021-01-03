import api.src.models as models
import api.src.db as db
import api.src.adapters as adapters
import psycopg2

class Builder:
    def run(self, report_details, conn, cursor):
        venue = VenueBuilder().run(report_details, conn, cursor)
        if venue.exists:
            return {'venue': venue, 'location': venue.location(cursor), 
                    'venue_categories': venue.venue_categories(cursor)}
        else:
            location = LocationBuilder().run(report_details, venue, conn, cursor)
            venue_categories = CategoryBuilder().run(report_details, venue, conn, cursor)
            return {'venue': venue, 'location': location, 'venue_categories': venue_categories}

class SubIndustryBuilder:
    attributes = ['sub_industry_GICS', 'sector_GICS']
    
    def select_attributes(self, sub_industry_details):
        """
        sub_industry_details: a dictionary
        # data file: data/sp500/S&P500-Sub_Industries.csv
        """
        sub_industry = sub_industry_details['sub_industry_GICS']
        sector = sub_industry_details['sector_GICS']
        return dict(zip(self.attributes, [sub_industry, sector]))

    def run(self, sub_industry_details, conn, cursor):
        selected = self.select_attributes(sub_industry_details)
        sub_industry = db.save(models.SubIndustry(**selected),conn, cursor)
        return sub_industry


class CompanyBuilder:
    attributes = ['name', 'ticker', 'sub_industry_id',
              'number_of_employees', 'HQ_state', 'country', 'year_founded']

    def select_attributes(self, company_details):
        sub_industry_name = company_details['sub_industry_name']
        sub_industry_id = models.SubIndustry.find_by_sub_industry(sub_industry_name, db.cursor).id
        company_info_vector = [company_details['name'],
                               company_details['ticker'],
                               sub_industry_id,
                               company_details['number_of_employees'],
                               company_details['HQ_state'],
                               company_details['country'], 
                               company_details['year_founded']]
        return dict(zip(self.attributes, company_info_vector))
 
    def run(self, company_details, conn, cursor):
        selected = self.select_attributes(company_details)
        company_info_row = db.save(models.Company(**selected), conn, cursor)
        return company_info_row


class QuarterlyReportBuilder:
    attributes = ['date', 'company_id', 'revenue', 'cost', 'net_income', 'earnings_per_share']
    def select_attributes(self, report_details):
        """
        param report_details for each company_year_quarter, to be
        obtained through calling the get_company_quarterly_financials.

        First doing the import in the top section of this script:
        import get_company_quarterly_financials
        from /Project_development/project_scoping_prototyping/prototyping/intrinio_api_prototyping.ipynb

        returns a dictionary with the following keys:
        'Total Revenue', 
        'Total Cost of Revenue',
        'Consolidated Net Income / (Loss)'
        'Basic Earnings per Share'
        'date'
        'ticker'

        'company_id' to be inside this method definition.
        """
        ticker = report_details['ticker']
        try:
            models.Company.find_by_stock_ticker(ticker, db.cursor).id 
        except:
            db.cursor.execute('rollback;')
        company_id = models.Company.find_by_stock_ticker(ticker, db.cursor).id 

        quarterly_financials_vector = [report_details['date'],
                                       company_id,
                                       report_details['Total Revenue'],
                                       report_details['Total Cost of Revenue'],
                                       report_details['Consolidated Net Income / (Loss)'],
                                       report_details['Basic Earnings per Share']
                                       ]
        return dict(zip(self.attributes, quarterly_financials_vector))

    def run(self, report_details, conn, cursor):
        selected = self.select_attributes(report_details)
        quarterly_report = db.save(models.QuarterlyReport(**selected), conn, cursor)
        return quarterly_report

class PricePEbuilder:
    attributes = ['date', 'company_id', 'closing_price', 'price_earnings_ratio']
    
    def select_attributes(self, price_pe_dict):
        """
        prices_record may include a company's closing price on the last
        day of each quarter, obtained from Intrinio
        """
        date = price_pe_dict['date'] 
        company_id = price_pe_dict['company_id'] 
        closing_price = price_pe_dict['closing_price']
        pe_ratio = price_pe_dict['price_earnings_ratio'] 

        selected = dict(zip(self.attributes,
                        [date, company_id, closing_price, pe_ratio])) 
        return selected
        
    def price_pe_dict_list(self, quarterly_reports_list, cursor):
        price_pe_dict_list = []
        for quarterly_report_obj in quarterly_reports_list: 
            company_id = quarterly_report_obj.company_id
            ticker = models.Company.find_by_company_id(company_id, cursor).ticker
            date = quarterly_report_obj.date
            closing_price = (adapters.api_calls.historical_stock_price_via_intrinio_api.
                                stock_historical_price_via_intrinio_api(ticker, date))
            pe_json = models.PricePE.to_pe_json_by_date(date, closing_price, cursor)
            pe_ratio = pe_json['price_earnings_ratio']

            price_pe_dict = {}
            price_pe_dict['date'] = date
            price_pe_dict['company_id'] = company_id
            price_pe_dict['closing_price'] = closing_price
            price_pe_dict['price_earnings_ratio'] = pe_ratio
            price_pe_dict_list.append(price_pe_dict)
        return price_pe_dict_list

    def run(self, quarterly_reports_list, conn, cursor):
        price_pe_dict_list = self.price_pe_dict_list(quarterly_reports_list, cursor)
        selected = self.select_attributes(price_pe_dict)
        price_pe = db.save(models.PricePE, selected, conn, cursor)
        return price_pe