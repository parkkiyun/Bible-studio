import requests
from bs4 import BeautifulSoup
import re

def analyze_new_pattern():
    """새로운 패턴 분석"""
    
    # 테스트용 샘플 텍스트 (이미지에서 본 내용 기반)
    sample_text = """19:1

저물 때에 - 소돔성의 타락상을 바로 살필 수 있는 최적의 때이다. 왜냐하면 음란과 음란과 방탕, 각종 사악한 죄악들이 활개치는 때는 주로 어두운 밤 시간이기 때문이다(창 7:7-9). 이런 의미에서 어두움은 성경상 죄악의 신세를 상징한다. 따라서 예수께서 이 세상에 빛으로 오셨때에도 어두움을 사랑한 유대인들은 그를 영접지 않고 십자가에 못박아 죽였다(요 1:4-11;19:15). 오늘날 여전히 어두움의 때에 처해있는 우리들(눅 22:53) 역시 불법과 각종 죄악의 올무에 걸려 넘어지지 않도록 항상 깨어 근신하고 있어야 할 것이다(살전 5:6).

두천사 - 타락한 소돔 성을 불로 심판할 목적을 띠고 하나님께로부터 파송된 '분노의 천사'(삼하 24:16)들이다(18:22).

성문에 앉았다가 - 고대 사회에서 성문은 재판장소, 사업 거래소, 고지(告知) 장소 및 사교생활의 주요 무대였다(신 21:19;수 20:4;왕하 7:1;느 13:19;시 69:12;잠1:21). 따라서 성문에는 언제나 사람들이 붐볐는데 롯이 그곳에 앉아 있었다는 것은 지도층 인사로서 그곳 거민들에게 상당한 영향을 미치고 있었음을 추측케 해준다.

일어나 영접하고 - 숙부 아브라함에게서 볼 수 있었던 것과 동일한 나그네 대접 행위이다. 이러한 롯의 진실은 소돔 주민들과는 달리(4-9절) 희미하게나마 아직도 롯에게 남아 있는 경건성의 반영이다(벧후2:7,8).

그러나 그의 경건적인 장모은 죄악으로 가득찬 타락의 도시 소돔을 과감히 떠나지 않고 계속 그들 속에 함께 서여 산 데 있다(살전 5:22).

19:2

내 주여 - 이 역시 아브라함의 경우와 마찬가지로 롯도 천사들의 신분을 알지 못한 채 단순히 일반적인 존칭어를 사용한 것에 불과하다.

거리에서 경야하리라 - '거리'에 해당하는 히브리어 '레호브'( )는 '넓은 공터', 즉 성문 앞의 '광장'을 의미한다. 삿 19:15에 의하면 집으로 초대받지 못한 여행자들은 이러한 성읍의 광거리서 유숙하곤 하였음을 알 수 있다. 그러나 천사들이 롯의 초대에도 불구하고 거리에서 밤을 지새우겠다 하였으니 소돔의 타락상을 구체적으로 시찰하기 위함이었다.

19:3

식탁( , 미쉬테) - '상차'(마시다, 술취하다)에서 온 말로 '마실 것', '향연'의미한다. 이는 여행 끝에 지친 나그네들을 위해 우선적으로 음료수나 포도주를 대접한 것을 나타낸다."""
    
    print("🔍 새로운 패턴 분석")
    print("=" * 50)
    
    # 1. 줄 시작 부분의 절 번호 패턴 찾기
    verse_pattern = r'^(\d+):(\d+)$'
    lines = sample_text.split('\n')
    
    verse_starts = []
    for i, line in enumerate(lines):
        line = line.strip()
        if re.match(verse_pattern, line):
            verse_starts.append((i, line))
            print(f"절 구분자 발견: 줄 {i+1} - '{line}'")
    
    print(f"\n📊 총 {len(verse_starts)}개 절 구분자 발견")
    
    # 2. 절별로 내용 분할
    print("\n📝 절별 내용 분할:")
    for j, (line_idx, verse_num) in enumerate(verse_starts):
        # 다음 절의 시작 위치 찾기
        if j + 1 < len(verse_starts):
            next_line_idx = verse_starts[j + 1][0]
        else:
            next_line_idx = len(lines)
        
        # 절 내용 추출 (절 번호 다음 줄부터)
        verse_content_lines = lines[line_idx + 1:next_line_idx]
        verse_content = '\n'.join(verse_content_lines).strip()
        
        # 빈 줄 제거
        verse_content = re.sub(r'\n\s*\n', '\n\n', verse_content)
        
        print(f"\n[{verse_num}] ({len(verse_content)}자)")
        print(f"내용: {verse_content[:100]}{'...' if len(verse_content) > 100 else ''}")
    
    # 3. 내용 안의 성경 참조 패턴 확인
    print(f"\n🔗 내용 안의 성경 참조 패턴:")
    reference_patterns = [
        r'\([가-힣]+ \d+:\d+(?:-\d+)?\)',  # (창 7:7-9)
        r'\d+:\d+(?:-\d+)?\)',            # 19:15)
        r'\([가-힣]+ \d+:\d+(?:-\d+)?;[^)]+\)',  # (요 1:4-11;19:15)
    ]
    
    for pattern in reference_patterns:
        matches = re.findall(pattern, sample_text)
        if matches:
            print(f"패턴 '{pattern}': {matches[:5]}...")  # 처음 5개만 표시

def test_real_page():
    """실제 페이지에서 새 패턴 테스트"""
    # 실제 호크마 페이지에서 테스트할 URL이 있다면...
    print("\n🌐 실제 페이지 테스트 필요")
    print("새로운 패턴이 적용된 페이지 URL을 제공해주세요.")

if __name__ == "__main__":
    analyze_new_pattern()
    test_real_page() 