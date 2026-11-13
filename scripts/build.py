#!/usr/bin/env python3
"""Generate the home page for the 12 shared languages (ipe_web_kit.languages) and sitemap.xml. Run: python3 scripts/build.py"""
import json
import os
import struct
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "vendor"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ipe_web_kit import languages, seo  # noqa: E402
import journal_md  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOTS = ["ios_01_start", "ios_02_play_start", "ios_03_dragging", "ios_04_line_clear", "ios_05_midgame", "ios_06_gameover", "ios_07_revived"]
V = "20261113a"

L = {}
for _k in languages.SUPPORTED:
    _f = os.path.join(ROOT, "content", "i18n", _k + ".json")
    if not os.path.isfile(_f):
        sys.exit(f"missing translation file: content/i18n/{_k}.json")
    L[_k] = json.load(open(_f, encoding="utf-8"))
    L[_k].update(lang=_k)
# og:locale — 언어 태그 → Open Graph 지역 표기
OG_LOCALE = {"en": "en_US", "ko": "ko_KR", "ja": "ja_JP", "zh-Hant": "zh_TW", "es": "es_ES", "pt-BR": "pt_BR",
             "fr": "fr_FR", "de": "de_DE", "id": "id_ID", "th": "th_TH", "vi": "vi_VN", "tr": "tr_TR"}
SITE = "https://duskblocks.ipe.rest"
JLANGS = ("en", "ko")  # 저널 글이 있는 언어


def url(k):
    """언어 k 의 홈 경로 — 영어는 루트, 나머지는 /<태그>/ 아래."""
    return "/" if k == languages.DEFAULT else f"/{k}/"


def png_size(path):
    with open(path, "rb") as f:
        head = f.read(24)
    if head[:8] != b"\x89PNG\r\n\x1a\n":
        sys.exit(f"not a PNG: {path}")
    return struct.unpack(">II", head[16:24])


def screens(k):
    """Return {index in SHOTS: (name, folder, width, height)} — the language's own screenshots, else the English ones (앱 UI 스크린샷은 en·ko 만 있다)."""
    out = {}
    for i, name in enumerate(SHOTS):
        path = os.path.join(ROOT, "assets", "screens", k, name + ".png")
        if os.path.exists(path):
            out[i] = (name, k) + png_size(path)
        elif not os.path.isdir(os.path.join(ROOT, "assets", "screens", k)) and os.path.exists(os.path.join(ROOT, "assets", "screens", languages.DEFAULT, name + ".png")):
            out[i] = (name, languages.DEFAULT) + png_size(os.path.join(ROOT, "assets", "screens", languages.DEFAULT, name + ".png"))
        else:
            print(f"WARN: missing {k} screenshot assets/screens/{k}/{name}.png", file=sys.stderr)
    return out


def lang_js():
    """첫 방문(영어 주소) 한 번만 브라우저 언어로 보낸다 — 규칙은 languages.resolve 와 같다. 선택기에서 고른 언어는 기억한다."""
    sup = json.dumps(list(languages.SUPPORTED))
    return ("<script>(function(){try{var S=%s,K='ipe_lang',p=location.pathname;"
            "document.addEventListener('click',function(e){var a=e.target.closest&&e.target.closest('a[data-lang]');if(a){try{localStorage.setItem(K,a.getAttribute('data-lang'))}catch(x){}}});"
            "if(p!=='/')return;var st=null;try{st=localStorage.getItem(K)}catch(x){}if(st)return;"
            "function R(t){var q=String(t||'').toLowerCase().split(/[-_]/),c=q[0]==='in'?'id':q[0],r=q.slice(1),i;if(c==='zh'){var sc=r.filter(function(x){return x.length===4})[0],rg=r.filter(function(x){return x.length===2})[0];"
            "return(sc==='hant'||(!sc&&['tw','hk','mo'].indexOf(rg)>-1))?'zh-Hant':'en'}if(c==='pt')return'pt-BR';for(i=0;i<S.length;i++)if(S[i].toLowerCase()===c)return S[i];return'en'}"
            "var L=navigator.languages&&navigator.languages.length?navigator.languages:[navigator.language];for(var i=0;i<L.length;i++){var g=R(L[i]);if(g!=='en'){location.replace('/'+g+'/');return}if(String(L[i]).toLowerCase().split(/[-_]/)[0]==='en')return}}catch(x){}})()</script>"
            % sup)


