import pandas as pd

def analyze_excel(file_path):
    try:
        df = pd.read_excel(file_path)
        print(f"Successfully loaded {file_path}")
        print("--- DataFrame Info ---")
        df.info()
        print("\n--- DataFrame Columns ---")
        print(df.columns)
        print("\n--- Last 5 Rows ---")
        print(df.tail())
        
        # Check for rows with many NaN values, which might indicate misalignment
        nan_rows = df[df.isnull().sum(axis=1) > 5]
        if not nan_rows.empty:
            print("\n--- Rows with many NaN values (potential issues) ---")
            print(nan_rows)

    except Exception as e:
        print(f"Error analyzing Excel file: {e}")

if __name__ == "__main__":
    analyze_excel('complete_hochma_parsed_updated.xlsx')
