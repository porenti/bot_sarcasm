import sqlite3 as sql

connection = sql.connect("main.db")

subd = connection.cursor()
subd.execute("""
                CREATE TABLE people
                (id integer NOT NULL,
                step integer NOT NULL DEFAULT '1',
                sex integer default '0',
                education integer default '0',
                AgeMin integer default '18',
                AgeMax integer default '25',
                town text default ' ');
                """)

connection.commit()
connection.close()
