import pytest

@pytest.fixture()
def db_cursor():
    flask_app = create_app(database_name='investment_analysis_test', testing=True, debug=True)
    # ...existing code...