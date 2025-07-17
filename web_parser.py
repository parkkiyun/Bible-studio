import requests
from bs4 import BeautifulSoup
import json
import csv
from urllib.parse import urljoin, urlparse
import time
import re

class WebParser:
    def __init__(self, headers=None):
        """
        웹 파서 초기화
        
        Args:
            headers (dict): HTTP 요청 헤더
        """
        self.session = requests.Session()
        self.headers = headers or {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session.headers.update(self.headers)
    
    def fetch_page(self, url, timeout=10):
        """
        웹 페이지를 가져오기
        
        Args:
            url (str): 가져올 웹 페이지 URL
            timeout (int): 요청 타임아웃
            
        Returns:
            requests.Response: HTTP 응답 객체
        """
        try:
            # URL에 스키마가 없으면 https:// 추가
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            print(f"페이지 가져오기 실패: {e}")
            return None
    
    def parse_html(self, html_content):
        """
        HTML 내용을 파싱하기
        
        Args:
            html_content (str): HTML 문자열
            
        Returns:
            BeautifulSoup: 파싱된 HTML 객체
        """
        return BeautifulSoup(html_content, 'html.parser')
    
    def extract_text(self, soup, selector=None):
        """
        텍스트 추출
        
        Args:
            soup (BeautifulSoup): 파싱된 HTML 객체
            selector (str): CSS 선택자 (선택사항)
            
        Returns:
            str: 추출된 텍스트
        """
        if selector:
            elements = soup.select(selector)
            return [elem.get_text(strip=True) for elem in elements]
        else:
            return soup.get_text(strip=True)
    
    def extract_links(self, soup, base_url=None):
        """
        링크 추출
        
        Args:
            soup (BeautifulSoup): 파싱된 HTML 객체
            base_url (str): 기본 URL (상대 링크 처리용)
            
        Returns:
            list: 링크 리스트
        """
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            if base_url:
                href = urljoin(base_url, href)
            links.append({
                'text': link.get_text(strip=True),
                'url': href
            })
        return links
    
    def extract_images(self, soup, base_url=None):
        """
        이미지 추출
        
        Args:
            soup (BeautifulSoup): 파싱된 HTML 객체
            base_url (str): 기본 URL (상대 링크 처리용)
            
        Returns:
            list: 이미지 리스트
        """
        images = []
        for img in soup.find_all('img'):
            src = img.get('src')
            if src:
                if base_url:
                    src = urljoin(base_url, src)
                images.append({
                    'src': src,
                    'alt': img.get('alt', ''),
                    'title': img.get('title', '')
                })
        return images
    
    def extract_meta_data(self, soup):
        """
        메타데이터 추출
        
        Args:
            soup (BeautifulSoup): 파싱된 HTML 객체
            
        Returns:
            dict: 메타데이터
        """
        meta_data = {}
        
        # 제목
        title = soup.find('title')
        if title:
            meta_data['title'] = title.get_text(strip=True)
        
        # 메타 태그
        for meta in soup.find_all('meta'):
            name = meta.get('name') or meta.get('property')
            content = meta.get('content')
            if name and content:
                meta_data[name] = content
        
        return meta_data
    
    def extract_table_data(self, soup, table_selector='table'):
        """
        테이블 데이터 추출
        
        Args:
            soup (BeautifulSoup): 파싱된 HTML 객체
            table_selector (str): 테이블 CSS 선택자
            
        Returns:
            list: 테이블 데이터 리스트
        """
        tables = []
        for table in soup.select(table_selector):
            table_data = []
            
            # 헤더 추출
            headers = []
            header_row = table.find('tr')
            if header_row:
                for th in header_row.find_all(['th', 'td']):
                    headers.append(th.get_text(strip=True))
            
            # 데이터 행 추출
            for row in table.find_all('tr')[1:]:  # 첫 번째 행은 헤더로 간주
                row_data = []
                for cell in row.find_all(['td', 'th']):
                    row_data.append(cell.get_text(strip=True))
                if row_data:
                    table_data.append(row_data)
            
            tables.append({
                'headers': headers,
                'data': table_data
            })
        
        return tables
    
    def save_to_json(self, data, filename):
        """
        JSON 파일로 저장
        
        Args:
            data: 저장할 데이터
            filename (str): 파일명
        """
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"데이터가 {filename}에 저장되었습니다.")
    
    def save_to_csv(self, data, filename):
        """
        CSV 파일로 저장
        
        Args:
            data (list): 저장할 데이터 (리스트 형태)
            filename (str): 파일명
        """
        if not data:
            print("저장할 데이터가 없습니다.")
            return
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            if isinstance(data[0], dict):
                fieldnames = data[0].keys()
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            else:
                writer = csv.writer(f)
                writer.writerows(data)
        print(f"데이터가 {filename}에 저장되었습니다.")
    
    def parse_website(self, url, extract_options=None):
        """
        웹사이트 종합 파싱
        
        Args:
            url (str): 파싱할 웹사이트 URL
            extract_options (dict): 추출 옵션
            
        Returns:
            dict: 파싱 결과
        """
        extract_options = extract_options or {
            'text': True,
            'links': True,
            'images': True,
            'meta': True,
            'tables': True
        }
        
        # 페이지 가져오기
        response = self.fetch_page(url)
        if not response:
            return None
        
        # HTML 파싱
        soup = self.parse_html(response.text)
        
        result = {
            'url': url,
            'status_code': response.status_code,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # 각종 데이터 추출
        if extract_options.get('text'):
            result['text'] = self.extract_text(soup)
        
        if extract_options.get('links'):
            result['links'] = self.extract_links(soup, url)
        
        if extract_options.get('images'):
            result['images'] = self.extract_images(soup, url)
        
        if extract_options.get('meta'):
            result['meta_data'] = self.extract_meta_data(soup)
        
        if extract_options.get('tables'):
            result['tables'] = self.extract_table_data(soup)
        
        return result


def main():
    """
    메인 함수 - 사용 예제
    """
    # 웹 파서 초기화
    parser = WebParser()
    
    # 파싱할 URL
    url = input("파싱할 웹사이트 URL을 입력하세요: ")
    
    if not url:
        print("URL이 입력되지 않았습니다.")
        return
    
    # 웹사이트 파싱
    print(f"웹사이트 파싱 중: {url}")
    result = parser.parse_website(url)
    
    if result:
        print(f"\n파싱 완료!")
        print(f"상태 코드: {result['status_code']}")
        print(f"제목: {result.get('meta_data', {}).get('title', 'N/A')}")
        print(f"링크 개수: {len(result.get('links', []))}")
        print(f"이미지 개수: {len(result.get('images', []))}")
        print(f"테이블 개수: {len(result.get('tables', []))}")
        
        # 결과 저장
        save_option = input("\n결과를 저장하시겠습니까? (y/n): ")
        if save_option.lower() == 'y':
            filename = input("파일명을 입력하세요 (확장자 제외): ")
            if filename:
                parser.save_to_json(result, f"{filename}.json")
                
                # 링크만 별도로 CSV 저장
                if result.get('links'):
                    parser.save_to_csv(result['links'], f"{filename}_links.csv")
    else:
        print("웹사이트 파싱에 실패했습니다.")


if __name__ == "__main__":
    main() 