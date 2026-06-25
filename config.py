# game-guide-automation config
CRAWLER_CONFIG = {
    "lol": {
        "enabled": True,
        "sources": [
            {"name": "opgg_champions", "url": "https://www.op.gg/champions", "type": "champion_stats", "interval_hours": 24},
            {"name": "17173_lol", "url": "https://lol.17173.com/j/", "type": "guides", "interval_hours": 12},
        ],
        "categories": ["上分技巧", "英雄攻略", "版本更新", "技术干货"],
    },
    "delta_force": {
        "enabled": True,
        "sources": [
            {"name": "delta_nga", "url": "https://bbs.nga.cn/thread.php?fid=-1", "type": "forum", "interval_hours": 12},
        ],
        "categories": ["冷门玩法", "枪械策略", "地图技巧", "装备搭配"],
    },
}
OUTPUT_CONFIG = {"articles_per_game": 20, "min_content_length": 100, "language": "zh-CN"}
SITE_CONFIG = {
    "site_name": "游戏攻略站",
    "site_description": "英雄联盟上分技巧 & 三角洲行动冷门玩法 - 每日更新",
    "site_url": "https://你的用户名.github.io/game-guide-automation",
    "author": "GameGuideBot",
    "articles_per_page": 10,
    "theme": "dark",
}
DATA_DIR = "data"
OUTPUT_DIR = "docs"
