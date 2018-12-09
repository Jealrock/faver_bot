import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from peewee import SqliteDatabase
import src.models as models
import db_initializer

db = SqliteDatabase(':memory:', autocommit=False)
db.connect()
