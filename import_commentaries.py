
import pandas as pd
import sqlite3
import os

# Define file paths
excel_path = r"C:\Users\basar\Documents\Bible project\paser-app\hochma_db_final_corrected.xlsx"
db_path = r"C:\Users\basar\Documents\Bible project\ai-sermon-assistant\src\data\bible.db"
backup_path = r"C:\Users\basar\Documents\Bible project\ai-sermon-assistant\src\data\bible.db.bak"

# 1. Backup the database
try:
    if os.path.exists(db_path):
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"Successfully backed up {db_path} to {backup_path}")
except Exception as e:
    print(f"Error backing up database: {e}")
    exit()

# 2. Read data from the Excel file, skipping the header
try:
    df = pd.read_excel(excel_path, header=0)
    print("Successfully read the Excel file.")
    print("Excel columns:", df.columns.tolist())
except Exception as e:
    print(f"Error reading Excel file: {e}")
    exit()

# 3. Insert data into the database
try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create the 'commentaries' table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS commentaries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        book TEXT NOT NULL,
        chapter INTEGER NOT NULL,
        verse INTEGER NOT NULL,
        commentary TEXT NOT NULL,
        UNIQUE(book, chapter, verse, commentary)
    )
    """)
    print(''''commentaries' table created or already exists.''')

    # Insert data into the table
    for index, row in df.iterrows():
        try:
            # Combine '주석서' (index 1) and '주석_내용' (index 6) into the 'commentary' column
            combined_commentary = f"{row.iloc[1]}: {row.iloc[6]}"
            cursor.execute("""
            INSERT OR REPLACE INTO commentaries (book, chapter, verse, commentary)
            VALUES (?, ?, ?, ?)
            """, (row.iloc[2], row.iloc[4], row.iloc[5], combined_commentary))
        except Exception as e:
            print(f"Could not insert row {index}: {e}")

    conn.commit()
    conn.close()
    print("Successfully inserted commentaries into the database.")

except Exception as e:
    print(f"Error inserting data into database: {e}")

