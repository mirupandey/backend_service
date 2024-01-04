import pandas as pd
from sqlalchemy import create_engine, text, inspect
from pymongo import MongoClient

def create_connection():
    engine = create_engine("sqlite+pysqlite:///User_Data.db", echo=True, future=True)
    # conn = engine.connect()
    # conn
    with engine.connect() as conn:
        insp = inspect(engine)
        table_exist = insp.has_table('Users')
        if not table_exist:
            conn.execute(text("CREATE TABLE IF NOT EXISTS Users (username varchar(100) not null, name varchar(100) not null, password varchar(100) not null, primary key (username))"))
    
    return engine

def mongo_db_create():
    myclient = MongoClient('mongodb://localhost:27017/') 
    mydb = myclient.product_db

    mycol = mydb.products
    return mycol