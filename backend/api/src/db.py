import psycopg2
from flask import current_app, g

def get_db():
    if 'db' not in g:
        g.db = psycopg2.connect(current_app.config['DATABASE'])
    return g.db

def init_db():
    db = get_db()
    # Add initialization code here
    return db

def init_app(app):
    app.teardown_appcontext(lambda e: g.pop('db', None))
