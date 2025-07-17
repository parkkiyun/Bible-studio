from line_based_parser import LineBasedHochmaParser

def test_line_based():
    """줄바꿈 기반 파서 테스트"""
    parser = LineBasedHochmaParser()
    
    print("🔍 139453 게시글 테스트 (줄바꿈 기반 파서)")
    print("=" * 50)
    
    result = parser.parse_to_excel('139453', 'line_based_139453.xlsx')
    
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
        
        # 처음 5개 절 미리보기
        print(f"\n🔍 처음 5개 절:")
        df = result['dataframe']
        for i in range(min(5, len(df))):
            row = df.iloc[i]
            print(f"  [{i+1}] {row['성경책']} {row['장']}:{row['절']} ({row['내용_길이']}자)")
            if '절_구분자' in row:
                print(f"      구분자: '{row['절_구분자']}'")
            print(f"      내용: {row['주석_내용'][:80]}...")
    else:
        print("❌ 파싱 실패")

if __name__ == "__main__":
    test_line_based() 