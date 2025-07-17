from advanced_hochma_parser import AdvancedHochmaParser

# 파서 생성
parser = AdvancedHochmaParser()

# 창세기 31장 파싱
print("수정된 파서로 창세기 31장 파싱 중...")
result = parser.parse_single_article('139477')

print(f"주석명: {result['commentary_name']}")
print(f"성경책: {result['book_name']} {result['chapter']}장")
print(f"절별 주석 수: {len(result['verse_commentaries'])}개")

print("\n첫 5개 절:")
for i, v in enumerate(result['verse_commentaries'][:5]):
    print(f"  {v['chapter']}:{v['verse']} - {v['commentary'][:80]}...")

print("\n마지막 5개 절:")
for i, v in enumerate(result['verse_commentaries'][-5:]):
    print(f"  {v['chapter']}:{v['verse']} - {v['commentary'][:80]}...")

print(f"\n총 {len(result['verse_commentaries'])}개 절이 파싱되었습니다!") 