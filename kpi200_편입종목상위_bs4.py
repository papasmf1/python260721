import requests
from bs4 import BeautifulSoup
from openpyxl import Workbook

URL = "https://finance.naver.com/sise/sise_index.naver?code=KPI200"
ENTRY_URL_TEMPLATE = "https://finance.naver.com/sise/entryJongmok.naver?type=KPI200&page={page}"
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://finance.naver.com/",
}


def _find_entry_box(soup):
    """주어진 HTML에서 '편입종목상위' 박스(div.box_type_m)를 찾는다."""
    for box in soup.select("div.box_type_m"):
        title = box.select_one("h4.top_tlt")
        if not title:
            continue
        title_text = title.get_text(" ", strip=True).replace(" ", "")
        if "편입종목" in title_text and "상위" in title_text:
            return box

    # 한글 인코딩/문구 변화에 대비: entryJongmok 링크가 있는 표를 기준으로 fallback
    for table in soup.select("table.type_1"):
        if table.select_one("a[href*='entryJongmok']"):
            return table.find_parent("div", class_="box_type_m")

    return None


def _fetch_soup(url):
    res = requests.get(url, headers=HEADERS, timeout=10)
    res.raise_for_status()

    # 일부 응답에서 charset이 부정확하게 잡혀 한글 매칭이 깨질 수 있어 보정한다.
    enc = (res.encoding or "").lower()
    if not enc or enc == "iso-8859-1":
        res.encoding = "euc-kr"
    else:
        res.encoding = res.apparent_encoding

    return BeautifulSoup(res.text, "html.parser")


def _parse_rows_from_entry_box(entry_box, page=None):
    """편입종목상위 박스에서 종목 행만 파싱한다."""
    table = entry_box.select_one("table.type_1")
    if table is None:
        raise ValueError("편입종목상위 테이블을 찾지 못했습니다.")

    result = []
    # 주신 구조 기준: 종목 데이터 행은 td.ctg를 포함
    for tr in table.select("tr"):
        name_td = tr.select_one("td.ctg")
        if name_td is None:
            continue

        tds = tr.find_all("td")
        if len(tds) < 7:
            continue

        name = name_td.get_text(strip=True)
        diff_dir = ""
        blind = tds[2].select_one("span.blind")
        if blind:
            diff_dir = blind.get_text(strip=True)

        diff_value = tds[2].get_text(" ", strip=True)
        diff = f"{diff_dir} {diff_value}".strip() if diff_dir else diff_value

        link = name_td.select_one("a")
        item_link = ""
        if link and link.get("href"):
            item_link = requests.compat.urljoin("https://finance.naver.com", link["href"])

        item = {
            "종목명": name,
            "종목링크": item_link,
            "현재가": tds[1].get_text(" ", strip=True),
            "전일비": diff,
            "등락률": tds[3].get_text(" ", strip=True),
            "거래량": tds[4].get_text(" ", strip=True),
            "거래대금(백만)": tds[5].get_text(" ", strip=True),
            "시가총액(억)": tds[6].get_text(" ", strip=True),
        }
        if page is not None:
            item["페이지"] = page
        result.append(item)

    return result


def crawl_top_included_items(page=1):
    """특정 페이지의 편입종목상위 데이터를 크롤링한다."""
    soup = _fetch_soup(ENTRY_URL_TEMPLATE.format(page=page))

    entry_box = _find_entry_box(soup)
    if entry_box is None:
        raise ValueError("편입종목상위 박스를 찾지 못했습니다.")

    return _parse_rows_from_entry_box(entry_box, page=page)


def crawl_all_pages(total_pages=20):
    """편입종목상위 1~total_pages 페이지를 모두 크롤링한다."""
    all_items = []
    for page in range(1, total_pages + 1):
        page_items = crawl_top_included_items(page=page)
        all_items.extend(page_items)
    return all_items


def save_to_excel(data, file_name="kospi200.xlsx"):
    """크롤링 결과를 엑셀 파일로 저장한다."""
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "KOSPI200_편입종목상위"

    headers = [
        "페이지",
        "종목명",
        "현재가",
        "전일비",
        "등락률",
        "거래량",
        "거래대금(백만)",
        "시가총액(억)",
        "종목링크",
    ]
    sheet.append(headers)

    for row in data:
        sheet.append(
            [
                row.get("페이지", ""),
                row.get("종목명", ""),
                row.get("현재가", ""),
                row.get("전일비", ""),
                row.get("등락률", ""),
                row.get("거래량", ""),
                row.get("거래대금(백만)", ""),
                row.get("시가총액(억)", ""),
                row.get("종목링크", ""),
            ]
        )

    workbook.save(file_name)


def crawl_page_nav():
    """편입종목상위 박스 하단 페이지 네비게이션을 파싱한다."""
    soup = _fetch_soup(ENTRY_URL_TEMPLATE.format(page=1))
    entry_box = _find_entry_box(soup)
    if entry_box is None:
        return []

    nav = entry_box.select_one("table.Nnavi")
    if nav is None:
        return []

    pages = []
    for a in nav.select("a"):
        text = a.get_text(" ", strip=True)
        href = a.get("href", "")
        if not href:
            continue
        pages.append(
            {
                "텍스트": text,
                "링크": requests.compat.urljoin("https://finance.naver.com", href),
            }
        )
    return pages


if __name__ == "__main__":
    data = crawl_all_pages(total_pages=20)
    save_to_excel(data, file_name="kospi200.xlsx")

    print(f"총 {len(data)}개 종목 (20페이지 합계)")
    print("엑셀 저장 완료: kospi200.xlsx")
    for i, row in enumerate(data, 1):
        print(
            f"{i:03d}. [p{row['페이지']:02d}] {row['종목명']} | 현재가: {row['현재가']} | 전일비: {row['전일비']} "
            f"| 등락률: {row['등락률']} | 거래량: {row['거래량']} "
            f"| 거래대금(백만): {row['거래대금(백만)']} | 시가총액(억): {row['시가총액(억)']}"
            f" | 링크: {row['종목링크']}"
        )

    nav_data = crawl_page_nav()
    print("\n페이지 네비게이션:")
    for p in nav_data:
        print(f"- {p['텍스트']}: {p['링크']}")
