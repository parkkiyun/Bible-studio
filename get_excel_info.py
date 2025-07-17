import pandas as pd

excel_file_path = 'complete_hochma_parsed_20250626_074211.xlsx'
sheet_name = '호크마 주석 데이터' # Assuming this sheet name is correct

try:
    df = pd.read_excel(excel_file_path, sheet_name=sheet_name)
    print("Excel file loaded successfully.")
    print("\nColumns:")
    print(df.columns.tolist())
    print("\nFirst 5 rows:")
    print(df.head().to_string()) # .to_string() to ensure full output in console
except Exception as e:
    print(f"Error loading Excel file: {e}")
    # Try without sheet name if the above fails
    try:
        df = pd.read_excel(excel_file_path)
        print("\nAttempting to load without specifying sheet_name.")
        print("Excel file loaded successfully (without sheet_name).")
        print("\nColumns:")
        print(df.columns.tolist())
        print("\nFirst 5 rows:")
        print(df.head().to_string())
    except Exception as e_no_sheet:
        print(f"Error loading Excel file even without sheet_name: {e_no_sheet}")
