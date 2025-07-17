import pandas as pd
import sys
import json

def check_missing_bible_data(excel_file_path, output_file_path):
    # Hardcoded Bible structure (Protestant Canon: Book Name -> Number of Chapters)
    bible_structure = {
        "창세기": 50, "출애굽기": 40, "레위기": 27, "민수기": 36, "신명기": 34,
        "여호수아": 24, "사사기": 21, "룻기": 4, "사무엘상": 31, "사무엘하": 24,
        "열왕기상": 22, "열왕기하": 25, "역대상": 29, "역대하": 36, "에스라": 10,
        "느헤미야": 13, "에스더": 10, "욥기": 42, "시편": 150, "잠언": 31,
        "전도서": 12, "아가": 8, "이사야": 66, "예레미야": 52, "예레미야애가": 5,
        "에스겔": 48, "다니엘": 12, "호세아": 14, "요엘": 3, "아모스": 9,
        "오바댜": 1, "요나": 4, "미가": 7, "나훔": 3, "하박국": 3,
        "스바냐": 3, "학개": 2, "스가랴": 14, "말라기": 4,
        "마태복음": 28, "마가복음": 16, "누가복음": 24, "요한복음": 21, "사도행전": 28,
        "로마서": 16, "고린도전서": 16, "고린도후서": 13, "갈라디아서": 6, "에베소서": 6,
        "빌립보서": 4, "골로새서": 4, "데살로니가전서": 5, "데살로니가후서": 3,
        "디모데전서": 6, "디모데후서": 4, "디도서": 3, "빌레몬서": 1,
        "히브리서": 13, "야고보서": 5, "베드로전서": 5, "베드로후서": 3,
        "요한일서": 5, "요한이서": 1, "요한삼서": 1, "유다서": 1, "요한계시록": 22
    }

    try:
        with open('bible_verse_counts.json', 'r', encoding='utf-8') as f:
            bible_verse_counts = json.load(f)
    except FileNotFoundError:
        print("bible_verse_counts.json 파일을 찾을 수 없습니다. 절 수 검증이 제한됩니다.")
        bible_verse_counts = {}

    original_stdout = sys.stdout
    with open(output_file_path, 'w', encoding='utf-8') as f:
        sys.stdout = f

        try:
            df = pd.read_excel(excel_file_path) # Read without sheet_name as it failed before
            print(f"Successfully loaded Excel file: {excel_file_path}")
        except Exception as e:
            print(f"Error loading Excel file: {e}")
            sys.stdout = original_stdout # Restore original stdout before returning
            return

        # Ensure '절' column is numeric and handle potential NaNs
        df['절'] = pd.to_numeric(df['절'], errors='coerce').fillna(0).astype(int)

        found_verses = df.groupby(['성경책', '장'])['절'].apply(list).to_dict()

        missing_chapters = []
        chapter_verse_ranges = {}
        incomplete_chapters = []

        for book, max_chapter in bible_structure.items():
            for chapter in range(1, max_chapter + 1):
                expected_verse_count = 0
                if book in bible_verse_counts and chapter <= len(bible_verse_counts[book]):
                    expected_verse_count = bible_verse_counts[book][chapter - 1]

                if (book, chapter) not in found_verses:
                    missing_chapters.append(f"{book} {chapter}장 (예상 절 수: {expected_verse_count}개)")
                else:
                    verses = found_verses[(book, chapter)]
                    # Ensure 'verses' is a list of integers
                    verses = [int(v) for v in verses if pd.notna(v)]

                    if verses:
                        min_verse = min(verses)
                        max_verse = max(verses)
                        actual_verse_count = len(verses)
                        chapter_verse_ranges[f"{book} {chapter}장"] = f"절 범위: {min_verse}-{max_verse} (총 {actual_verse_count}개 절)"
                        
                        if expected_verse_count > 0 and actual_verse_count != expected_verse_count:
                            incomplete_chapters.append(f"{book} {chapter}장: 예상 {expected_verse_count}개 절, 실제 {actual_verse_count}개 절")
                    else:
                        chapter_verse_ranges[f"{book} {chapter}장"] = "절 없음 (데이터는 존재)"
                        if expected_verse_count > 0:
                            incomplete_chapters.append(f"{book} {chapter}장: 예상 {expected_verse_count}개 절, 실제 0개 절")

        print("\n--- Missing Chapters ---")
        if missing_chapters:
            for mc in missing_chapters:
                print(mc)
        else:
            print("No missing chapters found based on the hardcoded Bible structure.")

        print("\n--- Incomplete Chapters (Verse Count Mismatch) ---")
        if incomplete_chapters:
            for ic in incomplete_chapters:
                print(ic)
        else:
            print("No incomplete chapters found based on verse count mismatch.")

        print("\n--- Chapter Verse Ranges (for existing chapters) ---")
        for chapter_info, verse_range in chapter_verse_ranges.items():
            print(f"{chapter_info}: {verse_range}")

    sys.stdout = original_stdout # Restore original stdout

if __name__ == "__main__":
    excel_file = 'hochma_db_final_corrected.xlsx'
    output_file = 'bible_analysis_report.txt'
    check_missing_bible_data(excel_file, output_file)