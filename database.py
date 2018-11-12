import os
from peewee import PostgresqlDatabase

db = PostgresqlDatabase(os.getenv('DATABASE_NAME'),
                        user=os.getenv('DATABASE_USER'),
                        password=os.getenv('DATABASE_PASS'),
                        host=os.getenv('DATABASE_HOST'))