def jurl(k):
    """저널 목록 경로 — 글은 en·ko 만 있다. 한국어는 /ko/journal/, 나머지 언어는 영어 /journal/ 로 간다."""
    return "/ko/journal/" if k == "ko" else "/journal/"


def header(c, cur="home"):
    k = c["lang"]
    items = "".join(
        f'<li><a href="{url(l)}" hreflang="{languages.hreflang(l)}" lang="{languages.hreflang(l)}" data-lang="{l}"'
        f'{" aria-current=" + chr(34) + "true" + chr(34) if l == k else ""}>{languages.NAMES[l]}</a></li>'
        for l in languages.SUPPORTED)
    switch = (f'<details class="langpick"><summary aria-label="{c["lang_label"]}"><span lang="{k}">{languages.NAMES[k]}</span></summary>'
              f'<ul>{items}</ul></details>')
    return (f'<header class="bar"><div class="wrap barin">'
            f'<a class="brand" href="{url(k)}"><img src="/assets/icon-180.png?v={V}" width="32" height="32" alt=""><span>Dusk Blocks</span></a>'
            f'<nav class="nav" aria-label="{c["nav_label"]}">'
            f'<a href="{url(k)}"{" aria-current=" + chr(34) + "page" + chr(34) if cur == "home" else ""}>{c["home"]}</a>'
            f'<a href="{jurl(k)}"{" aria-current=" + chr(34) + "page" + chr(34) if cur == "journal" else ""}{"" if k in JLANGS else " hreflang=" + chr(34) + "en" + chr(34)}>{c["journal"]}</a>'
            f'{switch}</nav>'
            f'</div></header>')


def footer(c):
    return (f'<footer class="foot"><div class="wrap">'
            f'<p class="slots"><a href="{jurl(c["lang"])}"{"" if c["lang"] in JLANGS else " hreflang=" + chr(34) + "en" + chr(34)}>{c["journal"]}</a><span>{c["privacy"]}</span><span>{c["terms"]}</span><a href="mailto:ipe.haven@gmail.com">{c["contact"]}</a></p>'
            f'<p class="small">© 2026 Dusk Blocks · {c["more"]} <a href="https://ipe.rest/">ipe()</a></p>'
            f'</div></footer>')


def head_common(c, title, desc, canon, alts=None, og_type="website"):
    k = c["lang"]
    if alts is None:
        alts = ([(languages.hreflang(l), SITE + url(l)) for l in languages.SUPPORTED], SITE + url(languages.DEFAULT))
    return f'''<!doctype html>
<html lang="{k}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="theme-color" content="#171a36">
<meta name="color-scheme" content="dark">
<link rel="canonical" href="{canon}">
{seo.alternate_links(alts[0], x_default=alts[1])}
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="Dusk Blocks">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canon}">
<meta property="og:locale" content="{OG_LOCALE[k]}">
<meta property="og:image" content="https://duskblocks.ipe.rest/assets/og.png?v={V}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="https://duskblocks.ipe.rest/assets/og.png?v={V}">
<link rel="icon" type="image/png" href="/assets/icon-180.png?v={V}">
<link rel="apple-touch-icon" href="/assets/icon-180.png?v={V}">
<link rel="stylesheet" href="/style.css?v={V}">
{lang_js() if k == languages.DEFAULT else ""}'''


def img(folder, name, w, h, alt, loading, cls=""):
    cls_attr = f' class="{cls}"' if cls else ""
    return (f'<img{cls_attr} src="/assets/screens/{folder}/{name}.png?v={V}" width="{w}" height="{h}" alt="{alt}" '
            f'style="aspect-ratio:{w}/{h}" loading="{loading}" decoding="async">')


