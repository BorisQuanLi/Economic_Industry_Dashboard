import pytest
from click.testing import CliRunner
from backend.webservice.manage import cli, init_db
from backend.etl.pipeline import DataPipeline

@pytest.fixture
def runner():
    return CliRunner()

def test_cli_init_db(runner):
    """Test database initialization command"""
    result = runner.invoke(init_db)
    assert result.exit_code == 0
    assert 'Initialized the database' in result.output

def test_cli_group(runner):
    """Test CLI group exists and runs"""
    result = runner.invoke(cli, ['--help'])
    assert result.exit_code == 0
    assert 'Management script for the Economic Industry Dashboard' in result.output
