# 성경 본문 + 호크마 주석 통합 활용 가이드

## 📋 개요
이제 `bible_database.db` 하나의 데이터베이스에서 **성경 본문**과 **호크마 주석**을 함께 조회할 수 있습니다.

## 🗄️ 데이터베이스 구조

### 1. `verses` 테이블 (기존 성경 본문)
```sql
CREATE TABLE verses (
    id INTEGER PRIMARY KEY,
    book_name TEXT NOT NULL,      -- 성경책 이름 (예: "창세기")
    book_code INTEGER NOT NULL,   -- 성경책 코드 (1-66)
    chapter INTEGER NOT NULL,     -- 장 번호
    verse INTEGER NOT NULL,       -- 절 번호
    text TEXT NOT NULL,          -- 성경 본문
    version TEXT NOT NULL,       -- 성경 버전 (예: "korean-traditional")
    verse_title TEXT             -- 절 제목 (대부분 NULL)
);
```

### 2. `commentaries` 테이블 (호크마 주석)
```sql
CREATE TABLE commentaries (
    id INTEGER PRIMARY KEY,
    book_name TEXT NOT NULL,      -- 성경책 이름 (예: "창세기")
    book_code INTEGER NOT NULL,   -- 성경책 코드 (1-66)
    chapter INTEGER NOT NULL,     -- 장 번호
    verse INTEGER NOT NULL,       -- 절 번호
    text TEXT NOT NULL,          -- 주석 내용
    version TEXT NOT NULL,       -- 주석 버전 (예: "호크마 주석-commentary")
    verse_title TEXT,            -- 절 제목
    commentary_name TEXT NOT NULL, -- 주석명 (예: "호크마 주석")
    original_url TEXT,           -- 원본 URL
    parsed_date TIMESTAMP        -- 파싱 날짜
);
```

## 🔍 통합 조회 방법

### 1. 특정 절의 성경 본문 + 주석 조회
```sql
-- 창세기 31장 1절의 성경 본문과 호크마 주석 함께 조회
SELECT 
    v.text as 성경본문,
    c.text as 호크마주석,
    c.commentary_name as 주석명
FROM verses v
LEFT JOIN commentaries c ON 
    v.book_name = c.book_name AND 
    v.chapter = c.chapter AND 
    v.verse = c.verse
WHERE v.book_name = '창세기' 
    AND v.chapter = 31 
    AND v.verse = 1 
    AND v.version = 'korean-traditional';
```

### 2. 특정 장의 모든 절 + 주석 조회
```sql
-- 창세기 31장 전체 성경 본문과 주석 조회
SELECT 
    v.verse as 절,
    v.text as 성경본문,
    c.text as 호크마주석
FROM verses v
LEFT JOIN commentaries c ON 
    v.book_name = c.book_name AND 
    v.chapter = c.chapter AND 
    v.verse = c.verse AND
    c.commentary_name = '호크마 주석'
WHERE v.book_name = '창세기' 
    AND v.chapter = 31 
    AND v.version = 'korean-traditional'
ORDER BY v.verse;
```

### 3. 주석이 있는 절만 조회
```sql
-- 호크마 주석이 있는 창세기 절들만 조회
SELECT 
    v.chapter as 장,
    v.verse as 절,
    v.text as 성경본문,
    c.text as 호크마주석
FROM verses v
INNER JOIN commentaries c ON 
    v.book_name = c.book_name AND 
    v.chapter = c.chapter AND 
    v.verse = c.verse
WHERE v.book_name = '창세기' 
    AND v.version = 'korean-traditional'
    AND c.commentary_name = '호크마 주석'
ORDER BY v.chapter, v.verse;
```

## 🐍 Python 활용 예제

