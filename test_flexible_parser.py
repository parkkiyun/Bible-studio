from flexible_hochma_parser import FlexibleHochmaParser

def test_flexible_parser():
    """유연한 파서 테스트"""
    parser = FlexibleHochmaParser()
    
    # 기존 패턴 테스트 (창세기 31장)
    print("🔍 기존 패턴 테스트")
    print("=" * 40)
    
    article_id = "139477"  # 창세기 31장 (equals_any 패턴)
    result = parser.parse_to_excel(article_id, "test_flexible_창세기31장.xlsx")
    
    if result:
        print(f"✅ {result['article_data']['pattern_info']['type']} 패턴 성공")
        print(f"   절 수: {len(result['dataframe'])}")
        print(f"   파일: {result['excel_file']}")
    
    # 새로운 패턴 테스트를 위한 준비
    print(f"\n🆕 새로운 패턴 테스트 준비")
    print("=" * 40)
    print("새로운 패턴(line_start)이 있는 게시글 ID를 제공해주세요.")
    print("예: 19:1, 19:2, 19:3 형태로 절이 구분된 게시글")
    
    # 사용자 입력 대기
    new_id = input("새 패턴 게시글 ID (없으면 엔터): ").strip()
    
    if new_id:
        print(f"\n새로운 패턴 테스트 중...")
        new_result = parser.parse_to_excel(new_id, f"test_new_pattern_{new_id}.xlsx")
        
        if new_result:
            pattern_type = new_result['article_data']['pattern_info']['type']
            print(f"✅ {pattern_type} 패턴 성공")
            print(f"   절 수: {len(new_result['dataframe'])}")
            print(f"   파일: {new_result['excel_file']}")
            
            # 처음 3개 절 미리보기
            print(f"\n처음 3개 절 미리보기:")
            df = new_result['dataframe']
            for i in range(min(3, len(df))):
                row = df.iloc[i]
                print(f"  [{i+1}] {row['성경책']} {row['장']}:{row['절']} ({row['내용_길이']}자)")
                print(f"      {row['주석_내용'][:80]}...")
        else:
            print("❌ 새 패턴 테스트 실패")

if __name__ == "__main__":
    test_flexible_parser() 