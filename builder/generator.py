"""Site Generator - generates static HTML site"""
import json, re, os
from pathlib import Path
from datetime import datetime
from processor import ContentProcessor


class SiteGenerator:
    def __init__(self, config: dict, data_dir: str = "data", output_dir: str = "docs"):
        self.site_config = config.get("SITE_CONFIG", {})
        self.processor = ContentProcessor(data_dir=data_dir)
        self.output_dir = Path(output_dir)
        for sub in ["css", "js", "articles", "category", "game"]:
            (self.output_dir / sub).mkdir(parents=True, exist_ok=True)

    def _wrap(self, body: str, title: str) -> str:
        site = self.site_config
        name = site.get("site_name", "Game Guide")
        desc = site.get("site_description", "")
        year = datetime.now().year
        return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - {name}</title>
    <meta name="description" content="{desc}">
    <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>{chr(127918)}</text></svg>">
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <nav class="navbar">
        <div class="container">
            <a href="index.html" class="logo">{chr(127918)} {name}</a>
            <div class="nav-links">
                <a href="game/lol.html">{chr(127942)} League of Legends</a>
                <a href="game/delta_force.html">{chr(128299)} Delta Force</a>
                <span>{chr(128197)} {datetime.now().strftime("%m/%d")}</span>
            </div>
        </div>
    </nav>
    <main class="container">{body}</main>
    <footer class="footer">
        <div class="container">
            <p>&copy; {year} {name} | Auto-updated daily | Content from public sources</p>
        </div>
    </footer>
    <script src="js/main.js"></script>
</body>
</html>"""

    def _card(self, article: dict) -> str:
        title = article.get("title", "")
        content = article.get("content", "")
        category = article.get("category", "Other")
        game = article.get("game", "")
        source = article.get("source", "")
        created = article.get("created_at", "")[:10]
        gn = {"lol": "LoL", "delta_force": "Delta Force"}.get(game, game)
        summary = re.sub(r"[#*>`\[\]()]", "", content)[:150].strip() + "..."
        aid = article.get("hash", "")[:12]
        return f"""
        <article class="card" data-game="{game}">
            <div class="card-meta">
                <span class="tag tag-{category}">{category}</span>
                <span class="tag tag-game">{gn}</span>
            </div>
            <h2 class="card-title"><a href="articles/{aid}.html">{title}</a></h2>
            <p class="card-summary">{summary}</p>
            <div class="card-footer">
                <span>{chr(128214)} {source}</span>
                <span>{chr(128197)} {created}</span>
            </div>
        </article>"""

    def _empty(self) -> str:
        return f"""<div class="empty-state"><div class="empty-icon">{chr(128237)}</div><p>Content coming soon...</p></div>"""

    def index(self, articles: dict) -> str:
        body = f"""<section class="hero">
    <h1>{self.site_config.get("site_name", "")}</h1>
    <p class="hero-desc">{self.site_config.get("site_description", "")}</p>
    <p class="hero-update">{chr(128260)} Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M")}</p>
</section>
<section class="game-grid">
    <a href="game/lol.html" class="game-card game-lol">
        <div class="game-icon">{chr(127942)}</div>
        <h2>League of Legends</h2>
        <p>Ranking tips &middot; Champion guides &middot; Patch updates</p>
    </a>
    <a href="game/delta_force.html" class="game-card game-delta">
        <div class="game-icon">{chr(128299)}</div>
        <h2>Delta Force</h2>
        <p>Niche strats &middot; Weapon builds &middot; Map tips</p>
    </a>
</section>
<section class="section">
    <h2 class="section-title">{chr(128240)} Latest Guides</h2>
    <div class="card-grid">"""
        all_arts = []
        for ga in articles.values():
            all_arts.extend(ga)
        all_arts.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        if all_arts:
            for a in all_arts[:12]:
                body += self._card(a)
        else:
            body += self._empty()
        body += """</div></section>"""
        return self._wrap(body, "Home")

    def game_page(self, game: str, articles: list, categories: dict) -> str:
        gn = {"lol": "League of Legends", "delta_force": "Delta Force"}.get(game, game)
        ic = {"lol": chr(127942), "delta_force": chr(128299)}.get(game, chr(127918))
        body = f"""<div class="breadcrumb"><a href="../index.html">Home</a> &gt; <span>{gn}</span></div>
<section class="game-header"><h1>{ic} {gn} Guides</h1>
<p class="section-desc">{len(articles)} articles | Last updated: {datetime.now().strftime("%Y-%m-%d")}</p></section>
<section class="category-nav">"""
        for cat, cat_arts in categories.items():
            body += f"""<a href="../category/{cat}.html" class="cat-link">{cat} ({len(cat_arts)})</a>\n"""
        body += '</section><section class="section"><div class="card-grid">'
        for a in articles[:30]:
            body += self._card(a)
        body += "</div></section>"
        return self._wrap(body, f"{gn} Guides")

    def category_page(self, category: str, articles: list) -> str:
        body = f"""<div class="breadcrumb"><a href="../index.html">Home</a> &gt; <span>{category}</span></div>
