"""Tests for the MCP financial data server."""

from types import SimpleNamespace

import pytest

import server


class _FakeSectorRow:
	def __init__(self, payload):
		self._payload = payload

	def asDict(self):
		return self._payload


class _FakeSparkSession:
	def __init__(self):
		self.stopped = False

	def stop(self):
		self.stopped = True


def test_load_sector_rows_from_spark_uses_builder_output(monkeypatch):
	fake_spark = _FakeSparkSession()
	companies_df = object()

	class FakeBuilder:
		def __init__(self, spark):
			assert spark is fake_spark
			self.run_called = False
			self.summary_called_with = None

		def run(self):
			self.run_called = True
			return companies_df

		def get_sector_summary(self, received_companies_df):
			self.summary_called_with = received_companies_df
			return SimpleNamespace(
				collect=lambda: [
					_FakeSectorRow(
						{
							"sector": "Financials",
							"company_count": 12,
							"avg_employees": 54321.0,
							"aml_risk_flag": "High Capacity / Review Needed",
						}
					)
				]
			)

	monkeypatch.setattr(server, "_create_spark_session", lambda: fake_spark)
	monkeypatch.setattr(server, "SparkCompaniesBuilder", FakeBuilder)

	rows = server._load_sector_rows_from_spark()

	assert rows == [
		{
			"sector": "Financials",
			"company_count": 12,
			"avg_employees": 54321.0,
			"aml_risk_flag": "High Capacity / Review Needed",
		}
	]
	assert fake_spark.stopped is True


def test_get_sector_rows_falls_back_when_dependencies_missing(monkeypatch):
	monkeypatch.setattr(server, "SparkSession", None)
	monkeypatch.setattr(server, "SparkCompaniesBuilder", None)

	assert server._get_sector_rows() == server._FALLBACK_SECTOR_ROWS


def test_get_sector_rows_propagates_etl_failures(monkeypatch):
	fake_spark = _FakeSparkSession()

	class FailingBuilder:
		def __init__(self, spark):
			assert spark is fake_spark

		def run(self):
			raise ValueError("ETL failed")

		def get_sector_summary(self, companies_df):
			raise AssertionError("should not reach sector summary")

	monkeypatch.setattr(server, "_create_spark_session", lambda: fake_spark)
	monkeypatch.setattr(server, "SparkCompaniesBuilder", FailingBuilder)

	with pytest.raises(ValueError, match="ETL failed"):
		server._get_sector_rows()

	assert fake_spark.stopped is True
