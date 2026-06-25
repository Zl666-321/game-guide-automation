"""
爬虫基类 - 所有爬虫继承此类
"""
import json
import time
import hashlib
from pathlib import Path
from datetime import datetime
from abc import ABC, abstractmethod


class BaseCrawler(ABC):
    def __init__(self, game_name: str, config: dict, data_dir: str = "data"):
        self.game_name = game_name
        self.config = config
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.session = None

    def _get_session(self):
        if self.session is None:
            import requests
            self.session = requests.Session()
            self.session.headers.update({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            })
        return self.session

    def _content_hash(self, title: str, content: str) -> str:
        raw = f"{title}{content[:200]}"
        return hashlib.md5(raw.encode("utf-8")).hexdigest()

    def _load_existing(self) -> list:
        filepath = self.data_dir / f"{self.game_name}.json"
        if filepath.exists():
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def _save_articles(self, articles: list):
        existing = self._load_existing()
        existing_hashes = {a["hash"] for a in existing}
        new_count = 0
        for article in articles:
            if article["hash"] not in existing_hashes:
                existing.append(article)
                existing_hashes.add(article["hash"])
                new_count += 1
        existing.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        max_articles = self.config.get("articles_per_game", 20)
        existing = existing[:max_articles]
        filepath = self.data_dir / f"{self.game_name}.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(existing, f, ensure_ascii=False, indent=2)
        print(f"  [{self.game_name}] 新增 {new_count} 篇，总计 {len(existing)} 篇")
        return new_count

    def _make_article(self, title: str, content: str, category: str, source: str, source_url: str = "") -> dict:
        now = datetime.now().isoformat()
        return {
            "hash": self._content_hash(title, content),
            "title": title.strip(),
            "content": content.strip(),
            "category": category,
            "game": self.game_name,
            "source": source,
            "source_url": source_url,
            "created_at": now,
            "updated_at": now,
        }

    @abstractmethod
    def crawl(self) -> list:
        pass

    def run(self) -> int:
        print(f"[\u722c\u866b] \u5f00\u59cb\u722c\u53d6 {self.game_name}...")
        try:
            articles = self.crawl()
            print(f"[\u722c\u866b] {self.game_name}: \u722c\u53d6\u5230 {len(articles)} \u7bc7\u5185\u5bb9")
            return self._save_articles(articles)
        except Exception as e:
            print(f"[\u722c\u866b] {self.game_name} \u51fa\u9519: {e}")
            return 0

    def safe_get(self, url: str, retries: int = 3, delay: float = 1.0):
        session = self._get_session()
        for i in range(retries):
            try:
                resp = session.get(url, timeout=15)
                resp.raise_for_status()
                time.sleep(delay)
                return resp
            except Exception as e:
                if i < retries - 1:
                    wait = delay * (i + 1) * 2
                    print(f"    \u91cd\u8bd5 {i+1}/{retries} ({wait:.0f}s)...")
                    time.sleep(wait)
                else:
                    raise e
        return None
