#!/usr/bin/env python3
"""Static checks for the built site. Run after scripts/build.py."""
import os
import re
import struct
import sys
from html.parser import HTMLParser

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "vendor"))
from ipe_web_kit import languages  # noqa: E402

PAGES = {}
for _l in languages.SUPPORTED:
    _base = "" if _l == languages.DEFAULT else _l + "/"
    PAGES[_base + "index.html"] = _l
ALLOWED_LATIN_KO = {"Dusk", "Blocks", "iPhone", "App", "Store", "TestFlight", "ipe", "Contact", "EN", "KO"}
HANGUL = re.compile(r"[ㄱ-ㆎ가-힣]")
KANA = re.compile(r"[぀-ヿ]")
HAN = re.compile(r"[一-鿿]")
THAI = re.compile(r"[฀-๿]")
LATIN_WORD = re.compile(r"[A-Za-z][A-Za-z]+")
# 간체에만 있는 글자 — zh-Hant 페이지에 섞이면 안 된다
SIMPLIFIED_ONLY = set("们这个为说时来对还给过动开关门问间体点单当师应战无书买卖产亲仅从众优会传伤价儿写决况准减则刚剑办务劳华压发变号叹后吗启员响团园国图声处头夹奋奖妇学宁实宝将尔层岁岛带帮广库张录归当德总惊惯战执报择换据摄数无时显晒术机杂权条极标样检欢毕气汉没洁济测湿满灭灯点热爱环现电画异当盘确离种积稳穷笔笼类约级纪纯纸纽线练组细终经结给络统继续维综编网罗职联艺节苏药虽见观规视览触计认让训议记讲许论设访证识译试话该详语误说请读课谁调谈谢贝负贡财责败货质购贴贵费资赛赞赠赢趋跃车轨转软轻载较辅输边达迁运进远连迟选递逻遗释钟钱银错键长门闭闪闲闻阅队阳阴阶际陈随难页顶项顺须顾预领频颜题颗风飞饭饮馆驱验鱼鲜鸟麦黄齐龙齿")

errors = []


def fail(msg):
    errors.append(msg)


