"""
네이버 블로그(절세매니아) 최신 글 10개를 홈페이지에 반영한다.

  python update_blog.py

- RSS에서 최신 글을 읽어 site/assets/blog/ 에 썸네일을 저장하고
- site/assets/posts.js 를 새로 만든다 (index.html이 이 파일을 읽어 슬라이드를 그림).
"""
import json
import re
import urllib.request
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from pathlib import Path

BLOG_ID = "leetax_"
COUNT = 10
ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "site" / "assets" / "blog"
OUT_JS = ROOT / "site" / "assets" / "posts.js"
UA = {"User-Agent": "Mozilla/5.0 (TheonHomepage blog sync)"}


def get(url: str) -> bytes:
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
        return r.read()


def main() -> None:
    root = ET.fromstring(get(f"https://rss.blog.naver.com/{BLOG_ID}.xml"))
    items = root.findall("./channel/item")[:COUNT]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for old in OUT_DIR.glob("*.png"):
        old.unlink()

    posts = []
    for i, it in enumerate(items, 1):
        link = it.findtext("link", "").split("?")[0]
        desc = it.findtext("description", "")
        m = re.search(r'<img[^>]+src="([^"]+)"', desc)
        thumb = ""
        if m:
            name = f"post-{i:02d}.png"
            (OUT_DIR / name).write_bytes(get(m.group(1)))
            thumb = f"assets/blog/{name}"
        posts.append({
            "title": it.findtext("title", "").strip(),
            "link": link,
            "category": it.findtext("category", "").strip(),
            "date": parsedate_to_datetime(it.findtext("pubDate")).strftime("%Y.%m.%d"),
            "thumb": thumb,
        })

    OUT_JS.write_text(
        "// update_blog.py 가 자동으로 만든 파일입니다. 직접 수정하지 마세요.\n"
        f"window.BLOG_POSTS = {json.dumps(posts, ensure_ascii=False, indent=2)};\n",
        encoding="utf-8",
    )
    print(f"블로그 글 {len(posts)}개 반영 완료")
    for p in posts:
        print(f"  {p['date']}  {p['title']}")


if __name__ == "__main__":
    main()
