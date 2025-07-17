from excel_hochma_parser import ExcelHochmaParser

def test_excel_parser():
    """엑셀 파서 테스트"""
    parser = ExcelHochmaParser()
    
    # 창세기 31장 (139477) 테스트
    article_id = "139477"
    print(f"테스트: 창세기 31장 (ID: {article_id})")
    
    # 엑셀 파일로 저장
    result = parser.parse_to_excel(article_id)
    
    if result:
        print(f"\n✓ 엑셀 파일 생성 성공!")
        print(f"  파일명: {result['excel_file']}")
        print(f"  주석 절 수: {len(result['dataframe'])}")
        
        # 처음 5개 절 미리보기
        print("\n처음 5개 절 미리보기:")
        print(result['dataframe'][['장', '절', '내용_길이']].head())
        
        return result['excel_file']
    else:
        print("✗ 엑셀 파일 생성 실패")
        return None

if __name__ == "__main__":
    test_excel_parser() 