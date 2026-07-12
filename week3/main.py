import os
import sqlite3
import pandas as pd

def init_db():
    os.makedirs('data', exist_ok=True)
    conn = sqlite3.connect('data/spending.db')
    cursor = conn.cursor()
    
    cursor.execute("DROP TABLE IF EXISTS spendings;")

    # 과제 필수 요건: 테이블 생성 SQL 주석에 개념 설명 포함
    # [핵심 개념]
    # 테이블(Table): 데이터를 행(Row)과 열(Column)의 격자 구조로 저장하는 데이터베이스의 가장 기본적인 저장 단위.
    # 기본키(Primary Key): 각 행을 고유하게 식별할 수 있는 컬럼으로, 중복된 값과 NULL(빈 값)을 절대 허용하지 않음.
    # NOT NULL: 해당 컬럼에 값이 반드시 입력되어야 함을 보장하며, 비어 있는 상태(NULL)를 허용하지 않는 제약조건.
    cursor.execute("""
        CREATE TABLE spendings (
                  record_id TEXT,
                  date TEXT NOT NULL,
                  category TEXT NOT NULL,
                  item TEXT,
                  amount INTEGER NOT NULL,
                  payment TEXT,
                  memo TEXT,
                  year INTEGER,
                  month INTEGER,
                  day INTEGER,
                  amount_level TEXT
                  );
""")
    
    conn.commit()
    conn.close()
    print("[1/5] 테이블 생성 완료")


def save_to_db(df):
    conn = sqlite3.connect('data/spending.db')
    cursor = conn.cursor()
    
    # 스키마 유지를 위해 append 사용
    df.to_sql("spendings", conn, if_exists="append", index=False)
    
    cursor.execute("SELECT COUNT(*) FROM spendings;")
    total_rows = cursor.fetchone()[0]
    
    print(f"[2/5] 정제 데이터 저장 완료 -> {len(df)}행 저장 완료 (DB 내 행 수: {total_rows})")
    conn.close()


def load_5_rows():
    conn = sqlite3.connect('data/spending.db')
    query = "SELECT date, category, amount FROM spendings LIMIT 5;"
    df_result = pd.read_sql(query, conn)
    conn.close()
    return df_result


def whereorderby():
    conn = sqlite3.connect('data/spending.db')
    query = """
        SELECT date, category, amount, item, payment 
        FROM spendings 
        WHERE category = '식비' AND amount >= 30000 
        ORDER BY amount DESC;
    """
    df_result = pd.read_sql(query, conn)
    conn.close()
    return df_result


def summary_by_category():
    conn = sqlite3.connect('data/spending.db')
    query = """
        SELECT 
            category,
            SUM(amount) AS total_amount
        FROM spendings
        GROUP BY category;
    """
    df_result = pd.read_sql(query, conn)
    conn.close()
    return df_result


def summary_by_month():
    conn = sqlite3.connect('data/spending.db')
    query = """
        SELECT 
            year AS '년',
            month AS '월',
            COUNT(*) AS '건수',
            SUM(amount) AS '총지출액'
        FROM spendings
        GROUP BY year, month
        ORDER BY 년 ASC, 월 ASC;
    """
    df_result = pd.read_sql(query, conn)
    conn.close()
    return df_result


# ✨ 기능 6: Python vs SQL 검증 함수
def verify_data(df_clean, df_sql_cat):
    # 1. Python(pandas)으로 카테고리별 총지출 계산 후 정렬 및 인덱스 초기화
    df_py_cat = df_clean.groupby('category')['amount'].sum().reset_index()
    df_py_cat.columns = ['category', 'total_amount']
    df_py_cat = df_py_cat.sort_values(by='category').reset_index(drop=True)
    
    # 2. SQL 결과 데이터프레임도 정렬 및 인덱스 초기화하여 비교 대상 맞추기
    df_sql_sorted = df_sql_cat.sort_values(by='category').reset_index(drop=True)
    
    # 3. 두 데이터프레임의 값 일치 여부 비교 (소수점 및 데이터 타입 이슈 방지를 위해 똑같이 맞춰서 비교)
    is_equal = df_py_cat['total_amount'].equals(df_sql_sorted['total_amount'])
    
    print(f"[5/5] 집계 검증 완료 -> 전체 카테고리 일치: {is_equal}")


# ✨ 최종 main() 함수 구성
def main():
    print("====== 주차별 지출 프로젝트 데이터 파이프라인 시작 ======")
    
    # 1. 로드 (CSV 파일 읽기)
    try:
        df_clean = pd.read_csv('spending_clean.csv')
    except FileNotFoundError:
        df_clean = pd.read_csv('data/spending_clean.csv')
        
    # 2. DB 생성
    init_db()
    
    # 3. 저장
    save_to_db(df_clean)
    
    # 4. 조회 (기능 3, 기능 4, 기능 5)
    print("\n[3/5] 기본 조회 및 조건 조회 실행")
    print("--- 상위 5행 조회 결과 ---")
    print(load_5_rows())
    print("\n--- 조건 조회 (식비 >= 30000) 결과 ---")
    print(whereorderby())
    
    print("\n[4/5] GROUP BY 집계 조회 실행")
    print("--- 월별 집계 결과 ---")
    print(summary_by_month())
    
    # 5. 검증 (기능 6)
    print("\n--- 파이썬 vs SQL 교차 검증 진행 ---")
    df_sql_cat = summary_by_category() # 검증을 위한 SQL 카테고리별 데이터 로드
    verify_data(df_clean, df_sql_cat)
    
    print("======================================================")


if __name__ == "__main__":
    main()