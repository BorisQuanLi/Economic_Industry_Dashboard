import pytest
from flask import json
from api.src.db.db import get_db, close_db, drop_records, save
from api.src.models import Company, SubIndustry
from tests.helpers.build_records import build_records

def test_root_url(client):
    response = client.get('/')
    assert b'' in response.data

