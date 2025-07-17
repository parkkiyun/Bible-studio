import pandas as pd
import sqlite3
import json
from datetime import datetime

def analyze_current_excel():
    """현재 파싱된 엑셀 파일 분석"""
    print("📊 현재 파싱된 엑셀 파일 분석...")
    
    try:
        # 엑셀 파일 읽기
        df = pd.read_excel('hochma_complete_commentaries_20250626_060910.xlsx', sheet_name='호크마 주석 데이터')
        
        print(f"  총 행 수: {len(df):,}")
        print(f"  총 게시글 수: {df['article_id'].nunique()}")
        
        # 성경책별 통계
        book_stats = df.groupby('book_name').agg({
            'article_id': 'nunique',
            'chapter': ['min', 'max', 'nunique'],
            'verse': 'count'
        }).round(2)
        
        print(f"\n📚 파싱된 성경책 목록 ({len(book_stats)}개):")
        for book in book_stats.index:
            if pd.isna(book) or book == '' or book == 0:
                continue
            article_count = book_stats.loc[book, ('article_id', 'nunique')]
            min_chapter = book_stats.loc[book, ('chapter', 'min')]
            max_chapter = book_stats.loc[book, ('chapter', 'max')]
            chapter_count = book_stats.loc[book, ('chapter', 'nunique')]
            verse_count = book_stats.loc[book, ('verse', 'count')]
            
            print(f"  {book}: {chapter_count}장 ({min_chapter}~{max_chapter}장), {verse_count}절, {article_count}게시글")
        
        # 빈 성경책명 확인
        empty_books = df[df['book_name'].isna() | (df['book_name'] == '') | (df['book_name'] == 0)]
        if len(empty_books) > 0:
            print(f"\n⚠️  성경책명이 비어있는 항목: {len(empty_books)}개")
            print("  샘플 제목들:")
            for title in empty_books['title'].head(10):
                print(f"    - {title}")
        
        return book_stats
        
    except Exception as e:
        print(f"❌ 엑셀 파일 분석 실패: {e}")
        return None

def analyze_bible_database():
    """bible_database.db에서 성경 구조 분석"""
    print("\n📖 Bible Database 구조 분석...")
    
    try:
        conn = sqlite3.connect('bible_database.db')
        
        # 성경책별 장 수 조회
        query = """
        SELECT book_name, MAX(chapter) as max_chapter, COUNT(DISTINCT chapter) as chapter_count
        FROM verses 
        GROUP BY book_name 
        ORDER BY 
            CASE book_name
                WHEN '창세기' THEN 1 WHEN '출애굽기' THEN 2 WHEN '레위기' THEN 3 WHEN '민수기' THEN 4 WHEN '신명기' THEN 5
                WHEN '여호수아' THEN 6 WHEN '사사기' THEN 7 WHEN '룻기' THEN 8 WHEN '사무엘상' THEN 9 WHEN '사무엘하' THEN 10
                WHEN '열왕기상' THEN 11 WHEN '열왕기하' THEN 12 WHEN '역대상' THEN 13 WHEN '역대하' THEN 14 WHEN '에스라' THEN 15
                WHEN '느헤미야' THEN 16 WHEN '에스더' THEN 17 WHEN '욥기' THEN 18 WHEN '시편' THEN 19 WHEN '잠언' THEN 20
                WHEN '전도서' THEN 21 WHEN '아가' THEN 22 WHEN '이사야' THEN 23 WHEN '예레미야' THEN 24 WHEN '예레미야애가' THEN 25
                WHEN '에스겔' THEN 26 WHEN '다니엘' THEN 27 WHEN '호세아' THEN 28 WHEN '요엘' THEN 29 WHEN '아모스' THEN 30
                WHEN '오바댜' THEN 31 WHEN '요나' THEN 32 WHEN '미가' THEN 33 WHEN '나훔' THEN 34 WHEN '하박국' THEN 35
                WHEN '스바냐' THEN 36 WHEN '학개' THEN 37 WHEN '스가랴' THEN 38 WHEN '말라기' THEN 39 WHEN '마태복음' THEN 40
                WHEN '마가복음' THEN 41 WHEN '누가복음' THEN 42 WHEN '요한복음' THEN 43 WHEN '사도행전' THEN 44 WHEN '로마서' THEN 45
                WHEN '고린도전서' THEN 46 WHEN '고린도후서' THEN 47 WHEN '갈라디아서' THEN 48 WHEN '에베소서' THEN 49 WHEN '빌립보서' THEN 50
                WHEN '골로새서' THEN 51 WHEN '데살로니가전서' THEN 52 WHEN '데살로니가후서' THEN 53 WHEN '디모데전서' THEN 54 WHEN '디모데후서' THEN 55
                WHEN '디도서' THEN 56 WHEN '빌레몬서' THEN 57 WHEN '히브리서' THEN 58 WHEN '야고보서' THEN 59 WHEN '베드로전서' THEN 60
                WHEN '베드로후서' THEN 61 WHEN '요한일서' THEN 62 WHEN '요한이서' THEN 63 WHEN '요한삼서' THEN 64 WHEN '유다서' THEN 65
                WHEN '요한계시록' THEN 66 ELSE 999
            END
        """
        
        bible_structure = pd.read_sql_query(query, conn)
        conn.close()
        
        print(f"  총 성경책 수: {len(bible_structure)}")
        print(f"  총 장 수: {bible_structure['max_chapter'].sum()}")
        
        print(f"\n📋 성경책별 장 수:")
        for _, row in bible_structure.iterrows():
            print(f"  {row['book_name']}: {row['max_chapter']}장")
        
        return bible_structure
        
    except Exception as e:
        print(f"❌ Bible Database 분석 실패: {e}")
        return None

