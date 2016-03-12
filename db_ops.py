import sqlite3

db_pointer = None
con = None

def db_init():
    global con
    global db_pointer 
    con = sqlite3.connect('data.sqlite')
    pointer = con.cursor()
    db_pointer =  pointer

def db_exec(query_str):
    global db_pointer
    #pointer.execute("select * from feeds")
    db_pointer.execute(query_str)
    return db_pointer.fetchall()

def db_insert(sql, value):
    global db_pointer
    global con
    db_pointer.execute(sql, value)
    con.commit()
    return db_pointer.fetchone()
