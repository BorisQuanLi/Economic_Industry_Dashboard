from unittest.mock import patch
import os
from etl_service.src.adapters.wiki_page_client import get_sp500_wiki_data

def test_get_sp500_wiki_data_returns_path(tmp_path, monkeypatch):
    """get_sp500_wiki_data() should return an absolute path string."""
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    # Pre-create the file so the function skips the network fetch
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    # Find what filepath the function would use and create it
    from etl_service.src.adapters.wiki_page_client import get_wiki_data_filepath
    monkeypatch.setattr("etl_service.src.adapters.wiki_page_client.WIKI_DATA_FILEPATH",
                        str(data_dir / "sp500_stocks_wiki_info_test.csv"))
    (data_dir / "sp500_stocks_wiki_info_test.csv").write_text("test")

    result = get_sp500_wiki_data()
    assert isinstance(result, str)
    assert os.path.isabs(result)
