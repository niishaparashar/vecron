import sqlite3
from pathlib import Path

PROJECT_ROOT= Path(__file__).resolve().parent.parent

DB_PATH= PROJECT_ROOT/ "vecron.db"

def get_connection():
    '''using this fuction to connect to the database'''
    conn= sqlite3.connect(DB_PATH)
    conn.row_factory= sqlite3.Row  #enables dictionary-like access to rows
    return conn
def execute_query(query:str, params:tuple=()):
    #execute a write query like INSERT, UPDATE DELETE
    conn= get_connection()
    cursor= conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    conn.close()

def fetch_all(query:str, params:tuple =()):
    #this is to run a SELECT query and RETURN all the rows
    conn= get_connection()
    cursor= conn.cursor()
    cursor.execute(query, params)
    rows= cursor.fetchall()
    conn.close()
    return rows
def fetch_one(query:str, params:tuple=()):
    #this is to run a SELECT query and return only a single row
    conn= get_connection
    cursor= conn.cursor()
    cursor.execute(query, params)
    row= cursor.fetchone()
    conn.close()
    return row


