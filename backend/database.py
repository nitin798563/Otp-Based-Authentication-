import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DATABASE_HOST"),
        user=os.getenv("DATABASE_USER"),
        password=os.getenv("DATABASE_PASSWORD"),
        database=os.getenv("DATABASE_NAME")
    )
    
    
'''
# create_tables.py
from sqlalchemy import create_engine
from models import Base
import os

DATABASE_URL = "mysql+mysqlconnector://root:password@localhost/authdb"  # adjust

engine = create_engine(DATABASE_URL)
Base.metadata.create_all(bind=engine)  # ✅ tables auto-create
print("Tables created successfully")
'''