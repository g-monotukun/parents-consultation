"""src/ の原稿から、サイト全体のHTMLを生成する。

使い方: python3 build.py

原稿の先頭には次の形式でメタ情報を書く。
<!--
title: 記事タイトル
description: 検索結果やカードに出す説明文
category: カテゴリ名
icon: school | server | globe | sparkle | code
color: violet | teal | sky | amber | coral
order: 並び順（大きいほど上）
summary: この記事でわかること1|わかること2|わかること3
date: 2026-10-15
-->
src/articles/ の原稿は記事、src/ 直下の原稿は固定ページになる。
トップページ（index.html）は記事のメタ情報から自動で作られる。
広告リンクは <div class="aff" data-aff="キー"></div> と書き、links.js に登録する。
"""
import datetime
import hashlib
import html
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).parent
SRC = ROOT / "src"
SITE = "親と実家の相談室"
TAGLINE = "親のこと、実家のこと。ひとりで抱え込まないために。"
BASE_URL = "https://g-monotukun.github.io/parents-consultation/"
# Google Search Console の所有権確認用
GSC_META = '\n<meta name="google-site-verification" content="g2Jn0JbKjPQR9hn0YPAHpSJyRZgExQNaeE51vIjmieE">'
SITE_DESC = "親の介護、実家の片づけ、遺品整理など、家族のこれからについて、相談や見積もりの前に知っておきたい基礎知識をまとめるサイトです。"

ICONS = {
    "school": '<path d="M3 9.5 12 5l9 4.5-9 4.5-9-4.5Z"/><path d="M7 11.5V16c0 1.2 2.2 2.5 5 2.5s5-1.3 5-2.5v-4.5"/><path d="M21 9.5V15"/>',
    "server": '<rect x="4" y="4" width="16" height="6.5" rx="2"/><rect x="4" y="13.5" width="16" height="6.5" rx="2"/><path d="M8 7.25h.01M8 16.75h.01M12 7.25h4M12 16.75h4"/>',
    "globe": '<circle cx="12" cy="12" r="8.5"/><path d="M3.5 12h17M12 3.5c2.4 2.4 3.5 5.3 3.5 8.5s-1.1 6.1-3.5 8.5c-2.4-2.4-3.5-5.3-3.5-8.5s1.1-6.1 3.5-8.5Z"/>',
    "sparkle": '<path d="M12 3.5 13.8 9 19.5 11l-5.7 2-1.8 5.5-1.8-5.5L4.5 11l5.7-2L12 3.5Z"/><path d="M18.5 3.5v3M17 5h3"/>',
    "code": '<path d="m8.5 8-4 4 4 4M15.5 8l4 4-4 4M13.5 5.5l-3 13"/>',
    "calendar": '<rect x="4" y="5.5" width="16" height="14.5" rx="2.5"/><path d="M4 10h16M8.5 3.5v4M15.5 3.5v4"/>',
    "phone": '<rect x="7" y="3" width="10" height="18" rx="2.5"/><path d="M11 17.5h2"/>',
    "shield": '<path d="M12 3.5 5 6.5v5c0 4.3 2.9 7.8 7 9 4.1-1.2 7-4.7 7-9v-5l-7-3Z"/><path d="m9 12 2.2 2.2L15.5 10"/>',
    "razor": '<path d="M6 4.5h12v5H6z"/><path d="M8 9.5v2M12 9.5v2M16 9.5v2"/><path d="M12 11.5V20"/>',
    "check": '<path d="m5 12.5 4.5 4.5L19 7.5"/>',
    "pen": '<path d="M4 20h4L19 9l-4-4L4 16v4Z"/><path d="m13.5 6.5 4 4"/>',
}


def version(name):
    """ファイル内容のハッシュ。URLに付けて、更新時にブラウザのキャッシュを無効にする。"""
    return hashlib.md5((ROOT / name).read_bytes()).hexdigest()[:8]


# 広告キーごとの商品紹介。記事中の <div class="aff" data-aff="キー"></div> が商品ボックスになる。
# テキストリンクは links.js の「キー_text」に登録するとボタンとして表示される。
PRODUCTS = {
    "poimitsu": dict(
        name="ぽいみつ", color="teal", icon="shield", badge="無料一括見積もり",
        tagline="不用品回収・遺品整理・空き家の片づけを、複数の業者からまとめて見積もりできる",
        points=["見積もりは無料。比べてから依頼するかを決められる", "ゴミ屋敷・遺品整理・空き家の片づけにも対応", "1社ずつ問い合わせる手間を減らせる"],
        article="cleanup-estimate"),
}


