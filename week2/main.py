import os
import sys
import pandas as pd
import numpy as np


# 데이터 불러오기
def load_data(file_path):
    if not os.path.exists(file_path):
        print(f"안내 메시지: {file_path} 파일이 없습니다.")
        sys.exit(1)

    df = pd.read_csv(file_path, encoding="utf-8-sig")

    rows, cols = df.shape
    print(f"데이터 로드 완료: {rows}행 × {cols}열")
    print()  # 깔끔하게 한 줄 띄우기

    return df


# 기능 1. 날짜 파싱 + 파생 칼럼 
def parse_dates(df):
    # date column 변환, 실패는 NaT 처리
    df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d", errors="coerce")
    
    # 변환 실패 행 출력
    natCount = df["date"].isna().sum()
    print(f"날짜 변환 실패(NoT): {natCount}건")

    # 년월일 파생 컬럼
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["day"] = df["date"].dt.day

    # 년월일 추출
    print(df[["date", "year", "month", "day"]].head())
    
    return df

# 기능 2. 카테고리 표준화
def standardize_category(df):
    original_category = df["category"].copy()
    # 허용 목록 정의하기
    allowedCategories = ["식비", "교통", "쇼핑", "의료", "문화", "기타"]

    # 스트링인지 확인
    def cleanValue(val):
        if not isinstance(val, str):
            return "기타"
        
        # 문자열이라면 앞뒤 공백 제거하기 
        cleanedValue = val.strip()

        # 허용 목록에 있는지 확인, 아니면 기타로
        if cleanedValue in allowedCategories:
            return cleanedValue
        else:
            return "기타"

    # 컬럼 전체에 함수 적용
    df["category"] = df["category"].apply(cleanValue)

    # 프린트
    changed_count = (original_category != df["category"]).sum()
    print(f"카테고리 표준화: 변경 {changed_count}건")
    print(df['category'].value_counts())
    
    return df
    


# 기능 3. 금액 구간 컬럼
def add_amount_level(df):
    def determine_level(val):
        if val < 10000:
            return "소액"
        elif val < 50000:
            return "중액" 
        else:
            return "고액"
    
    df["amount_level"] = df["amount"].apply(determine_level)
    counts = df["amount_level"].value_counts()
    
    print(f"amount_level 분포 → 소액 {counts.get('소액', 0)} | 중액 {counts.get('중액', 0)} | 고액 {counts.get('고액', 0)}")

    return df

         

# 기능 4. 결측, 이상값 처리
def clean_values(df):
    initial_rows = len(df)

    # 결측치를 빈 문자열로
    memo_missing_count = df["memo"].isna().sum()
    df["memo"] = df["memo"].fillna("")

    # 금액 0 이하 제외
    df = df[df["amount"] > 0]

    # 날짜 NaT행 제거
    df = df.dropna(subset=["date"])

    # 인덱스 다시 매기기
    df = df.reset_index(drop=True)

    # 출력용 최종 데이터 수 저장
    final_rows = len(df)
    removed_rows = initial_rows - final_rows

    # print
    print(f"memo 빈칸 대체: {memo_missing_count}건")
    print(f"이상값·날짜오류 제거: {removed_rows}행 → 최종 {final_rows}행")

    return df

# 기능 5. 간단 집계 확인
def show_summary(df):
    monthSum = df.groupby("month")["amount"].sum().reset_index()
    monthSum = monthSum.rename(columns={"amount": "total_amount"})
    monthSum["month"] = monthSum["month"].astype(int)
    monthSum = monthSum.sort_values(by="month", ascending=True)

    catSum = df.groupby("category")["amount"].sum().reset_index()
    catSum = catSum.rename(columns={"amount": "total_amount"})
    catSum = catSum.sort_values(by="total_amount", ascending=False)

    print("=== 월별 총 지출 ===")
    print(monthSum.to_string(index=False))

    return df

# 기능 6. main() 연결 + 저장
if __name__ == "__main__":
    csv_file_path = "../data/spending.csv"
    df = load_data(csv_file_path)
    
    df = parse_dates(df)
    df = standardize_category(df)
    df = add_amount_level(df)
    df = clean_values(df)          
    df = show_summary(df)
    
    
    output_path = "../data/spending_clean.csv"
    df.to_csv(output_path, index=False, encoding="utf-8-sig")
    
    print(f"정제 데이터 저장 완료: data/spending_clean.csv ({df.shape[0]}행 × {df.shape[1]}열)")