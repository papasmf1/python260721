import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

SEARCH_URL = (
    "https://search.naver.com/search.naver?where=nexearch&sm=top_hty&fbm=0"
    "&ie=utf8&query=%EB%B0%98%EB%8F%84%EC%B2%B4&ackey=v6xj2xil"
)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/126.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
}


def get_soup(url, timeout=10):
    res = requests.get(url, headers=HEADERS, timeout=timeout)
    res.raise_for_status()
    if not res.encoding or res.encoding.lower() == "iso-8859-1":
        res.encoding = res.apparent_encoding
    return BeautifulSoup(res.text, "html.parser")


def extract_news_links_from_naver_search(search_url, limit=10):
    soup = get_soup(search_url)

    links = []
    seen = set()

    news_list = soup.select_one("div.fds-news-item-list-desk")
    if news_list:
        # The current Naver news layout repeats item blocks as direct children.
        for child in news_list.find_all(recursive=False):
            if child.name != "div":
                continue

            title_anchor = child.select_one("a[data-heatmap-target='.tit']")
            if not title_anchor:
                continue

            href = title_anchor.get("href", "").strip()
            if not href:
                continue
            href = urljoin(search_url, href)

            title = title_anchor.get_text(" ", strip=True) or "Untitled"
            summary_anchor = child.select_one("a[data-heatmap-target='.body']")
            nav_anchor = child.select_one("a[data-heatmap-target='.nav']")
            press_anchor = child.select_one("a[data-heatmap-target='.prof']")

            summary = ""
            if summary_anchor:
                summary = summary_anchor.get_text(" ", strip=True)

            press = ""
            if press_anchor:
                press = press_anchor.get_text(" ", strip=True)

            naver_news_url = ""
            if nav_anchor:
                naver_news_url = nav_anchor.get("href", "").strip()

            key = (title, href)
            if key in seen:
                continue
            seen.add(key)

            links.append({
                "title": title,
                "url": href,
                "summary": summary,
                "press": press,
                "naver_news_url": naver_news_url,
            })

            if len(links) >= limit:
                break

    if not links:
        candidates = soup.select("a.news_tit")
        if not candidates:
            candidates = soup.select("a[href*='news.naver.com'], a[href*='n.news.naver.com']")

        for a_tag in candidates:
            href = a_tag.get("href", "").strip()
            if not href:
                continue

            href = urljoin(search_url, href)

            title = a_tag.get("title") or a_tag.get_text(" ", strip=True)
            if not title:
                title = "Untitled"

            key = (title, href)
            if key in seen:
                continue
            seen.add(key)

            links.append({"title": title, "url": href})
            if len(links) >= limit:
                break

    return links


def extract_article_text(article_url):
    try:
        soup = get_soup(article_url)

        content_selectors = [
            "#dic_area",
            "#newsct_article",
            "#articleBodyContents",
            "#articeBody",
            ".go_trans._article_content",
            ".article_view",
            ".article_body",
            ".news_body",
            "#contents",
        ]

        article_text = ""
        for selector in content_selectors:
            node = soup.select_one(selector)
            if node:
                for tag in node.select("script, style"):
                    tag.decompose()
                article_text = node.get_text("\n", strip=True)
                if article_text:
                    break

        if not article_text:
            meta_desc = soup.select_one("meta[property='og:description']")
            if meta_desc and meta_desc.get("content"):
                article_text = meta_desc.get("content").strip()

        return article_text

    except Exception as exc:
        return f"[FAILED] {exc}"


def crawl_news_articles(search_url, limit=5, delay=0.7):
    news_links = extract_news_links_from_naver_search(search_url, limit=limit)

    results = []
    for idx, item in enumerate(news_links, 1):
        title = item["title"]
        url = item["url"]

        print(f"[{idx}/{len(news_links)}] Crawling: {title}")
        body = extract_article_text(url)

        results.append({
            "title": title,
            "url": url,
            "content": body,
        })

        time.sleep(delay)

    return results


if __name__ == "__main__":
    data = crawl_news_articles(SEARCH_URL, limit=5, delay=0.7)

    print("\n===== RESULT =====")
    for idx, row in enumerate(data, 1):
        preview = (row["content"] or "").replace("\n", " ")
        print(f"\n[{idx}] TITLE: {row['title']}")
        if row.get("press"):
            print(f"PRESS: {row['press']}")
        print(f"URL: {row['url']}")
        if row.get("naver_news_url"):
            print(f"NAVER NEWS URL: {row['naver_news_url']}")
        if row.get("summary"):
            print(f"SUMMARY: {row['summary'][:120]}...")
        print(f"CONTENT PREVIEW: {preview[:200]}...")
