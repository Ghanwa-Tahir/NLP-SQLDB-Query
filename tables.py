import sqlite3

conn = sqlite3.connect("Data.db")  # Make sure the path matches your DB file
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print("Tables in Data.db:")
for table in tables:
    print(table[0])

conn.close()