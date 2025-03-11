from flask import Flask
from flask_cors import CORS
# ...existing imports...

def create_app(database_name=None, testing=False, debug=False):
    app = Flask(__name__)
    CORS(app)
    
    app.config['TESTING'] = testing
    app.config['DEBUG'] = debug
    
    if database_name:
        app.config['DATABASE_NAME'] = database_name
    else:
        app.config['DATABASE_NAME'] = 'investment_analysis'
    
    # ...existing database setup code...
    
    return app