def product_box(key, p, with_banner=True):
    pr = PRODUCTS[key]
    pts = "".join(f"<li>{icon('check', 16)}<span>{s}</span></li>" for s in pr["points"])
    banner = f'<div class="aff" data-aff="{key}"></div>' if with_banner else ""
    more = "" if with_banner else f'<a class="btn ghost" href="{p}articles/{pr["article"]}.html">解説記事を読む</a>'
    return f"""<div class="product c-{pr['color']}" id="p-{key}">
<span class="product-pr">PR</span>
<div class="product-head"><span class="product-icon">{icon(pr['icon'], 28)}</span>
<div><span class="product-badge">{pr['badge']}</span><p class="product-name">{pr['name']}</p></div></div>
<p class="product-tagline">{pr['tagline']}</p>
<ul class="product-points">{pts}</ul>
{banner}<div class="product-actions"><span class="aff-btn" data-aff="{key}_text"></span>{more}</div>
</div>"""


def products_in(body, p):
    return re.sub(r'<div class="aff" data-aff="([a-z_]+)"></div>',
                  lambda m: product_box(m.group(1), p) if m.group(1) in PRODUCTS else m.group(0), body)


def icon(name, size=24):
    return (f'<svg class="ico" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[name]}</svg>')


def parse(path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"<!--\n(.*?)\n-->\n", text, re.S)
    if not m:
        raise SystemExit(f"{path}: 先頭にメタ情報のコメントがありません")
    meta = dict(line.split(": ", 1) for line in m.group(1).splitlines() if line.strip())
    meta["body"] = text[m.end():].strip()
    return meta


def jdate(s):
    d = datetime.date.fromisoformat(s)
    return f"{d.year}年{d.month}月{d.day}日"


def add_toc(body):
    """h2 に id を振り、目次のHTMLを返す。"""
    items = []

    def repl(m):
        n = len(items) + 1
        items.append(m.group(1))
        return f'<h2 id="s{n}">{m.group(1)}</h2>'

    body = re.sub(r"<h2>(.*?)</h2>", repl, body)
    if len(items) < 3:
        return body, ""
    lis = "".join(f'<li><a href="#s{i}">{t}</a></li>' for i, t in enumerate(items, 1))
    return body, f'<nav class="toc" aria-label="目次"><p class="toc-title">目次</p><ol>{lis}</ol></nav>'


def wrap_tables(body):
    """スマホで表を横スクロールできるように囲む。"""
    return body.replace("<table>", '<div class="table-wrap"><table>').replace("</table>", "</table></div>")


def reading_minutes(body):
    chars = len(re.sub(r"<[^>]+>|\s", "", body))
    return max(1, round(chars / 500))


def layout(title, description, body, p, is_home=False, path="", head=""):
    full_title = SITE if is_home else f"{title} | {SITE}"
    return f"""<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(full_title)}</title>
<meta name="description" content="{html.escape(description)}">
<meta property="og:title" content="{html.escape(full_title)}">
<meta property="og:description" content="{html.escape(description)}">
<meta property="og:type" content="{'website' if is_home else 'article'}">
<meta property="og:url" content="{BASE_URL}{path}">
<link rel="canonical" href="{BASE_URL}{path}">{GSC_META if is_home else ""}{head}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=M+PLUS+Rounded+1c:wght@700;800&family=Noto+Sans+JP:wght@400;500;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{p}style.css?v={version('style.css')}">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='9' fill='%23b45309'/%3E%3Ctext x='16' y='21' font-size='13' font-family='sans-serif' font-weight='700' fill='white' text-anchor='middle'%3E家%3C/text%3E%3C/svg%3E">
</head>
<body>
<div class="prbar">本サイトはアフィリエイト広告（PR）を利用しています</div>
<header class="site-header"><div class="wrap header-inner">
<a class="brand" href="{p}index.html"><span class="logo">家</span><span class="brand-text">{SITE}<small>{TAGLINE}</small></span></a>
<nav class="gnav"><a href="{p}index.html#articles">記事一覧</a><a href="{p}about.html">運営者情報</a></nav>
</div></header>
{body}
<footer class="site-footer"><div class="wrap">
<div class="footer-brand"><span class="logo">家</span><div><strong>{SITE}</strong><p>{SITE_DESC}</p></div></div>
<nav class="footer-nav"><a href="{p}index.html">トップ</a><a href="{p}about.html">運営者情報</a><a href="{p}privacy.html">プライバシーポリシー</a></nav>
<p class="copy">&copy; 2026 {SITE}</p>
</div></footer>
<script src="{p}links.js?v={version('links.js')}"></script>
</body>
</html>
"""