def compare_and_find_missing(current_books, bible_structure):
    """파싱된 데이터와 성경 구조 비교하여 누락 부분 찾기"""
    print("\n🔍 누락된 성경책과 장 분석...")
    
    if current_books is None or bible_structure is None:
        print("❌ 비교할 데이터가 없습니다.")
        return
    
    # 누락된 성경책들
    parsed_books = set()
    for book in current_books.index:
        if pd.notna(book) and book != '' and book != 0:
            parsed_books.add(book)
    
    all_books = set(bible_structure['book_name'].tolist())
    missing_books = all_books - parsed_books
    
    print(f"📚 파싱된 성경책: {len(parsed_books)}개")
    print(f"📖 전체 성경책: {len(all_books)}개")
    print(f"❌ 누락된 성경책: {len(missing_books)}개")
    
    if missing_books:
        print("  누락된 성경책들:")
        for book in sorted(missing_books):
            bible_chapters = bible_structure[bible_structure['book_name'] == book]['max_chapter'].iloc[0]
            print(f"    - {book}: {bible_chapters}장")
    
    # 파싱된 성경책들의 누락된 장들
    print(f"\n📄 파싱된 성경책들의 장 누락 현황:")
    missing_chapters = {}
    
    for book in parsed_books:
        if book in bible_structure['book_name'].values:
            bible_chapters = bible_structure[bible_structure['book_name'] == book]['max_chapter'].iloc[0]
            
            # 현재 파싱된 장들
            parsed_chapters = set()
            book_data = current_books.loc[book]
            min_ch = int(book_data[('chapter', 'min')])
            max_ch = int(book_data[('chapter', 'max')])
            count_ch = int(book_data[('chapter', 'nunique')])
            
            # 연속적이지 않을 수 있으므로 실제 데이터 확인 필요
            # 이건 대략적인 추정
            if count_ch == bible_chapters and min_ch == 1 and max_ch == bible_chapters:
                print(f"  ✅ {book}: 완전 ({bible_chapters}장)")
            else:
                missing_count = bible_chapters - count_ch
                print(f"  ⚠️  {book}: {count_ch}/{bible_chapters}장 (누락 {missing_count}장)")
                missing_chapters[book] = missing_count
    
    # 결과 요약
    result = {
        'total_books': len(all_books),
        'parsed_books': len(parsed_books),
        'missing_books': list(missing_books),
        'incomplete_books': missing_chapters,
        'bible_structure': bible_structure.to_dict('records')
    }
    
    # JSON으로 저장
    with open('missing_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 분석 결과 저장: missing_analysis.json")
    
    return result

def main():
    """메인 함수"""
    print("🔍 호크마 주석 파싱 완성도 분석")
    print("=" * 50)
    
    # 1. 현재 파싱된 엑셀 파일 분석
    current_books = analyze_current_excel()
    
    # 2. Bible Database 구조 분석
    bible_structure = analyze_bible_database()
    
    # 3. 비교 분석
    result = compare_and_find_missing(current_books, bible_structure)
    
    if result:
        print(f"\n📊 최종 요약:")
        print(f"  - 전체 성경책: {result['total_books']}개")
        print(f"  - 파싱된 성경책: {result['parsed_books']}개")
        print(f"  - 누락된 성경책: {len(result['missing_books'])}개")
        print(f"  - 불완전한 성경책: {len(result['incomplete_books'])}개")

if __name__ == "__main__":
    main() 