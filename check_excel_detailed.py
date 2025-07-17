import pandas as pd
import re
from collections import Counter

def analyze_excel_structure():
    """엑셀 파일 구조 상세 분석"""
    print("📊 엑셀 파일 구조 상세 분석...")
    
    try:
        # 엑셀 파일 읽기
        df = pd.read_excel('complete_hochma_parsed_20250626_074211.xlsx', sheet_name='호크마 주석 데이터')
        
        print(f"  총 행 수: {len(df):,}")
        print(f"  컬럼: {list(df.columns)}")
        
        # 샘플 데이터 확인
        print(f"
📋 Sample Data (first 5 rows):")
        for i in range(min(5, len(df))):
            row = df.iloc[i]
            print(f"  행 {i+1}:")
            print(f"    article_id: {row['article_id']}")
            print(f"    title: {row['title'][:100]}...")
            print(f"    book_name: {row['book_name']}")
            print(f"    chapter: {row['chapter']}")
            print(f"    verse: {row['verse']}")
            print(f"    content 길이: {len(str(row['content'])) if pd.notna(row['content']) else 0}")
            print()
        
        # 고유한 title들 확인
        unique_titles = df['title'].dropna().unique()
        print(f"📚 고유한 제목 수: {len(unique_titles)}")
        
        print(f"\n📖 제목 샘플들:")
        for i, title in enumerate(unique_titles[:10]):
            print(f"  {i+1}. {title}")
        
        # article_id별 제목 분석
        article_titles = df.groupby('article_id')['title'].first()
        print(f"\n🔍 게시글별 제목 패턴 분석:")
        
        title_patterns = Counter()
        bible_books_found = Counter()
        
        for article_id, title in article_titles.items():
            if pd.isna(title):
                continue
                
            # 호크마 주석 패턴 찾기
            if '호크마' in title:
                print(f"  {article_id}: {title}")
                
                # 성경책명 패턴 찾기
                bible_pattern = r'호크마 주석[,\s]*([가-힣]+서?(?:상|하)?(?:전서|후서)?(?:일서|이서|삼서)?(?:복음)?(?:기)?(?:애가)?)\s*(\d+)장'
                match = re.search(bible_pattern, title)
                if match:
                    book_name = match.group(1)
                    chapter = match.group(2)
                    bible_books_found[book_name] += 1
                    print(f"    → 성경책: {book_name}, 장: {chapter}")
        
        print(f"\n--- 발견된 성경책들 ---")
        for book, count in bible_books_found.most_common():
            print(f"  {book}: {count}개 게시글")
        
        return df, bible_books_found
        
    except Exception as e:
        print(f"❌ 분석 실패: {e}")
        return None, None

def test_title_extraction():
    """제목에서 성경책명 추출 테스트"""
    print("\n🧪 제목에서 성경책명 추출 테스트...")
    
    # 다양한 패턴 테스트
    test_titles = [
        "호크마 주석, 창세기 1장",
        "호크마 주석, 출애굽기 20장", 
        "호크마 주석, 사무엘상 1장",
        "호크마 주석, 고린도전서 1장",
        "호크마 주석, 요한일서 1장",
        "성경주석HANGL 한글|HebraecaAramaica ANglicaGraecaLatina|..."
    ]
    
    patterns = [
        r'호크마 주석[,\s]*([가-힣]+(?:상|하)?(?:전서|후서)?(?:일서|이서|삼서)?(?:복음)?(?:기)?(?:애가)?)\s*(\d+)장',
        r'호크마 주석[,\s]*([가-힣]+서?(?:상|하)?(?:전서|후서)?(?:일서|이서|삼서)?(?:복음)?(?:기)?(?:애가)?)\s*(\d+)장',
        r'호크마[^,]*,\s*([가-힣]+(?:상|하)?(?:전서|후서)?(?:일서|이서|삼서)?(?:복음)?(?:기)?(?:애가)?)\s*(\d+)장'
    ]
    
    for title in test_titles:
        print(f"\n제목: {title}")
        for i, pattern in enumerate(patterns):
            match = re.search(pattern, title)
            if match:
                book_name = match.group(1)
                chapter = match.group(2)
                print(f"  패턴 {i+1}: 성경책='{book_name}', 장='{chapter}'")
            else:
                print(f"  패턴 {i+1}: 매치 안됨")

def main():
    """메인 함수"""
    print("🔍 엑셀 파일 상세 분석 및 성경책명 추출 테스트")
    print("=" * 60)
    
    # 1. 엑셀 구조 분석
    df, bible_books = analyze_excel_structure()
    
    # 2. 제목 추출 테스트
    test_title_extraction()
    
    if df is not None:
        print(f"\n📊 요약:")
        print(f"  - 총 행 수: {len(df):,}")
        print(f"  - 고유 게시글 수: {df['article_id'].nunique()}")
        print(f"  - 발견된 성경책 수: {len(bible_books) if bible_books else 0}")

if __name__ == "__main__":
    main() 