def page(c):
    k = c["lang"]
    canon = SITE + url(k)
    chips = "".join(f"<li>{x}</li>" for x in c["chips"])
    feats = "".join(f'<article class="card"><span class="ico i{i}" aria-hidden="true"></span><h3>{t}</h3><p>{d}</p></article>' for i, (t, d) in enumerate(c["feats"]))
    sc = screens(k)
    figs = "".join(
        f'<figure class="shot">{img(sc[i][1], sc[i][0], sc[i][2], sc[i][3], c["alts"][i], "lazy")}<figcaption><strong>{c["caps"][i][0]}</strong> {c["caps"][i][1]}</figcaption></figure>'
        for i in sorted(sc))
    hero_v = ""
    if 1 in sc and 3 in sc:
        hero_v = (f'<div class="hero-v" aria-hidden="true">'
                  + img(sc[1][1], sc[1][0], sc[1][2], sc[1][3], "", "eager", "ph p-a")
                  + img(sc[3][1], sc[3][0], sc[3][2], sc[3][3], "", "eager", "ph p-b") + "</div>")
    cta2 = f'<a class="btn gho" href="#screenshots">{c["cta2"]}</a>' if figs else ""
    gallery = (f'<section class="sec" id="screenshots"><div class="wrap"><h2>{c["shots_h"]}</h2></div>'
               f'<div class="gal wrap">{figs}</div></section>') if figs else ""
    ld = ('{"@context":"https://schema.org","@type":"VideoGame","name":"Dusk Blocks","url":"%s","description":"%s","inLanguage":"%s","genre":"Puzzle","gamePlatform":"iOS","applicationCategory":"GameApplication","playMode":"SinglePlayer","image":"https://duskblocks.ipe.rest/assets/og.png","creator":{"@type":"Organization","name":"ipe()","url":"https://ipe.rest/"}}'
          % (canon, c["short"].replace('"', ''), k))
    return f'''{head_common(c, c["title"], c["desc"], canon)}
<script type="application/ld+json">{ld}</script>
</head>
<body>
<a class="skip" href="#main">{c["skip"]}</a>
{header(c)}
<main id="main">
<section class="wrap hero">
<div class="hero-t">
<p class="eyebrow">{c["eyebrow"]}</p>
<h1>{c["h1a"]} <span>{c["h1b"]}</span></h1>
<p class="lead">{c["lead"]}</p>
<p class="cta"><span class="btn pri" aria-disabled="true">{c["soon"]}</span>{cta2}</p>
<ul class="chips">{chips}</ul>
</div>
{hero_v}
</section>
<section class="wrap sec"><div class="grid3">{feats}</div></section>
{gallery}
<section class="wrap sec"><div class="store"><h2>{c["store_h"]}</h2><p>{c["store_p"]}</p><p class="tags"><span class="btn pri" aria-disabled="true">{c["soon"]}</span><span class="tag">{c["store_b"]}</span></p></div></section>
</main>
{footer(c)}
</body>
</html>
'''


for k, c in L.items():
    out = os.path.join(ROOT, "index.html" if k == languages.DEFAULT else f"{k}/index.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w", encoding="utf-8").write(page(c))
# ---- 저널: content/journal/<slug>/{en,ko}.md → /journal/ · /journal/<slug>/ · /ko/journal/ · /ko/journal/<slug>/ ----
JT = {
    "en": {"h1": "Journal", "lead": "Notes from making Dusk Blocks: design decisions, problems we hit, and what we measured.", "back": "All posts", "title": "Journal — Dusk Blocks", "desc": "Notes from making Dusk Blocks, a calm block puzzle for iPhone: design decisions, problems we hit, and playtests.", "by": "Dusk Blocks · ipe()"},
    "ko": {"h1": "저널", "lead": "블록핏(Dusk Blocks)을 만들며 남기는 글. 설계 결정, 막힌 문제, 측정한 것.", "back": "전체 글", "title": "저널 — 블록핏 Dusk Blocks", "desc": "아이폰용 차분한 블록 퍼즐 블록핏(Dusk Blocks)을 만들며 남기는 글: 설계 결정, 막힌 문제, 플레이테스트.", "by": "Dusk Blocks · ipe()"},
}
POSTS = journal_md.load_posts(ROOT)


