
import sys
sys.path.append('C:/Users/basar/Documents/Bible project/paser-app')
from flexible_hochma_parser import FlexibleHochmaParser
import pandas as pd
import os

def parse_missing_chapters(article_ids):
    parser = FlexibleHochmaParser()
    all_dfs = []
    for article_id in article_ids:
        result = parser.parse_to_excel(article_id)
        if result:
            all_dfs.append(result['dataframe'])

    if all_dfs:
        # Merge all dataframes
        merged_df = pd.concat(all_dfs, ignore_index=True)

        # Append to existing file
        existing_file = 'complete_hochma_parsed_20250709_232110.xlsx'
        output_file = 'complete_hochma_parsed_updated.xlsx'

        if os.path.exists(existing_file):
            existing_df = pd.read_excel(existing_file)
            final_df = pd.concat([existing_df, merged_df], ignore_index=True)
        else:
            final_df = merged_df

        final_df.to_excel(output_file, index=False)
        print(f"Successfully parsed and merged missing chapters into {output_file}")

if __name__ == "__main__":
    missing_ids = [139479, 139483, 139525, 139527, 139529, 139752, 139943, 139953, 140065, 140409, 140767, 140923, 141069, 141347, 141477]
    parse_missing_chapters(missing_ids)
