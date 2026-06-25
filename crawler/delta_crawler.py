"""Delta Force Crawler"""
import re
from datetime import datetime
from urllib.request import urlopen, Request
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

class DeltaForceCrawler(BaseCrawler):
    def __init__(self, config: dict, data_dir: str = "data"):
        super().__init__("delta_force", config, data_dir)

    def crawl(self) -> list:
        articles = []
        print("  [Crawl] NGA ...")
        articles += self._crawl_nga()
        print("  [Crawl] Tieba ...")
        articles += self._crawl_tieba()
        return articles

    def _classify(self, title: str) -> str:
        if any(k in title for k in ["冷门", "另类", "奇葩", "小众"]):
            return "冷门玩法"
        elif any(k in title for k in ["枪", "武器", "配装", "伤害"]):
            return "枪械策略"
        elif any(k in title for k in ["地图", "点位", "蹲点", "打法"]):
            return "地图技巧"
        elif any(k in title for k in ["装备", "护甲", "背包", "配件"]):
            return "装备搭配"
        return "冷门玩法"

    def _make_content(self, title: str, src: str, url: str, cat: str) -> str:
        descs = {
            "冷门玩法": "Beyond mainstream strategies, there are niche playstyles worth exploring.",
            "枪械策略": "Master weapon stats and attachments to maximize combat efficiency.",
            "地图技巧": "Map knowledge is key to victory. Learn positions and rotation paths.",
            "装备搭配": "Optimize your loadout for different tactical scenarios.",
        }
        desc = descs.get(cat, "Learn these tips to gain an edge in Delta Force.")
        tips = {
            "冷门玩法": "### Niche Strategy Tips\n- Try unconventional weapon combos\n- Use off-angle positions\n- Break the meta",
            "枪械策略": "### Weapon Tips\n- Choose weapons for engagement distance\n- Master recoil control\n- Tune attachments per map",
            "地图技巧": "### Map Tips\n- Learn key positions on each map\n- Master rotation routes\n- Use cover effectively",
            "装备搭配": "### Loadout Tips\n- Balance offense and defense\n- Adapt to squad role\n- Test new gear in practice",
        }
        return f"""## {title}

**Category**: {cat} | **Source**: {src} | **Date**: {datetime.now().strftime('%Y-%m-%d')}

### Summary
> {desc}

### Content
Aggregated from {src} discussion: "{title}"

{tips.get(cat, tips["冷门玩法"])}

### References
- [Original post]({url})
- More Delta Force guides updated daily
"""

    def _crawl_nga(self) -> list:
        articles = []
        keywords = ["Delta Force", "三角洲", "冷门玩法"]
        for kw in keywords:
            html = _fetch(f"https://bbs.nga.cn/nuke.php?func=search&keyword={kw}&fid=-1")
            if not html:
                continue
            try:
                tree = lxml_html.fromstring(html)
                posts = tree.xpath("//a[contains(@href, 'read.php')]")
                for post in posts[:8]:
                    title = post.text_content().strip()
                    href = post.get("href", "")
                    if not title or len(title) < 4:
                        continue
                    if not href.startswith("http"):
                        href = "https://bbs.nga.cn/" + href
                    cat = self._classify(title)
                    content = self._make_content(title, "NGA", href, cat)
                    articles.append(self._make_article(title=title, content=content, category=cat, source="NGA", source_url=href))
            except:
                pass
        return articles

    def _crawl_tieba(self) -> list:
        articles = []
        html = _fetch("https://tieba.baidu.com/f?kw=三角洲行动&ie=utf-8")
        if not html:
            return articles
        try:
            tree = lxml_html.fromstring(html)
            threads = tree.xpath("//a[contains(@class, 'j_th_tit')]")
            for thread in threads[:10]:
                title = thread.text_content().strip()
                href = thread.get("href", "")
                if not title or len(title) < 4:
                    continue
                if not href.startswith("http"):
                    href = "https://tieba.baidu.com" + href
                cat = self._classify(title)
                content = self._make_content(title, "百度贴吧", href, cat)
                articles.append(self._make_article(title=title, content=content, category=cat, source="百度贴吧", source_url=href))
        except:
            pass
        return articles
