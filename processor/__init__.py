"""
内容处理器 - 清洗、去重、排序文章
"""
import json
from pathlib import Path


class ContentProcessor:
    def __init__(self, data_dir: str = "data", min_length: int = 100):
        self.data_dir = Path(data_dir)
        self.min_length = min_length

    def process_game(self, game_name: str) -> list:
        filepath = self.data_dir / f"{game_name}.json"
        if not filepath.exists():
            return []
        with open(filepath, "r", encoding="utf-8") as f:
            articles = json.load(f)
        before = len(articles)
        articles = [a for a in articles if len(a.get("content", "")) >= self.min_length]
        after = len(articles)
        if before != after:
            print(f"  [\u8fc7\u6ee4] \u79fb\u9664 {before-after} \u7bc7\u8fc7\u77ed\u5185\u5bb9")
        articles.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return articles

    def get_all_articles(self, games: list = None) -> dict:
        if games is None:
            games = ["lol", "delta_force"]
        result = {}
        for game in games:
            articles = self.process_game(game)
            if articles:
                result[game] = articles
        return result

    def get_categories(self, game_name: str) -> dict:
        articles = self.process_game(game_name)
        categories = {}
        for article in articles:
            cat = article.get("category", "其他")
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(article)
        return categories

    def get_stats(self, game_name: str) -> dict:
        articles = self.process_game(game_name)
        categories = self.get_categories(game_name)
        return {
            "total": len(articles),
            "categories": {k: len(v) for k, v in categories.items()},
            "latest": articles[0]["created_at"][:10] if articles else "暂无",
        }
