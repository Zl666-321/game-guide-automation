"""LoL Crawler"""
import re
from datetime import datetime
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError
from lxml import html as lxml_html
from . import BaseCrawler

def _fetch(url):
    try:
        req = Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        })
        with urlopen(req, timeout=15) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"  [HTTP error] {e}")
        return None

class LoLCrawler(BaseCrawler):
    def __init__(self, config: dict, data_dir: str = "data"):
        super().__init__("lol", config, data_dir)

    def crawl(self) -> list:
        articles = []
        sources = self.config.get("lol", {}).get("sources", [])
        for src in sources:
            sname = src.get("name", "")
            surl = src.get("url", "")
            stype = src.get("type", "")
            print(f"  [Crawl] {sname} ({surl})")
            if stype == "champion_stats":
                articles += self._crawl_opgg(surl, sname)
            elif stype == "guides":
                articles += self._crawl_generic(surl, sname)
        return articles

    def _crawl_opgg(self, url: str, src: str) -> list:
        articles = []
        html = _fetch(url)
        if not html:
            return articles
        try:
            tree = lxml_html.fromstring(html)
            scripts = tree.xpath("//script[contains(text(), 'championData') or contains(text(), 'winRate')]/text()")
            for script in scripts:
                matches = re.findall(r'"name":\s*"([^"]+)".*?"winRate":\s*([0-9.]+)', script)
                for champ, wr in matches[:10]:
                    content = f"""## {champ} current patch stats

**Win Rate**: {wr}%
**Source**: {src} | {datetime.now().strftime('%Y-%m-%d')}

### Notes
{champ} in current meta. Data from OP.GG real-time stats.

### Recommendation
Win rate fluctuates per patch. Cross-reference with multiple data sources for best results.
"""
                    articles.append(self._make_article(
                        title=f"""{champ} patch data ({datetime.now().strftime('%m/%d')})""",
                        content=content,
                        category="上分技巧",
                        source=src,
                    ))
        except Exception as e:
            print(f"  [OP.GG parse error] {e}")
        return articles

    def _crawl_generic(self, url: str, src: str) -> list:
        articles = []
        html = _fetch(url)
        if not html:
            return articles
        try:
            tree = lxml_html.fromstring(html)
            links = tree.xpath("//a[contains(@href, '.html') or contains(@href, '.shtml')]")
            for link in links[:15]:
                title = link.text_content().strip()
                href = link.get("href", "")
                if not title or len(title) < 5:
                    continue
                if not href.startswith("http"):
                    base = "/".join(url.split("/")[:3])
                    href = base + href
                cat = "英雄攻略"
                if any(k in title for k in ["上分", "冲分", "段位"]):
                    cat = "上分技巧"
                elif any(k in title for k in ["版本", "更新", "补丁"]):
                    cat = "版本更新"
                elif any(k in title for k in ["技巧", "教学", "攻略"]):
                    cat = "技术干货"
                content = f"""## {title}

**Source**: {src} | {datetime.now().strftime('%Y-%m-%d %H:%M')}

### Summary
Aggregated from {src}.

### Details
{title} is a trending topic among League of Legends players. This guide covers key insights and strategies to help you climb the ranked ladder.

### Key Points
- Master core mechanics to improve fundamentals
- Stay updated with patch changes
- Practice consistently and review your gameplay

### References
- [Original article]({href})
- More guides updated daily
"""
                articles.append(self._make_article(
                    title=title, content=content, category=cat, source=src, source_url=href
                ))
        except Exception as e:
            print(f"  [Parse error] {e}")
        return articles
