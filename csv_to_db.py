import pandas as pd
import sqlite3

# File names
csv_file = 'Data.csv'
sqlite_db = 'Data.db'
table_name = 'users'  # You can change this if needed

# Read the CSV file
df = pd.read_csv(csv_file)

# Optional: Drop index columns like 'Unnamed: 0' if present
if 'Unnamed: 0' in df.columns:
    df = df.drop(columns=['Unnamed: 0'])

# Create SQLite connection and write to DB
conn = sqlite3.connect(sqlite_db)
df.to_sql(table_name, conn, if_exists='replace', index=False)

print(f"CSV data successfully written to {sqlite_db} in table '{table_name}'")

conn.close()
