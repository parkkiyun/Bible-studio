import json

def find_missing_article_ids(json_file_path, missing_chapters):
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    article_ids = {}
    for link in data['links']:
        for book, chapter in missing_chapters.items():
            if book in link['title'] and f"{chapter:02d}장" in link['title']:
                if book not in article_ids:
                    article_ids[book] = {}
                article_ids[book][chapter] = link['article_id']
    return article_ids

if __name__ == "__main__":
    missing_chapters_to_find = {
        "창세기": [32, 34],
        "출애굽기": [5, 6, 7],
        "신명기": [15],
        "사무엘상": [26, 31],
        "열왕기하": [8],
        "욥기": [35],
        "시편": [146],
        "이사야": [20],
        "예레미야": [26],
        "스바냐": [1],
        "마가복음": [14]
    }

    all_ids = {}
    for book, chapters in missing_chapters_to_find.items():
        for chapter in chapters:
            #This is a bit of a hack, but it works for the given data
            temp_missing = {book: chapter}
            ids = find_missing_article_ids("hochma_all_links_20250626_071054.json", temp_missing)
            if ids:
                if book not in all_ids:
                    all_ids[book] = {}
                all_ids[book][chapter] = ids[book][chapter]

    # Flatten the dictionary to a list of IDs
    final_ids = []
    for book in all_ids:
        for chapter in all_ids[book]:
            final_ids.append(all_ids[book][chapter])

    print(f"Found article IDs: {final_ids}")

    # Now, let's create a script to parse these IDs.
    parser_script = f"""
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
        print(f"Successfully parsed and merged missing chapters into {{output_file}}")

if __name__ == "__main__":
    missing_ids = {final_ids}
    parse_missing_chapters(missing_ids)
"""

    with open("parse_missing_chapters.py", "w", encoding="utf-8") as f:
        f.write(parser_script)
    print("Created parse_missing_chapters.py")

