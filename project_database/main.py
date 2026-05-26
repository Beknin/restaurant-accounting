import sqlite3
connection = sqlite3.connect('database.db')
cursor = connection.cursor()
with open('restaurant_accounting.sql', 'r', encoding = 'utf-8') as f:
    sql_script = f.read()
cursor.executescript(sql_script)
connection.commit()
connection.close()