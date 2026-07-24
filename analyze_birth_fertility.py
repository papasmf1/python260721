import re
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


FILE_PATH = Path("c:/work/출생아수__합계출산율__자연증가_등_20260724153629.xlsx")
OUT_LONG = Path("c:/work/clean_birth_fertility_long.csv")
OUT_WIDE = Path("c:/work/clean_birth_fertility_wide.csv")
OUT_SUMMARY = Path("c:/work/birth_fertility_analysis_summary.txt")
OUT_PLOT = Path("c:/work/births_by_year_line.png")


INDICATOR_MAP = {
    "출생아수(명)": "births",
    "합계출산율(명)": "tfr",
    "자연증가건수(명)": "natural_increase_count",
    "조출생률(천명당)": "crude_birth_rate_per_1000",
    "자연증가율(천명당)": "natural_increase_rate_per_1000",
    "출생성비(명)": "sex_ratio_at_birth",
}


def extract_year(col_name: object) -> int | None:
    text = str(col_name)
    match = re.search(r"(19\d{2}|20\d{2})", text)
    if not match:
        return None
    return int(match.group(1))


def build_clean_dataframe() -> tuple[pd.DataFrame, pd.DataFrame]:
    raw = pd.read_excel(FILE_PATH, sheet_name="데이터")

    # 첫 컬럼은 지표명으로 사용
    first_col = raw.columns[0]
    raw = raw.rename(columns={first_col: "indicator"})

    # 연도형 컬럼만 선별하고 표준 연도명으로 재매핑
    year_cols = {}
    for col in raw.columns[1:]:
        year = extract_year(col)
        if year is not None:
            year_cols[col] = year

    df = raw[["indicator", *year_cols.keys()]].copy()
    df = df.rename(columns=year_cols)

    # long 형태로 변환
    long_df = df.melt(id_vars="indicator", var_name="year", value_name="value")
    long_df["indicator"] = long_df["indicator"].astype(str).str.strip()
    long_df["year"] = pd.to_numeric(long_df["year"], errors="coerce").astype("Int64")
    long_df["value"] = pd.to_numeric(long_df["value"], errors="coerce")

    # 결측/비정상 행 제거
    long_df = long_df.dropna(subset=["indicator", "year", "value"])
    long_df = long_df[long_df["year"].between(1900, 2100)]

    # 분석용 영문 코드 생성
    long_df["indicator_code"] = long_df["indicator"].map(INDICATOR_MAP)

    # wide 형태(연도별 지표 컬럼)
    wide_df = (
        long_df.dropna(subset=["indicator_code"])
        .pivot(index="year", columns="indicator_code", values="value")
        .sort_index()
    )
    wide_df.index = wide_df.index.astype(int)

    return long_df.sort_values(["indicator", "year"]), wide_df


def make_summary(wide_df: pd.DataFrame) -> str:
    births = wide_df["births"].dropna()
    tfr = wide_df["tfr"].dropna()

    start_year = int(births.index.min())
    end_year = int(births.index.max())
    start_val = float(births.loc[start_year])
    end_val = float(births.loc[end_year])

    change_abs = end_val - start_val
    change_pct = (change_abs / start_val) * 100

    years = end_year - start_year
    cagr = ((end_val / start_val) ** (1 / years) - 1) * 100 if years > 0 else 0.0

    max_birth_year = int(births.idxmax())
    min_birth_year = int(births.idxmin())

    below_1_mask = tfr < 1.0
    below_1_years = tfr[below_1_mask].index.tolist()

    corr = births.corr(tfr, method="pearson")

    decade_df = births.to_frame("births").copy()
    decade_df["decade"] = (decade_df.index // 10) * 10
    decade_stats = decade_df.groupby("decade")["births"].agg(["mean", "max", "min"])

    yoy = births.diff()
    top_drop = yoy.nsmallest(5)
    top_rise = yoy.nlargest(5)

    lines = []
    lines.append("[데이터 개요]")
    lines.append(f"- 분석 기간: {start_year}~{end_year}년")
    lines.append(f"- 출생아 수 시작값: {start_val:,.0f}명")
    lines.append(f"- 출생아 수 마지막값: {end_val:,.0f}명")
    lines.append(f"- 총 변화량: {change_abs:,.0f}명 ({change_pct:.2f}%)")
    lines.append(f"- 연평균 증감률(CAGR): {cagr:.2f}%")
    lines.append("")

    lines.append("[극값]")
    lines.append(f"- 출생아 수 최대: {max_birth_year}년 ({births.loc[max_birth_year]:,.0f}명)")
    lines.append(f"- 출생아 수 최소: {min_birth_year}년 ({births.loc[min_birth_year]:,.0f}명)")
    lines.append("")

    lines.append("[합계출산율(TFR)]")
    lines.append(f"- TFR 1.0 미만 첫 해: {below_1_years[0] if below_1_years else '없음'}")
    lines.append(f"- TFR 1.0 미만 연도 수: {len(below_1_years)}")
    if below_1_years:
        lines.append("- TFR 1.0 미만 연도: " + ", ".join(map(str, below_1_years)))
    lines.append("")

    lines.append("[상관관계]")
    lines.append(f"- 출생아 수 vs 합계출산율 피어슨 상관계수: {corr:.4f}")
    lines.append("")

    lines.append("[10년 단위 출생아 수 통계]")
    for decade, row in decade_stats.iterrows():
        lines.append(
            f"- {decade}s: 평균 {row['mean']:,.0f}명, 최대 {row['max']:,.0f}명, 최소 {row['min']:,.0f}명"
        )
    lines.append("")

    lines.append("[전년 대비 출생아 수 급변 Top 5]")
    lines.append("- 감소 폭 Top 5")
    for y, v in top_drop.items():
        lines.append(f"  {int(y)}년: {v:,.0f}명")
    lines.append("- 증가 폭 Top 5")
    for y, v in top_rise.items():
        lines.append(f"  {int(y)}년: {v:,.0f}명")

    return "\n".join(lines)


def plot_births(wide_df: pd.DataFrame) -> None:
    births = wide_df["births"].dropna()

    # 윈도우 한글 폰트 설정(없으면 기본 폰트 사용)
    try:
        plt.rcParams["font.family"] = "Malgun Gothic"
    except Exception:
        pass
    plt.rcParams["axes.unicode_minus"] = False

    plt.figure(figsize=(12, 6))
    plt.plot(births.index, births.values, marker="o", linewidth=2)
    plt.title("대한민국 연도별 출생아 수 추이")
    plt.xlabel("연도")
    plt.ylabel("출생아 수(명)")
    plt.grid(True, linestyle="--", alpha=0.4)
    plt.tight_layout()
    plt.savefig(OUT_PLOT, dpi=150)
    plt.close()


def main() -> None:
    long_df, wide_df = build_clean_dataframe()

    long_df.to_csv(OUT_LONG, index=False, encoding="utf-8-sig")
    wide_df.to_csv(OUT_WIDE, encoding="utf-8-sig")

    summary = make_summary(wide_df)
    OUT_SUMMARY.write_text(summary, encoding="utf-8")

    plot_births(wide_df)

    print("클렌징/분석/시각화 완료")
    print(f"- 정제 long 데이터: {OUT_LONG}")
    print(f"- 정제 wide 데이터: {OUT_WIDE}")
    print(f"- 분석 요약: {OUT_SUMMARY}")
    print(f"- 라인그래프: {OUT_PLOT}")
    print("\n[요약 미리보기]")
    print(summary)


if __name__ == "__main__":
    main()
