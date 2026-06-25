"""Main entry point - run crawl, build, and deploy"""
import sys, os, json
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import CRAWLER_CONFIG, OUTPUT_CONFIG, SITE_CONFIG, DATA_DIR, OUTPUT_DIR
from crawler.lol_crawler import LoLCrawler
from crawler.delta_crawler import DeltaForceCrawler
from builder.generator import SiteGenerator


def run_crawl():
    print("=" * 50)
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] Starting crawl...")
    print("=" * 50)
    total = 0
    if CRAWLER_CONFIG.get("lol", {}).get("enabled", True):
        print("\nLoL...")
        total += LoLCrawler(CRAWLER_CONFIG, DATA_DIR).run()
    if CRAWLER_CONFIG.get("delta_force", {}).get("enabled", True):
        print("\nDelta Force...")
        total += DeltaForceCrawler(CRAWLER_CONFIG, DATA_DIR).run()
    print(f"\nDone! {total} new articles")
    return total


def run_build():
    print("=" * 50)
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] Building site...")
    print("=" * 50)
    gen = SiteGenerator({"SITE_CONFIG": SITE_CONFIG, "OUTPUT_CONFIG": OUTPUT_CONFIG}, DATA_DIR, OUTPUT_DIR)
    gen.generate_html()
    # Generate deploy manifest
    from processor import ContentProcessor
    proc = ContentProcessor(data_dir=DATA_DIR)
    all_arts = proc.get_all_articles()
    info = {"last_updated": datetime.now().isoformat(), "last_build": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "articles": {g: len(a) for g, a in all_arts.items()},
            "total": sum(len(a) for a in all_arts.values())}
    with open(os.path.join(OUTPUT_DIR, "deploy.json"), "w", encoding="utf-8") as f:
        json.dump(info, f, ensure_ascii=False, indent=2)
    return info


def init_sample():
    print("Initializing sample data...")
    now = datetime.now().isoformat()
    samples = {
        "lol": [
            {"hash": "lol_001", "title": "Top 5 Champions for Climbing Solo Queue This Patch",
             "content": "## Top 5 Solo Queue Champions\n\nBased on high-ELO win rates and pick rates, these 5 champions will help you climb.\n\n### 1. K'Sante (Top)\n- Win Rate: 51.8%\n- Strong laning phase\n- Great teamfight presence\n\n### 2. Lee Sin (Jungle)\n- Win Rate: 50.5%\n- High skill ceiling\n- Game-changing plays\n\n### Tips\n- Master 2-3 champions max\n- Focus on macro play\n- Watch patch notes",
             "category": "rank", "game": "lol", "source": "OP.GG",
             "source_url": "https://op.gg", "created_at": now, "updated_at": now},
            {"hash": "lol_002", "title": "Mid Lane Wave Management Guide",
             "content": "## Wave Management for Mid Lane\n\nLearn how to control minion waves to gain advantages.\n\n### Slow Push\n- Last hit only\n- Builds up a large wave\n- Dive opponent under turret\n\n### Fast Push\n- Clear wave quickly\n- Freeze near your turret\n- Deny enemy CS\n\n### Freeze\n- Keep wave just outside turret\n- Safe farming\n- Easy gank setup",
             "category": "tech", "game": "lol", "source": "NGA",
             "source_url": "https://bbs.nga.cn", "created_at": now, "updated_at": now},
            {"hash": "lol_003", "title": "Patch 13.x Jungle Changes Analysis",
             "content": "## Patch 13.x Jungle Changes\n\n### Key Changes\n1. Camp respawn increased by 15s\n2. Jungle pet damage adjusted\n3. New epic monster mechanics\n\n### Impact\n- Farming junglers buffed slightly\n- Gank timing more important\n- Objective control is key\n\n### Recommended Junglers\n- Udyr (farm heavy)\n- Xin Zhao (early ganks)\n- Lee Sin (balanced)",
             "category": "patch", "game": "lol", "source": "Riot Games",
             "source_url": "https://lol.qq.com", "created_at": now, "updated_at": now},
        ],
        "delta_force": [
            {"hash": "df_001", "title": "Sniper Solo Queue Strategy - Niche Playstyle",
             "content": "## Sniper Solo Queue Strategy\n\nA unconventional approach to ranking up as sniper main.\n\n### Core Strategy\n- **Hide**: Stay concealed\n- **Wait**: Patience is key\n- **Move**: Relocate after each shot\n\n### Loadout\n- Primary: Bolt-action + silencer\n- Secondary: SMG for close range\n- Gear: Camo + noise reduction\n\n### Tips\n- Use high ground positions\n- Coordinate with team pings\n- Know when to switch weapons",
             "category": "niche", "game": "delta_force", "source": "NGA",
             "source_url": "https://bbs.nga.cn", "created_at": now, "updated_at": now},
            {"hash": "df_002", "title": "M4A1 Advanced Build Guide",
             "content": "## M4A1 Best Build Configuration\n\nThe M4A1 is versatile but needs the right attachments.\n\n### All-Rounder Build\n- **Barrel**: Long barrel (range + accuracy)\n- **Grip**: Vertical (reduces vertical recoil)\n- **Sight**: Red dot or holographic\n- **Mag**: Extended mag\n\n### Precision Build\n- **Barrel**: Heavy barrel (max accuracy)\n- **Grip**: Angled (reduces horizontal recoil)\n- **Sight**: 4x scope\n- **Stock**: Stable stock\n\n### Recoil Control\n- First 10 rounds are very stable\n- Slightly pull down after 10 rounds\n- Practice burst firing\n- Use cover to peek-shoot",
             "category": "weapon", "game": "delta_force", "source": "Tieba",
             "source_url": "https://tieba.baidu.com", "created_at": now, "updated_at": now},
        ]
    }
    os.makedirs(DATA_DIR, exist_ok=True)
    for game, arts in samples.items():
        with open(os.path.join(DATA_DIR, f"{game}.json"), "w", encoding="utf-8") as f:
            json.dump(arts, f, ensure_ascii=False, indent=2)
        print(f"  {game}: {len(arts)} sample articles")
    print("Sample data created!")


if __name__ == "__main__":
    if "--init" in sys.argv:
        init_sample()
        run_build()
    elif "--crawl" in sys.argv:
        run_crawl()
    elif "--build" in sys.argv:
        run_build()
    elif "--all" in sys.argv:
        run_crawl()
        run_build()
    else:
        if not os.path.exists(DATA_DIR) or not any(f.endswith(".json") for f in os.listdir(DATA_DIR)):
            print("First run - initializing sample data...")
            init_sample()
        run_build()
        print("\nUsage:")
        print("  python main.py --all    # crawl + build")
        print("  python main.py --crawl  # crawl only")
        print("  python main.py --build  # build site only")