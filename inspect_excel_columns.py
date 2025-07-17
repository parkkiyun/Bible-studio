import pandas as pd

# Define file paths
excel_path = r"C:\Users\basar\Documents\Bible project\paser-app\hochma_db_final_corrected.xlsx"

# 2. Read data from the Excel file
try:
    df = pd.read_excel(excel_path, header=0)
    print("Successfully read the Excel file.")
    print(df.columns)
except Exception as e:
    print(f"Error reading Excel file: {e}")
    exit()