def png_size(path):
    with open(path, "rb") as f:
        head = f.read(24)
    if head[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return struct.unpack(">II", head[16:24])


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.lang = None
        self.refs = []
        self.imgs = []
        self.hreflangs = set()
        self.opt_langs = []
        self.selects = {"header": 0, "footer": 0, "other": 0}
        self.nav_hrefs = []
        self.foot_hrefs = []
        self._ctx = []
        self.text = []
        self._skip = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html":
            self.lang = a.get("lang")
        if tag in ("script", "style", "head"):
            self._skip += 1
        if tag in ("header", "footer", "nav"):
            self._ctx.append(tag)
        if tag == "select":
            self.selects["header" if "header" in self._ctx else "footer" if "footer" in self._ctx else "other"] += 1
        if tag == "option" and a.get("lang"):
            self.opt_langs.append(a["lang"])
        if tag == "a" and a.get("href"):
            if "nav" in self._ctx and "noscript" not in self._ctx:
                self.nav_hrefs.append(a["href"])
            if "footer" in self._ctx:
                self.foot_hrefs.append(a["href"])
        if tag == "noscript":
            self._ctx.append("noscript")
        if tag == "link":
            if a.get("rel") == "alternate" and a.get("hreflang"):
                self.hreflangs.add(a["hreflang"])
            if a.get("href"):
                self.refs.append(a["href"])
        if tag in ("a", "script", "img") and (a.get("href") or a.get("src")):
            self.refs.append(a.get("href") or a.get("src"))
        if tag == "img":
            self.imgs.append(a)

    def handle_endtag(self, tag):
        if tag in ("header", "footer", "nav", "noscript") and tag in self._ctx:
            self._ctx.reverse(); self._ctx.remove(tag); self._ctx.reverse()
        if tag in ("script", "style", "head") and self._skip:
            self._skip -= 1

    def handle_data(self, data):
        if not self._skip:
            self.text.append(data)


def local_path(ref):
    if not ref or not ref.startswith("/") or ref.startswith("//"):
        return None
    clean = ref.split("?")[0].split("#")[0]
    if clean.endswith("/"):
        clean += "index.html"
    return os.path.join(ROOT, clean.lstrip("/"))


def check_chrome(rel, p, html):
    """헤더 select 1개(12개 언어) · 푸터 select 0개 · 내비에 약관/개인정보 없음 · 푸터에 약관/개인정보 링크."""
    if p.selects["header"] != 1 or p.selects["footer"] or p.selects["other"]:
        fail(f"{rel}: select 수 {p.selects} (헤더 1·푸터 0 이어야 한다)")
    if sorted(p.opt_langs) != sorted(languages.SUPPORTED):
        fail(f"{rel}: select option 언어 {p.opt_langs} 가 SUPPORTED 와 다르다")
    for h in p.nav_hrefs:
        if h.rstrip("/").endswith(("terms", "privacy")):
            fail(f"{rel}: 내비에 약관/개인정보 링크 {h}")
    for kind in ("privacy", "terms"):
        if not any(h.rstrip("/").endswith(kind) and not h.startswith("http") for h in p.foot_hrefs):
            fail(f"{rel}: 푸터에 {kind} 링크가 없다")
    if not any("journal" in h for h in p.nav_hrefs):
        fail(f"{rel}: 내비에 저널 링크가 없다")


for rel, lang in PAGES.items():
    full = os.path.join(ROOT, rel)
    if not os.path.isfile(full):
        fail(f"{rel}: 페이지가 없다")
        continue
    html = open(full, encoding="utf-8").read()
    p = Page()
    p.feed(html)

    if p.lang != lang:
        fail(f"{rel}: html lang={p.lang!r}, 기대값 {lang!r}")
    want = {languages.hreflang(l) for l in languages.SUPPORTED} | {"x-default"}
    if p.hreflangs != want:
        fail(f"{rel}: hreflang 불일치 — 누락 {sorted(want - p.hreflangs)} · 불필요 {sorted(p.hreflangs - want)}")
    check_chrome(rel, p, html)
    if f"/style.css?v=" not in html:
        fail(f"{rel}: style.css 에 ?v= 캐시버스팅이 없다")

    for ref in p.refs:
        target = local_path(ref)
        if target and not os.path.exists(target):
            fail(f"{rel}: 깨진 로컬 참조 {ref}")

    visible = " ".join(p.text)
    # 선택기에는 모든 언어의 자기 이름이 보이므로 글자 검사는 선택기 목록을 뺀 본문만 본다
    body = re.sub(r"|".join(re.escape(n) for n in languages.NAMES.values()), " ", visible)
    hb = lambda rx: bool(rx.search(body))
    if lang == "ko":
        stray = {w for w in LATIN_WORD.findall(body) if w not in ALLOWED_LATIN_KO}
        if stray:
            fail(f"{rel}: 한글 페이지에 영문 노출 {sorted(stray)}")
        if not hb(HANGUL):
            fail(f"{rel}: 한글 문구가 없다")
    else:
        if hb(HANGUL):
            fail(f"{rel}: {lang} 페이지에 한글 노출")
    if lang == "ja" and not hb(KANA):
        fail(f"{rel}: ja 페이지에 가나가 없다(번역 누락?)")
    if lang not in ("ja", "zh-Hant") and (hb(KANA) or hb(HAN)):
        fail(f"{rel}: {lang} 페이지에 일본어·중국어 글자 노출")
    if lang == "zh-Hant":
        if not hb(HAN) or hb(KANA):
            fail(f"{rel}: zh-Hant 페이지 한자 없음 또는 가나 노출")
        bad = sorted(set(body) & SIMPLIFIED_ONLY)
        if bad:
            fail(f"{rel}: zh-Hant 에 간체 글자 {bad}")
    if lang == "th" and not hb(THAI):
        fail(f"{rel}: th 페이지에 태국 글자 없음")
    if lang != "th" and hb(THAI):
        fail(f"{rel}: {lang} 페이지에 태국 글자 노출")

    for a in p.imgs:
        src = a.get("src", "")
        target = local_path(src)
        if not target or not os.path.exists(target) or not target.endswith(".png"):
            continue
        size = png_size(target)
        w, h = a.get("width"), a.get("height")
        if not size or not w or not h:
            fail(f"{rel}: {src} 크기 속성 누락")
            continue
        if abs(int(w) / int(h) - size[0] / size[1]) > 0.01 * size[0] / size[1]:
            fail(f"{rel}: {src} width/height 비율이 실제 PNG {size} 와 다르다")
        m = re.search(r"aspect-ratio:\s*(\d+)\s*/\s*(\d+)", a.get("style", ""))
        if m and abs(int(m[1]) / int(m[2]) - size[0] / size[1]) > 0.01 * size[0] / size[1]:
            fail(f"{rel}: {src} aspect-ratio 가 실제 PNG {size} 와 다르다")

# 저널 목록(12개 언어)·글·약관·개인정보 페이지: lang·로컬 참조·hreflang·캐시버스팅·사이트맵·헤더/푸터
sm = open(os.path.join(ROOT, "sitemap.xml"), encoding="utf-8").read()
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import journal_md  # noqa: E402
JPAGES = []
LPAGES = []
for _l in languages.SUPPORTED:
    _b = "" if _l == languages.DEFAULT else _l + "/"
    _d = os.path.join(ROOT, _b + "journal")
    if not os.path.isfile(os.path.join(_d, "index.html")):
        fail(f"{_b}journal/: 저널 목록이 없다")
        continue
    JPAGES.append((_b + "journal/index.html", _l, "list"))
    for _s in sorted(os.listdir(_d)):
        if os.path.isfile(os.path.join(_d, _s, "index.html")):
            JPAGES.append((f"{_b}journal/{_s}/index.html", _l, _s))
    for _k in ("privacy", "terms"):
        LPAGES.append((f"{_b}{_k}/index.html", _l, _k))
# 번역판은 copy_review(iris)가 있는 것만 발행 — 소스에 없으면 빌드 결과에 있으면 안 된다
SRC = journal_md.load_posts(ROOT, only_reviewed=False)
for rel, lang, kind in JPAGES:
    if kind != "list" and lang not in SRC.get(kind, {}):
        fail(f"{rel}: 소스(content/journal/{kind}/{lang}.md)가 없는 글 페이지")
    elif kind != "list" and not journal_md.is_reviewed(SRC[kind][lang][0], lang):
        fail(f"{rel}: copy_review(iris) 없는 번역판이 발행됐다")
for rel, lang, kind in JPAGES + LPAGES:
    fp = os.path.join(ROOT, rel)
    if not os.path.isfile(fp):
        fail(f"{rel}: 페이지가 없다")
        continue
    html = open(fp, encoding="utf-8").read()
    p = Page()
    p.feed(html)
    if p.lang != lang:
        fail(f"{rel}: html lang={p.lang!r}, 기대값 {lang!r}")
    if "x-default" not in p.hreflangs:
        fail(f"{rel}: hreflang x-default 가 없다")
    if kind in ("list", "privacy", "terms") and p.hreflangs != {languages.hreflang(l) for l in languages.SUPPORTED} | {"x-default"}:
        fail(f"{rel}: 12개 언어 hreflang 이어야 한다 — {sorted(p.hreflangs)}")
    if kind not in ("list", "privacy", "terms"):
        have = {languages.hreflang(l) for l in languages.SUPPORTED if l in SRC.get(kind, {}) and journal_md.is_reviewed(SRC[kind][l][0], l)}
        if p.hreflangs != have | {"x-default"}:
            fail(f"{rel}: 글 hreflang 은 발행된 언어판만 — {sorted(p.hreflangs)} ≠ {sorted(have)}")
    if "/style.css?v=" not in html:
        fail(f"{rel}: style.css 에 ?v= 캐시버스팅이 없다")
    check_chrome(rel, p, html)
    for ref in p.refs:
        target = local_path(ref)
        if target and not os.path.exists(target):
            fail(f"{rel}: 깨진 로컬 참조 {ref}")
    if "<h1>" not in html:
        fail(f"{rel}: h1 이 없다")
    if "{{" in html:
        fail(f"{rel}: 치환 안 된 자리표시자 {{{{")
    loc = "/" + rel[: -len("index.html")]
    if f"<loc>https://duskblocks.ipe.rest{loc}</loc>" not in sm:
        fail(f"{rel}: sitemap.xml 에 없다")
    if lang == "ko" and not HANGUL.search(" ".join(p.text)):
        fail(f"{rel}: 한글 문구가 없다")
if not os.path.isfile(os.path.join(ROOT, "assets", "ipe-lang.js")):
    fail("assets/ipe-lang.js 가 없다")
home = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
if "ipe-lang.js" not in home or "data-redirect" not in home:
    fail("index.html: 브라우저 언어 감지 스크립트(ipe-lang.js data-redirect)가 없다")
for _l in languages.SUPPORTED[1:] if languages.SUPPORTED[0] == languages.DEFAULT else [x for x in languages.SUPPORTED if x != languages.DEFAULT]:
    if "data-redirect" in open(os.path.join(ROOT, _l, "index.html"), encoding="utf-8").read():
        fail(f"{_l}/index.html: 언어 경로 페이지에 redirect 스크립트가 있다(루프 위험)")

# 번역 문구 파일: 키 일치 + 영어 그대로인 값(번역 누락) 검출
import json
en = json.load(open(os.path.join(ROOT, "content", "i18n", "en.json"), encoding="utf-8"))
for l in languages.SUPPORTED:
    d = json.load(open(os.path.join(ROOT, "content", "i18n", l + ".json"), encoding="utf-8"))
    miss = sorted(set(en) - set(d))
    if miss:
        fail(f"i18n/{l}.json: 키 누락 {miss}")
    if l not in (languages.DEFAULT,):
        for key in ("title", "desc", "lead", "short"):
            if d.get(key) == en[key]:
                fail(f"i18n/{l}.json: {key} 가 영어 그대로")
if errors:
    print("\n".join(f"FAIL: {e}" for e in errors))
    sys.exit(1)
print(f"ok: {len(PAGES)} pages + {len(JPAGES)} journal pages + {len(LPAGES)} legal pages checked")
