# reference foursquare-flask-api repo/api/api/src/__init__.py
from flask import Flask
import simplejson as json
from flask import request

import src.models as models
import src.db as db

# def create_app(database='foursquare_development',