def post_url(lang, slug):
    return f"{jurl(lang)}{slug}/"


def journal_list(lang):
    """lang 의 글 목록(최신순): [(slug, meta, body)]."""
    rows = [(slug, v[lang][0], v[lang][1]) for slug, v in POSTS.items() if lang in v]
    rows.sort(key=lambda r: (r[1]["date"], r[1].get("time", "00:00")), reverse=True)
    return rows


def journal_alts(slug):
    """en·ko 가 모두 있는 글만 서로 hreflang 으로 잇는다."""
    langs = [l for l in JLANGS if slug is None or l in POSTS.get(slug, {})]
    pairs = [(languages.hreflang(l), SITE + (post_url(l, slug) if slug else jurl(l))) for l in langs]
    return (pairs, SITE + (post_url("en", slug) if slug else jurl("en")))


def journal_page(lang, slug=None):
    c = L[lang]
    t = JT[lang]
    if slug is None:
        canon = SITE + jurl(lang)
        items = "".join(
            f'<li><article class="jitem"><p class="rel-meta"><time datetime="{m["date"]}">{m["date"]}</time></p>'
            f'<h2><a href="{post_url(lang, s_)}">{journal_md.inline(m["title"])}</a></h2><p>{journal_md.inline(m["description"])}</p></article></li>'
            for s_, m, _ in journal_list(lang))
        inner = (f'<h1>{t["h1"]}</h1><p class="lead">{t["lead"]}</p><ul class="jlist">{items}</ul>')
        head = head_common(c, t["title"], t["desc"], canon, journal_alts(None))
        ld = ""
    else:
        m, body = POSTS[slug][lang]
        canon = SITE + post_url(lang, slug)
        inner = (f'<p class="rel-meta"><a href="{jurl(lang)}">← {t["back"]}</a></p><article class="jpost"><p class="rel-meta"><time datetime="{m["date"]}">{m["date"]}</time></p>'
                 f'<h1>{journal_md.inline(m["title"])}</h1>{journal_md.render(body)}</article>')
        head = head_common(c, m["title"] + " — Dusk Blocks", m["description"], canon, journal_alts(slug), "article")
        stamp = m["date"] + ("T" + m["time"] + ":00+09:00" if m.get("time") else "")
        ld = ('<script type="application/ld+json">' + json.dumps({
            "@context": "https://schema.org", "@type": "Article", "headline": m["title"], "description": m["description"],
            "datePublished": stamp, "inLanguage": lang, "mainEntityOfPage": canon,
            "author": {"@type": "Organization", "name": "ipe()", "url": "https://ipe.rest/"},
            "publisher": {"@type": "Organization", "name": "ipe()", "url": "https://ipe.rest/"}}, ensure_ascii=False) + "</script>")
    return f'''{head}
{ld}
</head>
<body>
<a class="skip" href="#main">{c["skip"]}</a>
{header(c, "journal")}
<main id="main"><div class="wrap jmain">{inner}</div></main>
{footer(c)}
</body>
</html>
'''


JOURNAL_URLS = []
for lang in JLANGS:
    base = "" if lang == languages.DEFAULT else lang + "/"
    for slug, v in POSTS.items():
        if lang in v:
            d = os.path.join(ROOT, base + "journal", slug)
            os.makedirs(d, exist_ok=True)
            open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(journal_page(lang, slug))
            JOURNAL_URLS.append(post_url(lang, slug))
    d = os.path.join(ROOT, base + "journal")
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(journal_page(lang))
    JOURNAL_URLS.insert(0, jurl(lang))

open(os.path.join(ROOT, "sitemap.xml"), "w").write(
    '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    + "".join(f"<url><loc>{SITE}{url(l)}</loc></url>\n" for l in languages.SUPPORTED)
    + "".join(f"<url><loc>{SITE}{u}</loc></url>\n" for u in JOURNAL_URLS) + "</urlset>\n")
print("ok")
