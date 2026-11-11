#!/usr/bin/env python3
"""Generate index.html (en) and ko/index.html from one template. Run: python3 scripts/build.py"""
import os
V = "20261111e"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOTS = ["ios_01_start", "ios_02_play_start", "ios_03_dragging", "ios_04_line_clear", "ios_05_midgame", "ios_06_gameover", "ios_07_revived"]

L = {
 "en": dict(
  lang="en", path="/", other="/ko/", other_lbl="한국어", locale="en_US",
  title="Dusk Blocks — A Calm Block Puzzle for iPhone",
  desc="Dusk Blocks is a calm 8×8 block puzzle for iPhone. Place three pieces, clear lines, and enjoy daily puzzles, soft line clears, and one-handed play.",
  short="A calm 8×8 block puzzle for iPhone with daily puzzles, soft line clears, and one-handed play.",
  soon="Coming soon", eyebrow="CALM BLOCK PUZZLE", h1a="Dusk", h1b="Blocks",
  lead="Calm block puzzle, tuned for quiet evenings. Place 3 pieces on an 8×8 board, clear lines, and keep the board flowing at your own pace.",
  cta2="View screenshots", chips=["One-handed play", "Daily puzzle", "Rewarded continue only when you choose it", "11 languages"],
  feats=[("Always solvable starts", "The next three pieces always have a way to fit, so every run starts fair and calm."),
         ("Daily puzzle, one seed per day", "A fresh board every day, generated from the date for a quiet daily habit."),
         ("Line clears feel soft and rewarding", "Subtle motion, score pops, and a color-line bonus for clearing a single-color row.")],
  shots_h="Screenshots", skip="Skip to content",
  caps=[("Start the board.", "A calm first look at the 8×8 puzzle and the three-piece tray."),
        ("Place your first pieces.", "Begin with an easy opening and keep the board flexible."),
        ("Drag with one hand.", "Smooth placement designed for quick, quiet play."),
        ("Clear a line, feel the flow.", "Lines disappear with a soft burst and make room for the next move."),
        ("Mid-game, still in control.", "Plan ahead and keep the board from locking up."),
        ("When the board fills up.", "The run ends cleanly with your score and best score in view."),
        ("Continue if you want to.", "A rewarded continue appears only when you choose it.")],
  alts=["Dusk Blocks start screen", "First pieces placed", "Dragging a piece", "A line clearing", "Mid-game board", "Game over screen", "Resumed game after a continue"],
  store_h="Available on iPhone soon", store_p="The App Store release is coming soon.", store_b="iPhone only",
  foot1="Dusk Blocks — a calm block puzzle for iPhone.", foot2="Made for quiet sessions, one-handed play, and daily puzzle breaks.",
  note="Screenshots are from in-development builds.", contact="Contact", more="A game by", ),
 "ko": dict(
  lang="ko", path="/ko/", other="/", other_lbl="English", locale="ko_KR",
  title="Dusk Blocks — iPhone용 차분한 블록 퍼즐",
  desc="Dusk Blocks는 iPhone용 차분한 8×8 블록 퍼즐로, 3개 조각을 놓아 줄을 지우며 매일 가볍게 즐길 수 있습니다.",
  short="매일의 퍼즐과 부드러운 줄 삭제, 한 손 플레이를 담은 iPhone용 차분한 8×8 블록 퍼즐.",
  soon="출시 예정", eyebrow="차분한 블록 퍼즐", h1a="Dusk", h1b="Blocks",
  lead="조용한 저녁에 어울리는 차분한 블록 퍼즐. 8×8 판에 조각 3개를 놓아 줄을 지우고, 나만의 속도로 판을 이어 가세요.",
  cta2="스크린샷 보기", chips=["한 손 플레이", "매일의 퍼즐", "보상형 이어하기는 선택할 때만", "11개 언어"],
  feats=[("언제나 풀 수 있는 시작", "다음 세 조각은 항상 놓을 자리가 있어서, 매 판이 공정하고 차분하게 시작됩니다."),
         ("하루에 하나, 오늘의 퍼즐", "날짜로 만들어지는 새로운 판이 매일 열려 조용한 일상의 습관이 됩니다."),
         ("부드럽고 보람 있는 줄 삭제", "은은한 움직임과 점수 효과, 한 가지 색으로 줄을 지우면 받는 컬러 라인 보너스.")],
  shots_h="스크린샷", skip="본문으로 건너뛰기",
  caps=[("판을 시작해요.", "8×8 퍼즐과 세 조각 트레이를 차분하게 처음 만나 보세요."),
        ("첫 조각을 놓아요.", "쉬운 오프닝으로 시작해 판을 유연하게 유지하세요."),
        ("한 손으로 끌어 놓기.", "빠르고 조용한 플레이를 위한 부드러운 배치."),
        ("줄을 지우는 흐름.", "줄이 부드럽게 사라지며 다음 수를 위한 자리를 만듭니다."),
        ("중반에도 여유롭게.", "미리 계획해서 판이 막히지 않게 하세요."),
        ("판이 가득 차면.", "점수와 최고 점수를 보여 주며 깔끔하게 한 판이 끝납니다."),
        ("원하면 이어서.", "보상형 이어하기는 직접 선택할 때만 나타납니다.")],
  alts=["Dusk Blocks 시작 화면", "첫 조각을 놓은 화면", "조각을 끌어 놓는 화면", "줄이 지워지는 화면", "중반 화면", "게임 오버 화면", "이어하기 후 재개 화면"],
  store_h="곧 iPhone에서 만나요", store_p="App Store 출시를 준비하고 있어요.", store_b="iPhone 전용",
  foot1="Dusk Blocks — iPhone용 차분한 블록 퍼즐.", foot2="조용한 한 판, 한 손 플레이, 매일의 퍼즐 휴식을 위해 만들었어요.",
  note="스크린샷은 개발 중인 빌드에서 찍은 것입니다.", contact="문의", more="만든 곳", ),
}