def card(a, p):
    return f"""<a class="card c-{a['color']}" href="{p}articles/{a['slug']}.html">
<div class="thumb">{icon(a['icon'], 44)}<span class="thumb-cat">{a['category']}</span></div>
<div class="card-body"><h3>{a['title']}</h3><p>{a['description']}</p>
<span class="card-meta">{jdate(a['date'])}<span class="more">読む →</span></span></div>
</a>"""


def quick_compare(body):
    """記事に登場する商品の早見表。各行から商品ボックスへ移動できる。"""
    keys = [k for k in dict.fromkeys(re.findall(r'data-aff="([a-z_]+)"', body)) if k in PRODUCTS]
    if len(keys) < 2:
        return ""
    rows = "".join(
        f'<tr><th><span class="qc-name c-{PRODUCTS[k]["color"]}">{PRODUCTS[k]["name"]}</span></th>'
        f'<td>{PRODUCTS[k]["tagline"]}</td><td><a class="qc-go" href="#p-{k}">詳しく見る ↓</a></td></tr>'
        for k in keys)
    return (f'<div class="quick"><p class="quick-title">{icon("sparkle", 18)} この記事で紹介するサービス</p>'
            f'<div class="table-wrap"><table><tr><th>サービス</th><th>特徴</th><th></th></tr>{rows}</table></div></div>')


def faq_parts(a):
    if not a.get("faq"):
        return "", ""
    qa = [item.split("::", 1) for item in a["faq"].split("||")]
    items = "".join(f'<details class="faq-item"><summary>{q}</summary><p>{ans}</p></details>' for q, ans in qa)
    data = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": ans}} for q, ans in qa]}
    return (f'<h2>よくある質問</h2><div class="faq">{items}</div>',
            f'\n<script type="application/ld+json">{json.dumps(data, ensure_ascii=False)}</script>')


def build_article(a, articles):
    p = "../"
    faq_html, faq_ld = faq_parts(a)
    body, toc = add_toc(products_in(wrap_tables(a["body"] + faq_html), p))
    updated = a.get("updated", a["date"])
    dates = f'<span>公開 {jdate(a["date"])}</span>' + (f'<span>更新 {jdate(updated)}</span>' if updated != a["date"] else "")
    conclusion = (f'<div class="conclusion"><p class="conclusion-title">結論</p><p>{a["conclusion"]}</p></div>'
                  if a.get("conclusion") else "")
    article_ld = {"@context": "https://schema.org", "@type": "Article", "headline": a["title"],
                  "description": a["description"], "datePublished": a["date"], "dateModified": updated,
                  "author": {"@type": "Organization", "name": f"{SITE} 編集部", "url": BASE_URL + "about.html"},
                  "mainEntityOfPage": f"{BASE_URL}articles/{a['slug']}.html"}
    head = f'\n<script type="application/ld+json">{json.dumps(article_ld, ensure_ascii=False)}</script>{faq_ld}'
    summary = "".join(f"<li>{icon('check', 18)}<span>{s}</span></li>" for s in a["summary"].split("|"))
    related = [r for r in articles if r["slug"] != a["slug"]]
    related.sort(key=lambda r: (r["category"] != a["category"], -int(r["order"])))
    rel_html = "".join(card(r, p) for r in related[:3])
    content = f"""<div class="article-hero c-{a['color']}"><div class="wrap narrow">
<nav class="crumbs"><a href="{p}index.html">ホーム</a><span>›</span><span>{a['category']}</span></nav>
<div class="hero-icon">{icon(a['icon'], 36)}</div>
<h1>{a['title']}</h1>
<p class="article-meta"><span class="chip">{a['category']}</span>{dates}<span>約{reading_minutes(a['body'])}分で読めます</span></p>
</div></div>
<main class="wrap narrow article">
{conclusion}
<div class="summary"><p class="summary-title">この記事でわかること</p><ul>{summary}</ul></div>
{quick_compare(a["body"])}
{toc}
<div class="prose">
{body}
</div>
<p class="note">※本記事は一般的な情報提供を目的としています。制度や料金・条件は変わることがあるため、自治体や各公式サイトでご確認ください。</p>
<aside class="author">
<span class="logo big">家</span>
<div><p class="author-name">{SITE} 編集部</p>
<p>公的機関や事業者の公開情報をもとに、相談・見積もりの前に知っておきたい基礎知識をまとめています。記事はAIを活用して作成し、公開前に運営者が内容を確認しています。</p></div>
</aside>
</main>
<section class="related"><div class="wrap"><h2 class="section-title">あわせて読みたい</h2><div class="grid">{rel_html}</div></div></section>
"""
    return layout(a["title"], a["description"], content, p, path=f"articles/{a['slug']}.html", head=head)


