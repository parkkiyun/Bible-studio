from fixed_line_based_parser import FixedLineBasedHochmaParser

def test_fixed_parser():
    """수정된 줄바꿈 기반 파서 테스트"""
    parser = FixedLineBasedHochmaParser()
    
    print("🔍 139453 게시글 테스트 (수정된 <br> 처리)")
    print("=" * 50)
    
    result = parser.parse_to_excel('139453', 'fixed_139453.xlsx')
    
    if result:
        print(f"\n✅ 파싱 성공!")
        print(f"  - 파일: {result['excel_file']}")
        print(f"  - 패턴: {result['article_data']['pattern_info']}")
        print(f"  - 절 수: {len(result['dataframe'])}")
        
        # 절 구분자별 통계 확인
        if '절_구분자' in result['dataframe'].columns:
            separator_counts = result['dataframe']['절_구분자'].value_counts()
            print(f"\n📊 절 구분자 통계:")
            for separator, count in separator_counts.items():
                print(f"  - '{separator}': {count}개")
        
        # 처음 10개 절 미리보기
        print(f"\n🔍 처음 10개 절:")
        df = result['dataframe']
        for i in range(min(10, len(df))):
            row = df.iloc[i]
            print(f"  [{i+1:2}] {row['성경책']} {row['장']}:{row['절']} ({row['내용_길이']}자)")
            if '절_구분자' in row:
                print(f"       구분자: '{row['절_구분자']}'")
            print(f"       내용: {row['주석_내용'][:80]}...")
            
        # 고유 절 번호 확인
        unique_verses = df[['장', '절']].drop_duplicates().sort_values(['장', '절'])
        print(f"\n📋 파싱된 절 번호들 (총 {len(unique_verses)}개):")
        verse_list = []
        for _, row in unique_verses.iterrows():
            verse_list.append(f"{row['장']}:{row['절']}")
        
        # 20개씩 줄로 표시
        for i in range(0, len(verse_list), 20):
            line_verses = verse_list[i:i+20]
            print(f"  {', '.join(line_verses)}")
            
    else:
        print("❌ 파싱 실패")

if __name__ == "__main__":
    test_fixed_parser() 