def page(c):
    en = c["lang"] == "en"
    pre = "" if en else "../"
    canon = "https://duskblocks.ipe.rest" + c["path"]
    chips = "".join(f"<li>{x}</li>" for x in c["chips"])
    feats = "".join(f'<article class="card"><span class="ico i{i}" aria-hidden="true"></span><h3>{t}</h3><p>{d}</p></article>' for i, (t, d) in enumerate(c["feats"]))
    figs = "".join(
        f'<figure class="shot"><img src="/assets/{s}.png?v={V}" width="560" height="1217" alt="{c["alts"][i]}" loading="{"eager" if i < 1 else "lazy"}" decoding="async"><figcaption><strong>{c["caps"][i][0]}</strong> {c["caps"][i][1]}</figcaption></figure>'
        for i, s in enumerate(SHOTS))
    ld = ('{"@context":"https://schema.org","@type":"VideoGame","name":"Dusk Blocks","url":"%s","description":"%s","inLanguage":"%s","genre":"Puzzle","gamePlatform":"iOS","applicationCategory":"GameApplication","playMode":"SinglePlayer","image":"https://duskblocks.ipe.rest/assets/og.png","creator":{"@type":"Organization","name":"ipe()","url":"https://ipe.rest/"}}'
          % (canon, c["short"].replace('"', ''), c["lang"]))
    return f'''<!doctype html>
<html lang="{c["lang"]}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{c["title"]}</title>
<meta name="description" content="{c["desc"]}">
<meta name="theme-color" content="#171a36">
<meta name="color-scheme" content="dark">
<link rel="canonical" href="{canon}">
<link rel="alternate" hreflang="en" href="https://duskblocks.ipe.rest/">
<link rel="alternate" hreflang="ko" href="https://duskblocks.ipe.rest/ko/">
<link rel="alternate" hreflang="x-default" href="https://duskblocks.ipe.rest/">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Dusk Blocks">
<meta property="og:title" content="{c["title"]}">
<meta property="og:description" content="{c["short"]}">
<meta property="og:url" content="{canon}">
<meta property="og:locale" content="{c["locale"]}">
<meta property="og:image" content="https://duskblocks.ipe.rest/assets/og.png?v={V}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{c["title"]}">
<meta name="twitter:description" content="{c["short"]}">
<meta name="twitter:image" content="https://duskblocks.ipe.rest/assets/og.png?v={V}">
<link rel="icon" type="image/png" href="/assets/icon-180.png?v={V}">
<link rel="apple-touch-icon" href="/assets/icon-180.png?v={V}">
<link rel="stylesheet" href="/style.css?v={V}">
<script type="application/ld+json">{ld}</script>
</head>
<body>
<a class="skip" href="#main">{c["skip"]}</a>
<header class="bar"><div class="wrap barin">
<a class="brand" href="{c["path"]}"><img src="/assets/icon-180.png?v={V}" width="32" height="32" alt=""><span>Dusk Blocks</span></a>
<nav class="nav"><a class="lang" href="{c["other"]}" hreflang="{"ko" if en else "en"}">{c["other_lbl"]}</a><span class="pill">{c["soon"]}</span></nav>
</div></header>
<main id="main">
<section class="wrap hero">
<div class="hero-t">
<p class="eyebrow">{c["eyebrow"]}</p>
<h1>{c["h1a"]} <span>{c["h1b"]}</span></h1>
<p class="lead">{c["lead"]}</p>
<p class="cta"><span class="btn pri" aria-disabled="true">{c["soon"]}</span><a class="btn gho" href="#screenshots">{c["cta2"]}</a></p>
<ul class="chips">{chips}</ul>
</div>
<div class="hero-v" aria-hidden="true"><img class="ph p-a" src="/assets/ios_02_play_start.png?v={V}" width="560" height="1217" alt=""><img class="ph p-b" src="/assets/ios_04_line_clear.png?v={V}" width="560" height="1217" alt=""></div>
</section>
<section class="wrap sec"><div class="grid3">{feats}</div></section>
<section class="sec" id="screenshots"><div class="wrap"><h2>{c["shots_h"]}</h2></div>
<div class="gal wrap">{figs}</div></section>
<section class="wrap sec"><div class="store"><h2>{c["store_h"]}</h2><p>{c["store_p"]}</p><p class="tags"><span class="btn pri" aria-disabled="true">{c["soon"]}</span><span class="tag">{c["store_b"]}</span></p></div></section>
</main>
<footer class="foot"><div class="wrap">
<p class="f1">{c["foot1"]}</p><p>{c["foot2"]}</p>
<p class="slots"><span>Privacy</span><span>Terms</span><a href="mailto:ipe.haven@gmail.com">{c["contact"]}</a></p>
<p class="small">{c["note"]}</p>
<p class="small">© 2026 Dusk Blocks · {c["more"]} <a href="https://ipe.rest/">ipe()</a></p>
</div></footer>
</body>
</html>
'''

for k, c in L.items():
    out = os.path.join(ROOT, "index.html" if k == "en" else "ko/index.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w", encoding="utf-8").write(page(c))
print("ok")