GOALS = [
    ("帰省のときに確認しておきたい", "親と実家のチェックリスト", "homecoming-checklist", "calendar", "amber"),
    ("実家の片づけを業者に頼みたい", "無料見積もりの取り方", "cleanup-estimate", "shield", "teal"),
    ("老人ホームを探し始めたい", "資料請求と見学のポイント", "nursing-home-search", "phone", "sky"),
]


def build_home(articles):
    p = ""
    goals = "".join(
        f'<a class="goal c-{c}" href="articles/{slug}.html"><span class="goal-icon">{icon(ic, 26)}</span>'
        f'<span class="goal-text"><strong>{q}</strong><small>{sub} →</small></span></a>'
        for q, sub, slug, ic, c in GOALS)
    products = "".join(product_box(k, p, with_banner=False) for k in PRODUCTS)
    picks_open = '<section class="wrap" id="picks">' if PRODUCTS else "<!--"
    picks_close = f'<div class="products">{products}</div>\n</section>' if PRODUCTS else "-->"
    cards = "".join(card(a, p) for a in articles)
    content = f"""<section class="hero"><div class="wrap hero-inner">
<div class="hero-text">
<p class="eyebrow">{icon('shield', 16)} 帰省の前に、ちょっと調べておく</p>
<h1>親と実家のこと、<br><span class="hl">いまのうちに</span>。</h1>
<p class="lead">親が年をとってきた、実家に物があふれている。気になっていても、家族でも話しにくいものです。<br class="pc">介護・片づけ・遺品整理について、相談や見積もりの前に知っておきたいことをまとめています。</p>
<div class="hero-cta"><a class="btn" href="#goals">悩みから探す</a><a class="btn ghost" href="#articles">記事を読む</a></div>
</div>
<div class="goal-panel" id="goals">
<p class="goal-title">{icon('sparkle', 18)} 気になっていることは？</p>
{goals}
</div>
</div></section>
<section class="points"><div class="wrap points-grid">
<div class="point">{icon('check', 22)}<div><strong>悩み別に整理</strong><p>介護・片づけ・整理から読み始められます</p></div></div>
<div class="point">{icon('check', 22)}<div><strong>申込み前の確認点</strong><p>料金や解約など、見落としやすい条件を整理</p></div></div>
<div class="point">{icon('check', 22)}<div><strong>無料でできることから</strong><p>資料請求や見積もりなど、負担のない一歩を紹介</p></div></div>
</div></section>
{picks_open}
<h2 class="section-title">このサイトで紹介しているサービス</h2>
<p class="section-lead">記事の内容に関連するサービスです。料金や条件は各公式サイトでご確認ください。</p>
{picks_close}
<main class="wrap" id="articles">
<h2 class="section-title">新着記事</h2>
<div class="grid">{cards}</div>
</main>
<section class="wrap"><div class="cta-band">
<div><p class="cta-title">次の帰省で、少しだけ話してみませんか。</p><p>まずは知るところから始めましょう。</p></div>
<a class="btn light" href="#goals">悩みから探す</a>
</div></section>
"""
    return layout(SITE, SITE_DESC, content, p, is_home=True)


def build_page(meta):
    content = f"""<div class="article-hero c-teal"><div class="wrap narrow"><h1>{meta['title']}</h1></div></div>
<main class="wrap narrow article"><div class="prose">
{wrap_tables(meta['body'])}
</div></main>
"""
    return layout(meta["title"], meta["description"], content, "", path=meta["slug"] + ".html")


def write(rel, text):
    out = ROOT / rel
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    print(f"built {rel}")


def main():
    articles = []
    for path in (SRC / "articles").glob("*.html"):
        a = parse(path)
        a["slug"] = path.stem
        articles.append(a)
    articles.sort(key=lambda a: (a["date"], int(a["order"])), reverse=True)

    for a in articles:
        write(f"articles/{a['slug']}.html", build_article(a, articles))
    pages = []
    for path in SRC.glob("*.html"):
        meta = parse(path)
        meta["slug"] = path.stem
        pages.append(path.stem + ".html")
        write(path.name, build_page(meta))
    write("index.html", build_home(articles))

    urls = [("", max(a.get("updated", a["date"]) for a in articles))]
    urls += [(f"articles/{a['slug']}.html", a.get("updated", a["date"])) for a in articles]
    urls += [(pg, None) for pg in sorted(pages)]
    entries = "".join(f"<url><loc>{BASE_URL}{u}</loc>" + (f"<lastmod>{d}</lastmod>" if d else "") + "</url>\n"
                      for u, d in urls)
    write("sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?>\n'
                         f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{entries}</urlset>\n')


if __name__ == "__main__":
    main()
