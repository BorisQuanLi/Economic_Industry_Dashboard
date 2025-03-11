class SectorOverview:
    """Component for displaying sector overview"""
    def __init__(self, api_client):
        self.api_client = api_client

    def render(self, container):
        try:
            metrics = self.api_client.get_sector_metrics()
            container.metric("Average Revenue", metrics["average_revenue"])
            container.metric("Average Profit", metrics["average_profit"])
            container.metric("Total Market Cap", metrics["total_market_cap"])
        except Exception as e:
            raise Exception(str(e))

class CompanyList:
    """Component for displaying company list"""
    def __init__(self, api_client):
        self.api_client = api_client

    def get_companies(self, sector):
        return self.api_client.get_sector_companies(sector)
