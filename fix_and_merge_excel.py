
import pandas as pd
import glob
import os

def get_book_code(book_name):
    book_mapping = {
        '창세기': 1, '출애굽기': 2, '레위기': 3, '민수기': 4, '신명기': 5,
        '여호수아': 6, '사사기': 7, '룻기': 8, '사무엘상': 9, '사무엘하': 10,
        '열왕기상': 11, '열왕기하': 12, '역대상': 13, '역대하': 14, '에스라': 15,
        '느헤미야': 16, '에스더': 17, '욥기': 18, '시편': 19, '잠언': 20,
        '전도서': 21, '아가': 22, '이사야': 23, '예레미야': 24, '예레미야애가': 25,
        '에스겔': 26, '다니엘': 27, '호세아': 28, '요엘': 29, '아모스': 30,
        '오바댜': 31, '요나': 32, '미가': 33, '나훔': 34, '하박국': 35,
        '스바냐': 36, '학개': 37, '스가랴': 38, '말라기': 39,
        '마태복음': 40, '마가복음': 41, '누가복음': 42, '요한복음': 43, '사도행전': 44,
        '로마서': 45, '고린도전서': 46, '고린도후서': 47, '갈라디아서': 48, '에베소서': 49,
        '빌립보서': 50, '골로새서': 51, '데살로니가전서': 52, '데살로니가후서': 53,
        '디모데전서': 54, '디모데후서': 55, '디도서': 56, '빌레몬서': 57,
        '히브리서': 58, '야고보서': 59, '베드로전서': 60, '베드로후서': 61,
        '요한일서': 62, '요한이서': 63, '요한삼서': 64, '유다서': 65, '요한계시록': 66
    }
    return book_mapping.get(book_name, 999)

def fix_and_merge_excel():
    # 1. Standard column definition
    standard_columns = [
        'ID', '주석명', '성경책', '성경책_코드', '장', '절', '주석_내용',
        '버전', '원본_URL', '파싱_날짜', '내용_길이', '패턴_유형'
    ]

    # 2. Load and transform the original large file
    original_file = 'complete_hochma_parsed_20250709_232110.xlsx'
    if not os.path.exists(original_file):
        print(f"Original file not found: {original_file}")
        return

    df_orig = pd.read_excel(original_file)
    # The original file has a different structure. We need to adapt it.
    # Let's check its columns and adapt.
    # Original columns seem to be: ['article_id', 'title', 'book_name', 'chapter', 'verse', 'content', 'content_length', 'url']
    
    transformed_data = []
    for _, row in df_orig.iterrows():
        book_name = row['book_name']
        chapter = int(row['chapter'])
        verse = int(row['verse'])
        commentary_name = row['title'].split(',')[0] if ',' in row['title'] else '호크마 주석'

        transformed_data.append({
            'ID': f"{book_name}_{chapter}_{verse}",
            '주석명': commentary_name,
            '성경책': book_name,
            '성경책_코드': get_book_code(book_name),
            '장': chapter,
            '절': verse,
            '주석_내용': row['content'],
            '버전': f"{commentary_name}-commentary",
            '원본_URL': row['url'],
            '파싱_날짜': '2025-07-09',
            '내용_길이': row['content_length'],
            '패턴_유형': 'unknown_original'
        })
    
    df_transformed_orig = pd.DataFrame(transformed_data, columns=standard_columns)

    # 3. Load all newly parsed chapter files
    new_files = glob.glob('hochma_*.xlsx')
    new_dfs = []
    for f in new_files:
        try:
            # Make sure not to load the big composite files
            if 'complete' in f or 'corrected' in f or 'organized' in f or 'coverage' in f:
                continue
            df = pd.read_excel(f, sheet_name='주석데이터')
            new_dfs.append(df)
        except Exception as e:
            print(f"Could not process file {f}: {e}")

    if not new_dfs:
        print("No new chapter files found to merge.")
        all_data_df = df_transformed_orig
    else:
        # 4. Concatenate all dataframes
        df_new_chapters = pd.concat(new_dfs, ignore_index=True)
        # Ensure all columns match the standard
        df_new_chapters = df_new_chapters.reindex(columns=standard_columns)
        all_data_df = pd.concat([df_transformed_orig, df_new_chapters], ignore_index=True)

    # 5. Final processing and saving
    # Remove duplicates, just in case
    all_data_df.drop_duplicates(subset=['ID'], keep='last', inplace=True)
    # Sort values
    all_data_df.sort_values(by=['성경책_코드', '장', '절'], inplace=True)

    output_filename = 'hochma_db_final_corrected.xlsx'
    all_data_df.to_excel(output_filename, index=False, engine='openpyxl')
    print(f"Successfully created corrected file: {output_filename}")
    print(f"Total rows: {len(all_data_df)}")

if __name__ == "__main__":
    fix_and_merge_excel()
