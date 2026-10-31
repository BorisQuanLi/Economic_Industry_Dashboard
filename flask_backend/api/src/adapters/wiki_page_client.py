from etl_service.src.adapters.wiki_page_client import get_sp500_wiki_data


def ingest_sp500_stocks_info() -> str:
    return get_sp500_wiki_data()
