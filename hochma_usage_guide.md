# 호크마 성경주석 파서 사용 가이드

[https://nocr.net/com_kor_hochma](https://nocr.net/com_kor_hochma) 사이트의 성경주석을 자동으로 파싱하여 SQLite 데이터베이스에 저장하는 도구입니다.

## 🚀 빠른 시작

### 1. 프로그램 실행
```bash
python hochma_parser.py
```

### 2. 기본 기능들

#### ✅ 단일 게시글 파싱
- 메뉴에서 `1` 선택
- 게시글 ID 입력 (예: `139393`)
- 자동으로 제목과 본문을 추출하여 데이터베이스에 저장

#### ✅ 범위 게시글 파싱
- 메뉴에서 `2` 선택
- 시작 ID와 종료 ID 입력 (예: 139393 ~ 139400)
- 지연 시간 설정 (서버 부하 방지, 기본 1초)
- 범위 내 모든 게시글을 순차적으로 파싱

#### ✅ 데이터베이스 조회
- 메뉴에서 `3` 선택
- 성경책 이름으로 필터링 가능 (예: "창세기")
- 조회 개수 제한 설정 가능

#### ✅ JSON 내보내기
- 메뉴에서 `4` 선택
- 파일명 입력
- 전체 또는 특정 성경책만 내보내기

#### ✅ 통계 보기
- 메뉴에서 `5` 선택
- 총 게시글 수, 성경책별 게시글 수 확인

## 📊 데이터베이스 구조

```sql
CREATE TABLE articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id TEXT UNIQUE,           -- 게시글 ID (139393)
    url TEXT UNIQUE,                  -- 전체 URL
    title TEXT,                       -- 제목 ("호크마 주석, 창세기 01장")
    content TEXT,                     -- 본문 내용
    book_name TEXT,                   -- 성경책 이름 ("창세기")
    chapter TEXT,                     -- 장 번호 ("01")
    parsed_date TIMESTAMP,            -- 파싱 일시
    created_at TIMESTAMP              -- 생성 일시
);
```

## 🎯 활용 예시

### 창세기 전체 파싱
```bash
# 프로그램 실행 후 메뉴에서:
# 2 선택 (범위 파싱)
# 시작 ID: 139393 (창세기 1장)
# 종료 ID: 139442 (창세기 50장)
# 지연: 1 (1초 간격)
```

### 특정 성경책 조회
```bash
# 프로그램 실행 후 메뉴에서:
# 3 선택 (데이터베이스 조회)
# 성경책 이름: 창세기
# 조회 개수: 10
```

### 데이터 내보내기
```bash
# 프로그램 실행 후 메뉴에서:
# 4 선택 (JSON 내보내기)
# 파일명: genesis_commentary
# 성경책: 창세기
# → genesis_commentary.json 파일 생성
```

## 📋 주요 기능

- ✅ **정확한 제목 추출**: "호크마 주석, 창세기 XX장" 형식 자동 인식
- ✅ **깔끔한 본문 추출**: HTML 태그 제거, 핵심 내용만 추출
- ✅ **성경책/장 자동 분류**: 제목에서 성경책명과 장 번호 자동 추출
- ✅ **중복 방지**: 같은 게시글 재파싱시 업데이트
- ✅ **한글 인코딩**: UTF-8 완벽 지원
- ✅ **서버 부하 최소화**: 요청 간격 조절 가능
- ✅ **다양한 내보내기**: JSON, CSV 형식 지원

## ⚠️ 사용시 주의사항

1. **적절한 지연 시간**: 서버에 부하를 주지 않도록 1초 이상 지연 권장
2. **저작권 존중**: 개인 연구/학습 목적으로만 사용
3. **대량 파싱**: 한번에 너무 많은 게시글을 파싱하지 말고 적절히 분할
4. **백업**: 중요한 데이터는 정기적으로 JSON으로 백업

## 🔧 고급 사용법

### Python 코드에서 직접 사용
```python
from hochma_parser import HochmaParser

# 파서 초기화
parser = HochmaParser("my_database.db")

# 단일 게시글 파싱
result = parser.parse_single_article("139393")

# 범위 파싱
articles = parser.parse_article_range(139393, 139395, delay=1)

# 데이터베이스 조회
genesis_articles = parser.get_articles_from_db(book_name="창세기")

# 통계 정보
stats = parser.get_statistics()
print(f"총 {stats['total_articles']}개 게시글")
```

## 📈 성능 정보

- **파싱 속도**: 약 1-2초/게시글 (지연 시간 포함)
- **저장 공간**: 평균 15-30KB/게시글
- **메모리 사용량**: 최소 (~50MB)
- **동시 처리**: 순차 처리 (서버 부하 방지)

---

문의사항이나 개선 제안이 있으시면 언제든 말씀해주세요! 🙏 