<section class="section"><h1 class="section-title">{chr(127991)} {category}</h1>
<p class="section-desc">{len(articles)} articles</p>
<div class="card-grid">"""
        for a in articles[:30]:
            body += self._card(a)
        body += "</div></section>"
        return self._wrap(body, category)

    def article_page(self, article: dict) -> str:
        title = article.get("title", "")
        content = article.get("content", "")
        category = article.get("category", "")
        source = article.get("source", "")
        surl = article.get("source_url", "")
        game = article.get("game", "")
        created = article.get("created_at", "")[:10]
        gn = {"lol": "LoL", "delta_force": "Delta Force"}.get(game, game)
        # simple md to html
        html = content
        html = re.sub(r"^### (.+)$", r"<h3>\1</h3>", html, flags=re.MULTILINE)
        html = re.sub(r"^## (.+)$", r"<h2>\1</h2>", html, flags=re.MULTILINE)
        html = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html)
        html = re.sub(r"`([^`]+)`", r"<code>\1</code>", html)
        html = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2" target="_blank">\1</a>', html)
        html = re.sub(r"^> (.+)$", r"<blockquote>\1</blockquote>", html, flags=re.MULTILINE)
        lines = html.split("\n")
        result = []
        in_list = False
        for line in lines:
            s = line.strip()
            if s.startswith("- ") or s.startswith("* "):
                if not in_list:
                    result.append("<ul>")
                    in_list = True
                result.append(f"<li>{s[2:]}</li>")
            else:
                if in_list:
                    result.append("</ul>")
                    in_list = False
                if s and not s.startswith("<"):
                    result.append(f"<p>{s}</p>")
                else:
                    result.append(s)
        if in_list:
            result.append("</ul>")
        hc = "\n".join(result)
        body = f"""<div class="breadcrumb"><a href="../index.html">Home</a> &gt; <a href="../game/{game}.html">{gn}</a> &gt; <span>{title[:30]}</span></div>
<article class="article-detail">
    <div class="article-header">
        <div class="article-meta">
            <span class="tag tag-{category}">{category}</span>
            <span class="tag tag-game">{gn}</span>
            <span>{chr(128214)} {source}</span>
            <span>{chr(128197)} {created}</span>
        </div>
        <h1>{title}</h1>
    </div>
    <div class="article-content">{hc}</div>
    <div class="article-footer">
        <p>{chr(128204)} Source: <strong>{source}</strong></p>
        {f"<p>{chr(128279)} <a href=\\\"{surl}\\\" target=\\\"_blank\\\">{surl}</a></p>" if surl else ""}
    </div>
</article>"""
        return self._wrap(body, title)

    def generate_html(self):
        print("[Site] Generating static site...")
        self._write_css()
        self._write_js()
        all_articles = self.processor.get_all_articles()
        print(f"[Site] Loaded {sum(len(v) for v in all_articles.values())} articles")
        html = self.index(all_articles)
        with open(self.output_dir / "index.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("  OK index.html")
        for game, articles in all_articles.items():
            gn = {"lol": "LoL", "delta_force": "Delta Force"}.get(game, game)
            categories = self.processor.get_categories(game)
            html = self.game_page(game, articles, categories)
            with open(self.output_dir / "game" / f"{game}.html", "w", encoding="utf-8") as f:
                f.write(html)
            print(f"  OK game/{game}.html ({len(articles)} articles)")
            for cat, cat_arts in categories.items():
                html = self.category_page(cat, cat_arts)
                with open(self.output_dir / "category" / f"{cat}.html", "w", encoding="utf-8") as f:
                    f.write(html)
            for article in articles:
                html = self.article_page(article)
                aid = article.get("hash", "")[:12]
                with open(self.output_dir / "articles" / f"{aid}.html", "w", encoding="utf-8") as f:
                    f.write(html)
        print(f"[Site] Done! Output: {self.output_dir}/index.html")

    def _write_css(self):
        css = """/* Game Guide Site CSS */
:root {
    --bg: #0f0f1a; --bg-card: #1a1a2e; --bg-hover: #222240;
    --text: #e0e0e0; --text-dim: #8888aa;
    --accent: #7c5cfc; --glow: rgba(124,92,252,0.2);
    --green: #4ade80; --blue: #60a5fa; --orange: #fb923c; --pink: #f472b6;
    --border: #2a2a44; --radius: 12px;
}
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Noto Sans SC",sans-serif;
       background: var(--bg); color: var(--text); line-height: 1.7; min-height: 100vh; }
.container { max-width: 1000px; margin: 0 auto; padding: 0 20px; }
a { color: var(--accent); text-decoration: none; }
a:hover { color: var(--pink); }
.navbar { background: rgba(15,15,26,0.95); backdrop-filter: blur(10px); border-bottom: 1px solid var(--border);
          padding: 16px 0; position: sticky; top: 0; z-index: 100; }
.navbar .container { display: flex; justify-content: space-between; align-items: center; }
.logo { font-size: 1.3em; font-weight: 700; color: var(--accent); }
.nav-links { display: flex; gap: 20px; font-size: 0.9em; }
.nav-links a { color: var(--text-dim); }
.nav-links a:hover { color: var(--accent); }
.hero { text-align: center; padding: 60px 0 40px; }
.hero h1 { font-size: 2.5em; background: linear-gradient(135deg,var(--accent),var(--pink));
           -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 12px; }
