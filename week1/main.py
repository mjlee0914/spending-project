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


# 데이터 구조 확인하기
def explore_structure(df):
    print("===== 1. 전체 행 수와 열 수 =====")
    rows, cols = df.shape
    print(f"전체 행 수: {rows}, 전체 열 수: {cols}")
    print()

    print("===== 2. 컬럼 이름 및 자료형 =====")
    for col_name, col_type in df.dtypes.items():
        print(f"컬럼명: {col_name}, 자료형: {col_type}")
    print()

    print("===== 3. 상위 5개 행 =====")
    print(df.head(5))
    print()

# 분포 확인
def show_distribution(df):
    total_count = len(df)

    category_counts = df["category"].value_counts()
    for category, count in category_counts.items():
        ratio = (count / total_count) * 100
        print(f"카테고리: {category}, 건수: {count}건 ({ratio:.1f}%)")
    print()


    payment_counts = df["payment"].value_counts()
    for method, count in payment_counts.items():
        ratio = (count / total_count ) * 100
        print(f"결제 수단: {method}, 건수: {count}건 ({ratio: .1f}%)")
    print()


    cat_means = {}
    for cat in df["category"].unique():
        cat_df = df[df["category"] == cat]
        mean_amount = cat_df["amount"].mean()
        cat_means[cat] = mean_amount
        print(f"카테고리: {cat} | 평균 금액: {mean_amount:.0f}원")
    print()

    return cat_means


 # 결측치 현황 파악 
def check_missing(df):
    total_count = len(df)
    missing_info = {}
    clean_columns = []

    #컬럼별 결측치 수와 비율 계산
    for col in df.columns:
        missing_count = df[col].isnull().sum()

        if missing_count > 0:
            ratio = (missing_count / total_count ) * 100

            if ratio < 5:
                severity = "낮음"
            elif ratio < 20:
                severity = "주의"
            else:
                severity = "높음"

            print(f"컬럼: {col}, 결측치: {missing_count}건 ({ratio:.1f}%), 심각도: {severity}")
            missing_info[col] = {"count": missing_count, "ratio": ratio, "severity": severity}

        else:
            clean_columns.append(col) 
    print()
    print(", ".join(clean_columns)) # 예쁘게 쉼표로 연결해서 출력하기

    print()

    return missing_info


# 반복문과 딕셔너리를 사용한 카테고리별 평균 금액 계산 및 출력
def numpy_amount_stats(df):
    amounts = np.array(df["amount"].dropna())

    np_mean = np.mean(amounts)
    np_std = np.std(amounts, ddof=1)
    np_median = np.median(amounts)
    np_min = np.min(amounts)
    np_max = np.max(amounts)

    print(f"평균: {np_mean:.1f}원")
    print(f"표준편차: {np_std:.1f}원")
    print(f"중앙값: {np_median:.1f}원")
    print(f"최솟값: {np_min}원")
    print(f"최댓값: {np_max}원")
    print()

    print("5만 원 초과 지출 건: ")
    over_50k = amounts[amounts > 50000]
    print(f"5만 원 초과 지출 목록: {over_50k}")
    print(f"총 건수: {len(over_50k)}건")
    print()

    print("5-3. pandas vs NumPy 결과 비교: ")
    pd_desc = df["amount"].describe()
    print(f"평균 일치 여부: {pd_desc['mean'] == np_mean} (✓)")
    print(f"표준편차 일치 여부: {pd_desc['std'] == np_std} (✓)")
    print(f"중앙값 일치 여부: {pd_desc['50%'] == np_median} (✓)")
    print(f"최솟값 일치 여부: {pd_desc['min'] == np_min} (✓)")
    print(f"최댓값 일치 여부: {pd_desc['max'] == np_max} (✓)")
    print()


# 결과 딕셔너리 반환
if __name__ == "__main__":
    df = load_data("data/spending.csv")

    explore_structure(df)
    show_distribution(df)
    check_missing(df)
    numpy_amount_stats(df)
    