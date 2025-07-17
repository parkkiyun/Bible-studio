import pandas as pd
import sqlite3

def analyze_test_excel():
    """테스트 엑셀 파일 분석"""
    print("📊 테스트 파싱 결과 분석")
    print("=" * 40)
    
    try:
        # 테스트 엑셀 파일 읽기
        df = pd.read_excel('test_corrected_parsing.xlsx', sheet_name='호크마 주석 데이터')
        
        print(f"📋 기본 정보:")
        print(f"  총 행 수: {len(df):,}")
        print(f"  게시글 수: {df['article_id'].nunique()}")
        print(f"  성경책 수: {df['book_name'].nunique()}")
        
        print(f"\n📚 성경책별 상세:")
        book_stats = df.groupby('book_name').agg({
            'article_id': 'nunique',
            'chapter': ['nunique', 'min', 'max'],
            'verse': 'count',
            'content_length': ['sum', 'mean']
        }).round(2)
        
        for book in book_stats.index:
            if pd.notna(book):
                article_count = book_stats.loc[book, ('article_id', 'nunique')]
                chapter_count = book_stats.loc[book, ('chapter', 'nunique')]
                min_chapter = book_stats.loc[book, ('chapter', 'min')]
                max_chapter = book_stats.loc[book, ('chapter', 'max')]
                verse_count = book_stats.loc[book, ('verse', 'count')]
                total_chars = book_stats.loc[book, ('content_length', 'sum')]
                avg_chars = book_stats.loc[book, ('content_length', 'mean')]
                
                print(f"  📖 {book}:")
                print(f"    게시글: {article_count}개")
                print(f"    장: {chapter_count}개 ({min_chapter}~{max_chapter}장)")
                print(f"    절: {verse_count}개")
                print(f"    총 글자수: {total_chars:,}자")
                print(f"    평균 절 길이: {avg_chars:.0f}자")
        
        # 샘플 데이터 확인
        print(f"\n📄 샘플 데이터:")
        for i in range(min(3, len(df))):
            row = df.iloc[i]
            print(f"  {i+1}. {row['book_name']} {row['chapter']}:{row['verse']}")
            print(f"     제목: {row['title']}")
            print(f"     내용 ({len(row['content'])}자): {row['content'][:100]}...")
            print()
        
        # 제목 패턴 확인
        print(f"\n🔍 제목 패턴 확인:")
        unique_titles = df['title'].unique()
        for title in unique_titles[:5]:
            print(f"  {title}")
        
        # 누락된 데이터 확인
        print(f"\n⚠️  누락 데이터 확인:")
        empty_books = df[df['book_name'].isna() | (df['book_name'] == '')]
        print(f"  성경책명 누락: {len(empty_books)}개")
        
        empty_content = df[df['content'].isna() | (df['content'] == '')]
        print(f"  내용 누락: {len(empty_content)}개")
        
        return df
        
    except Exception as e:
        print(f"❌ 분석 실패: {e}")
        return None

def compare_with_bible_db(df):
    """Bible Database와 비교"""
    print(f"\n📖 Bible Database와 비교:")
    
    try:
        conn = sqlite3.connect('bible_database.db')
        
        # 파싱된 성경책들 확인
        parsed_books = set(df['book_name'].dropna().unique())
        
        # Bible DB에서 성경책 목록 가져오기
        bible_books_query = "SELECT DISTINCT book_name FROM verses ORDER BY book_name"
        bible_books_df = pd.read_sql_query(bible_books_query, conn)
        bible_books = set(bible_books_df['book_name'].tolist())
        
        print(f"  Bible DB 성경책 수: {len(bible_books)}")
        print(f"  파싱된 성경책 수: {len(parsed_books)}")
        
        # 파싱된 성경책들 중 Bible DB에 있는 것들
        valid_books = parsed_books & bible_books
        print(f"  유효한 성경책: {len(valid_books)}")
        
        if valid_books:
            print(f"  유효한 성경책 목록:")
            for book in sorted(valid_books):
                print(f"    - {book}")
        
        # 각 성경책의 장 수 비교
        print(f"\n📋 장 수 비교:")
        for book in valid_books:
            # Bible DB에서 해당 성경책의 최대 장 수
            max_chapter_query = f"SELECT MAX(chapter) as max_chapter FROM verses WHERE book_name = '{book}'"
            max_chapter_df = pd.read_sql_query(max_chapter_query, conn)
            bible_max_chapter = max_chapter_df['max_chapter'].iloc[0]
            
            # 파싱된 데이터에서 해당 성경책의 장 수
            book_data = df[df['book_name'] == book]
            parsed_chapters = sorted(book_data['chapter'].unique())
            
            print(f"  📖 {book}:")
            print(f"    Bible DB: {bible_max_chapter}장")
            print(f"    파싱됨: {len(parsed_chapters)}장 ({min(parsed_chapters)}~{max(parsed_chapters)})")
            
            if len(parsed_chapters) == bible_max_chapter:
                print(f"    ✅ 완전")
            else:
                missing_count = bible_max_chapter - len(parsed_chapters)
                print(f"    ⚠️  누락 {missing_count}장")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Bible DB 비교 실패: {e}")

def main():
    """메인 함수"""
    df = analyze_test_excel()
    
    if df is not None:
        compare_with_bible_db(df)
        
        print(f"\n✅ 테스트 분석 완료!")
        print(f"  파싱 품질: {'✅ 우수' if len(df) > 50 else '⚠️ 개선 필요'}")

if __name__ == "__main__":
    main() 