#!/usr/bin/env python3
"""Static checks for the built site. Run after scripts/build.py."""
import os
import re
import struct
import sys
from html.parser import HTMLParser

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PAGES = {
    "index.html": "en",
    "ko/index.html": "ko",
    "release-notes/index.html": "en",
    "ko/release-notes/index.html": "ko",
}
ALLOWED_LATIN_KO = {"Dusk", "Blocks", "iPhone", "App", "Store", "TestFlight", "ipe", "Contact", "EN", "KO"}
HANGUL = re.compile(r"[ㄱ-ㆎ가-힣]")
LATIN_WORD = re.compile(r"[A-Za-z][A-Za-z]+")

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
        self.text = []
        self._skip = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html":
            self.lang = a.get("lang")
        if tag in ("script", "style", "head"):
            self._skip += 1
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
    if not {"en", "ko", "x-default"} <= p.hreflangs:
        fail(f"{rel}: hreflang 누락 {sorted({'en','ko','x-default'} - p.hreflangs)}")
    if f"/style.css?v=" not in html:
        fail(f"{rel}: style.css 에 ?v= 캐시버스팅이 없다")

    for ref in p.refs:
        target = local_path(ref)
        if target and not os.path.exists(target):
            fail(f"{rel}: 깨진 로컬 참조 {ref}")

    visible = " ".join(p.text)
    if lang == "en" and HANGUL.search(visible):
        fail(f"{rel}: 영문 페이지에 한글 노출")
    if lang == "ko":
        stray = {w for w in LATIN_WORD.findall(visible) if w not in ALLOWED_LATIN_KO}
        if stray:
            fail(f"{rel}: 한글 페이지에 영문 노출 {sorted(stray)}")

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

if errors:
    print("\n".join(f"FAIL: {e}" for e in errors))
    sys.exit(1)
print(f"ok: {len(PAGES)} pages checked")
