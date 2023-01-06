import sqlite3 as sq


with sq.connect('server.db', check_same_thread=False) as con:
    cur = con.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS articles (
    ID INTEGER PRIMARY KEY,
    link TEXT
)""")

cur.execute("""CREATE TABLE IF NOT EXISTS quiz (
    ID INTEGER PRIMARY KEY,
    Text TEXT NOT NULL,
    FAn TEXT NOT NULL,
    SAn TEXT NOT NULL,
    TAn TEXT NOT NULL,
    RAn TEXT NOT NULL
)""")
