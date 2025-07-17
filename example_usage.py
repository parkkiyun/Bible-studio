from web_parser import WebParser

def example_basic_parsing():
    """
    기본 웹 파싱 예제
    """
    parser = WebParser()
    
    # 네이버 뉴스 예제
    url = "https://news.naver.com"
    
    print(f"웹사이트 파싱 중: {url}")
    result = parser.parse_website(url)
    
    if result:
        print(f"\n=== 파싱 결과 ===")
        print(f"URL: {result['url']}")
        print(f"상태 코드: {result['status_code']}")
        print(f"제목: {result.get('meta_data', {}).get('title', 'N/A')}")
        print(f"링크 개수: {len(result.get('links', []))}")
        print(f"이미지 개수: {len(result.get('images', []))}")
        
        # 첫 번째 몇 개 링크 출력
        print("\n=== 상위 5개 링크 ===")
        for i, link in enumerate(result.get('links', [])[:5]):
            print(f"{i+1}. {link['text'][:50]}... -> {link['url']}")
    
    return result

def example_custom_parsing():
    """
    커스텀 파싱 예제 - 특정 요소만 추출
    """
    parser = WebParser()
    
    url = "https://example.com"
    
    # 특정 옵션만 활성화
    options = {
        'text': False,
        'links': True,
        'images': False,
        'meta': True,
        'tables': False
    }
    
    result = parser.parse_website(url, extract_options=options)
    
    if result:
        print(f"\n=== 커스텀 파싱 결과 ===")
        print(f"메타데이터: {result.get('meta_data')}")
        print(f"링크 개수: {len(result.get('links', []))}")
    
    return result

def example_specific_content():
    """
    특정 CSS 선택자를 사용한 내용 추출 예제
    """
    parser = WebParser()
    
    url = "https://example.com"
    response = parser.fetch_page(url)
    
    if response:
        soup = parser.parse_html(response.text)
        
        # 특정 선택자로 텍스트 추출
        headlines = parser.extract_text(soup, 'h1, h2, h3')
        print(f"\n=== 헤드라인 추출 ===")
        for i, headline in enumerate(headlines[:10]):
            print(f"{i+1}. {headline}")
    
    return headlines

def example_save_data():
    """
    데이터 저장 예제
    """
    parser = WebParser()
    
    url = "https://example.com"
    result = parser.parse_website(url)
    
    if result:
        # JSON으로 저장
        parser.save_to_json(result, "parsed_data.json")
        
        # 링크만 CSV로 저장
        if result.get('links'):
            parser.save_to_csv(result['links'], "extracted_links.csv")
        
        print("데이터 저장 완료!")

if __name__ == "__main__":
    print("웹 파서 사용 예제\n")
    
    # 원하는 예제를 선택하여 실행
    print("1. 기본 파싱 예제")
    print("2. 커스텀 파싱 예제")
    print("3. 특정 내용 추출 예제")
    print("4. 데이터 저장 예제")
    
    choice = input("\n실행할 예제 번호를 입력하세요 (1-4): ")
    
    if choice == '1':
        example_basic_parsing()
    elif choice == '2':
        example_custom_parsing()
    elif choice == '3':
        example_specific_content()
    elif choice == '4':
        example_save_data()
    else:
        print("잘못된 선택입니다.") 