.hero-desc { color: var(--text-dim); font-size: 1.1em; }
.hero-update { color: var(--text-dim); font-size: 0.85em; margin-top: 8px; }
.game-grid { display: grid; grid-template-columns: repeat(auto-fit,minmax(280px,1fr)); gap: 20px; margin: 30px 0 40px; }
.game-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius);
             padding: 30px; text-decoration: none; color: var(--text); text-align: center; transition: all .3s; }
.game-card:hover { transform: translateY(-4px); box-shadow: 0 8px 30px var(--glow); border-color: var(--accent); }
.game-icon { font-size: 3em; margin-bottom: 12px; }
.game-card h2 { margin-bottom: 8px; }
.section { margin: 40px 0; }
.section-title { font-size: 1.5em; margin-bottom: 20px; }
.section-desc { color: var(--text-dim); margin-bottom: 16px; }
.game-header { padding: 30px 0; }
.game-header h1 { font-size: 2em; }
.category-nav { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 30px; }
.cat-link { background: var(--bg-card); color: var(--text); padding: 8px 16px; border-radius: 20px;
            border: 1px solid var(--border); font-size: .85em; transition: all .3s; }
.cat-link:hover { background: var(--accent); border-color: var(--accent); color: white; }
.card-grid { display: grid; grid-template-columns: repeat(auto-fill,minmax(320px,1fr)); gap: 20px; }
.card { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius);
        padding: 24px; transition: all .3s; }
.card:hover { border-color: var(--accent); transform: translateY(-2px); box-shadow: 0 4px 20px var(--glow); }
.card-meta { margin-bottom: 12px; display: flex; gap: 8px; flex-wrap: wrap; }
.tag { display: inline-block; padding: 3px 10px; border-radius: 12px; font-size: .78em; font-weight: 500; }
.tag-game { background: rgba(255,255,255,.08); color: var(--text-dim); }
.card-title { font-size: 1.1em; margin-bottom: 10px; }
.card-title a { color: var(--text); }
.card:hover .card-title a { color: var(--accent); }
.card-summary { color: var(--text-dim); font-size: .9em; margin-bottom: 14px;
               display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; }
.card-footer { display: flex; justify-content: space-between; font-size: .82em; color: var(--text-dim); }
.article-detail { padding: 30px 0; }
.article-header { margin-bottom: 30px; }
.article-header h1 { font-size: 2em; line-height: 1.3; margin-top: 16px; }
.article-meta { display: flex; gap: 10px; flex-wrap: wrap; align-items: center; }
.article-content { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius);
                  padding: 30px; line-height: 1.9; font-size: 1.05em; }
.article-content h2 { font-size: 1.4em; margin: 30px 0 16px; color: var(--accent); }
.article-content h3 { font-size: 1.15em; margin: 24px 0 12px; color: var(--blue); }
.article-content p { margin-bottom: 14px; }
.article-content ul { margin: 12px 0 16px 24px; }
.article-content li { margin-bottom: 6px; }
.article-content blockquote { border-left: 3px solid var(--accent); padding: 12px 20px; margin: 16px 0;
                             background: rgba(124,92,252,.05); border-radius: 0 8px 8px 0; color: var(--text-dim); }
.article-footer { margin-top: 30px; padding: 20px; background: var(--bg-card);
                 border: 1px solid var(--border); border-radius: var(--radius); font-size: .9em; color: var(--text-dim); }
.article-footer a { color: var(--accent); }
.breadcrumb { font-size: .85em; color: var(--text-dim); padding: 16px 0; }
.breadcrumb a { color: var(--accent); }
.empty-state { text-align: center; padding: 60px 20px; color: var(--text-dim); grid-column: 1/-1; }
.empty-icon { font-size: 4em; margin-bottom: 16px; }
.footer { text-align: center; padding: 40px 0; margin-top: 60px; border-top: 1px solid var(--border);
          color: var(--text-dim); font-size: .85em; }
@media (max-width: 640px) {
    .hero h1 { font-size: 1.8em; }
    .card-grid { grid-template-columns: 1fr; }
    .article-content { padding: 20px; }
    .nav-links span { display: none; }
}"""
        with open(self.output_dir / "css" / "style.css", "w", encoding="utf-8") as f:
            f.write(css)

    def _write_js(self):
        js = """document.addEventListener('DOMContentLoaded',()=>{
    const cards=document.querySelectorAll('.card');
    const o=new IntersectionObserver(entries=>{
        entries.forEach(e=>{if(e.isIntersecting){e.target.style.opacity='1';e.target.style.transform='translateY(0)'}})
    },{threshold:.1});
    cards.forEach(c=>{c.style.opacity='0';c.style.transform='translateY(20px)';c.style.transition='all .5s ease';o.observe(c)})
});"""
        with open(self.output_dir / "js" / "main.js", "w", encoding="utf-8") as f:
            f.write(js)