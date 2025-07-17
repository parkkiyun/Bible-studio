import pandas as pd
import os

def preview_excel(excel_file):
    """엑셀 파일 미리보기"""
    if not os.path.exists(excel_file):
        print(f"파일을 찾을 수 없습니다: {excel_file}")
        return
    
    print(f"📊 엑셀 파일 미리보기: {excel_file}")
    print("=" * 80)
    
    # 주석데이터 시트 읽기
    df = pd.read_excel(excel_file, sheet_name='주석데이터')
    
    print(f"📈 전체 데이터: {len(df)}개 절")
    print(f"📖 컬럼: {list(df.columns)}")
    
    print("\n🔍 처음 3개 절:")
    for i in range(min(3, len(df))):
        row = df.iloc[i]
        print(f"\n  [{i+1}] {row['성경책']} {row['장']}:{row['절']} ({row['내용_길이']}자)")
        print(f"       주석: {row['주석_내용'][:100]}{'...' if len(row['주석_내용']) > 100 else ''}")
    
    print(f"\n📊 통계:")
    print(f"  - 평균 내용 길이: {df['내용_길이'].mean():.1f}자")
    print(f"  - 최소 내용 길이: {df['내용_길이'].min()}자")
    print(f"  - 최대 내용 길이: {df['내용_길이'].max()}자")
    print(f"  - 절 범위: {df['절'].min()}절 ~ {df['절'].max()}절")
    
    # 요약정보 시트 읽기
    try:
        summary_df = pd.read_excel(excel_file, sheet_name='요약정보')
        print(f"\n📋 요약정보:")
        for _, row in summary_df.iterrows():
            print(f"  - {row['항목']}: {row['값']}")
    except:
        print("\n⚠️ 요약정보 시트를 읽을 수 없습니다.")

if __name__ == "__main__":
    # 가장 최근 엑셀 파일 찾기
    excel_files = [f for f in os.listdir('.') if f.endswith('.xlsx') and f.startswith('hochma_')]
    if excel_files:
        latest_file = max(excel_files, key=os.path.getctime)
        preview_excel(latest_file)
    else:
        print("엑셀 파일을 찾을 수 없습니다.") 