### 1. 통합 조회 클래스
```python
import sqlite3

class BibleCommentaryReader:
    def __init__(self, db_path="bible_database.db"):
        self.db_path = db_path
    
    def get_verse_with_commentary(self, book_name, chapter, verse, 
                                  bible_version="korean-traditional",
                                  commentary_name="호크마 주석"):
        """특정 절의 성경 본문과 주석을 함께 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = """
        SELECT 
            v.text as bible_text,
            c.text as commentary_text,
            c.commentary_name
        FROM verses v
        LEFT JOIN commentaries c ON 
            v.book_name = c.book_name AND 
            v.chapter = c.chapter AND 
            v.verse = c.verse AND
            c.commentary_name = ?
        WHERE v.book_name = ? 
            AND v.chapter = ? 
            AND v.verse = ?
            AND v.version = ?
        """
        
        cursor.execute(query, (commentary_name, book_name, chapter, verse, bible_version))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'book_name': book_name,
                'chapter': chapter,
                'verse': verse,
                'bible_text': result[0],
                'commentary_text': result[1],
                'commentary_name': result[2]
            }
        return None
    
    def get_chapter_with_commentary(self, book_name, chapter, 
                                   bible_version="korean-traditional",
                                   commentary_name="호크마 주석"):
        """특정 장의 모든 절과 주석을 함께 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = """
        SELECT 
            v.verse,
            v.text as bible_text,
            c.text as commentary_text
        FROM verses v
        LEFT JOIN commentaries c ON 
            v.book_name = c.book_name AND 
            v.chapter = c.chapter AND 
            v.verse = c.verse AND
            c.commentary_name = ?
        WHERE v.book_name = ? 
            AND v.chapter = ? 
            AND v.version = ?
        ORDER BY v.verse
        """
        
        cursor.execute(query, (commentary_name, book_name, chapter, bible_version))
        results = cursor.fetchall()
        conn.close()
        
        return [{
            'verse': row[0],
            'bible_text': row[1],
            'commentary_text': row[2]
        } for row in results]

# 사용 예제
reader = BibleCommentaryReader()

# 창세기 31장 1절 조회
verse_data = reader.get_verse_with_commentary('창세기', 31, 1)
print(f"성경 본문: {verse_data['bible_text']}")
print(f"호크마 주석: {verse_data['commentary_text'][:100]}...")

# 창세기 31장 전체 조회
chapter_data = reader.get_chapter_with_commentary('창세기', 31)
print(f"창세기 31장 총 {len(chapter_data)}절")
```

### 2. 주석 통계 조회
```python
def get_commentary_statistics():
    """주석 통계 정보 조회"""
    conn = sqlite3.connect("bible_database.db")
    cursor = conn.cursor()
    
    # 주석이 있는 성경책별 통계
    cursor.execute("""
        SELECT 
            book_name,
            COUNT(DISTINCT chapter) as chapters_with_commentary,
            COUNT(*) as total_verses_with_commentary
        FROM commentaries 
        GROUP BY book_name 
        ORDER BY book_code
    """)
    
    stats = cursor.fetchall()
    conn.close()
    
    return stats
```

## 🎯 활용 시나리오

### 1. 설교 준비
- 특정 구절의 성경 본문과 호크마 주석을 함께 조회
- 한 장 전체의 본문과 주석을 순서대로 읽기

### 2. 성경 공부
- 어려운 구절에 대한 주석 확인
- 성경 본문과 주석을 비교하며 이해 심화

### 3. 앱/웹 개발
- API 형태로 성경 본문과 주석 데이터 제공
- 사용자가 원하는 버전의 성경과 주석을 선택적으로 표시

## 📊 데이터 현황 (예시)
- **성경 본문**: 217,632개 절 (66권 전체)
- **호크마 주석**: 현재 창세기 31장 24개 절 (확장 예정)
- **통합 데이터베이스**: `bible_database.db` 하나로 모든 데이터 관리

## 🚀 확장 가능성
1. **다른 주석서 추가**: 매튜 헨리 주석, 존 칼빈 주석 등
2. **다양한 성경 버전**: 새번역, 현대인의 성경 등
3. **검색 기능**: 전문 검색, 키워드 검색
4. **연관 구절**: 관련 구절 자동 연결

이제 성경 본문과 호크마 주석을 하나의 통합된 시스템에서 활용할 수 있습니다! 🎉 