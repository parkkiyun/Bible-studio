# 웹 페이지 파서 (Web Page Parser)

Python을 사용한 강력하고 간편한 웹 페이지 파싱 도구입니다.

## 🚀 주요 기능

- **웹 페이지 다운로드**: HTTP/HTTPS 웹 페이지 자동 다운로드
- **HTML 파싱**: BeautifulSoup을 사용한 정확한 HTML 구조 분석
- **다양한 데이터 추출**:
  - 텍스트 내용 추출
  - 모든 링크와 링크 텍스트 수집
  - 이미지 URL과 속성 정보 추출
  - 메타데이터 (제목, 메타 태그) 수집
  - HTML 테이블을 구조화된 데이터로 변환
- **유연한 데이터 저장**: JSON, CSV 형식으로 결과 저장
- **CSS 선택자 지원**: 특정 요소만 선택적으로 추출 가능

## 🛠️ 설치 방법

1. 필요한 패키지 설치:
   ```bash
   pip install -r requirements.txt
   ```

## 📖 사용 방법

### 1. 기본 사용법

```python
from web_parser import WebParser

# 웹 파서 초기화
parser = WebParser()

# 웹사이트 파싱
result = parser.parse_website("https://example.com")

if result:
    print(f"제목: {result['meta_data']['title']}")
    print(f"링크 개수: {len(result['links'])}")
    print(f"이미지 개수: {len(result['images'])}")
```

### 2. 명령줄에서 사용

```bash
python web_parser.py
```

실행 후 파싱할 웹사이트 URL을 입력하면 됩니다.

### 3. 예제 프로그램 실행

```bash
python example_usage.py
```

다양한 사용 예제를 선택하여 실행할 수 있습니다.

## 📋 WebParser 클래스 주요 메서드

### `parse_website(url, extract_options=None)`
웹사이트를 종합적으로 파싱합니다.

**매개변수:**
- `url` (str): 파싱할 웹사이트 URL
- `extract_options` (dict): 추출할 데이터 옵션
  ```python
  {
      'text': True,    # 텍스트 추출
      'links': True,   # 링크 추출
      'images': True,  # 이미지 추출
      'meta': True,    # 메타데이터 추출
      'tables': True   # 테이블 추출
  }
  ```

### `extract_text(soup, selector=None)`
텍스트를 추출합니다.

```python
# 전체 텍스트 추출
text = parser.extract_text(soup)

# CSS 선택자로 특정 요소의 텍스트만 추출
headlines = parser.extract_text(soup, 'h1, h2, h3')
```

### `extract_links(soup, base_url=None)`
모든 링크를 추출합니다.

### `extract_images(soup, base_url=None)`
모든 이미지 정보를 추출합니다.

### `extract_table_data(soup, table_selector='table')`
HTML 테이블을 구조화된 데이터로 변환합니다.

### `save_to_json(data, filename)`
데이터를 JSON 파일로 저장합니다.

### `save_to_csv(data, filename)`
데이터를 CSV 파일로 저장합니다.

## 🔧 사용 예제

### 특정 요소만 추출하기

```python
parser = WebParser()

# 링크와 메타데이터만 추출
options = {
    'text': False,
    'links': True,
    'images': False,
    'meta': True,
    'tables': False
}

result = parser.parse_website("https://example.com", options)
```

### CSS 선택자 사용하기

```python
parser = WebParser()
response = parser.fetch_page("https://example.com")
soup = parser.parse_html(response.text)

# 모든 헤드라인 추출
headlines = parser.extract_text(soup, 'h1, h2, h3')

# 특정 클래스의 요소만 추출
articles = parser.extract_text(soup, '.article-content')
```

### 데이터 저장하기

```python
parser = WebParser()
result = parser.parse_website("https://example.com")

# 전체 결과를 JSON으로 저장
parser.save_to_json(result, "website_data.json")

# 링크만 CSV로 저장
parser.save_to_csv(result['links'], "extracted_links.csv")
```

## 🌟 활용 사례

- **뉴스 사이트 모니터링**: 최신 뉴스 헤드라인과 링크 수집
- **전자상거래 데이터 수집**: 상품 정보와 가격 모니터링
- **소셜 미디어 분석**: 게시물과 링크 분석
- **웹사이트 구조 분석**: 사이트맵 생성과 링크 구조 파악
- **콘텐츠 아카이빙**: 웹 페이지 내용 백업과 보관

## ⚠️ 주의사항

- 웹사이트의 robots.txt와 이용약관을 준수하세요
- 과도한 요청으로 서버에 부하를 주지 않도록 주의하세요
- 개인정보와 저작권을 존중하세요
- 일부 웹사이트는 자바스크립트가 필요할 수 있습니다 (이 경우 Selenium 등의 도구가 필요)

## 🤝 기여하기

버그 리포트나 기능 제안은 언제든 환영합니다!

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 