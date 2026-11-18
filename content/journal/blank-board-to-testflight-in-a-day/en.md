---
title: From an Empty Board to TestFlight in One Day
date: 2026-11-18
time: "19:01"
slug: blank-board-to-testflight-in-a-day
lang: en
translation_of: ko
description: On 2026-11-11 Dusk Blocks went from an empty scaffold to a TestFlight build. The order we built things in, and what we left for later.
category: making
---

[한국어로 읽기 →](/ko/journal/blank-board-to-testflight-in-a-day/)

Dusk Blocks is built with an AI coding assistant, working in short steps, and the git history of the first day shows the order. All times are KST, 2026-11-11.

- **12:19, scaffold.** An empty board screen, the language files, and a green gate: a script that formats, analyses and tests before every commit.
- **12:33, the core.** Pure Dart rules: bitboard, the fair tray, scoring, continue, save format, and 30 tests. No Flutter code is allowed in this layer, and a test checks that.
- **12:40, the game screen.** Drawing the board and tray, drag-and-drop with the piece lifted above your finger, game over, settings, first-run hint, endless and daily modes.
- **12:41 to 12:50, the bot simulator** ([results here](/journal/two-bots-one-thousand-games/)), and swapping two interface languages for Indonesian and Vietnamese.
- **18:17, the name.** The internal working name became Dusk Blocks.
- **18:46, TestFlight.** Build 1.0.0+2 uploaded and in the internal test group, about three minutes of processing. Not submitted for review.

## Why the order mattered

The risk in this game is not the screen, it is the rules: fairness, score, continue. So the rules went first, as pure functions with tests, and the screen came after as a thin layer on top. That is why the first playable build could be tested by bots before any person touched it.

## What was left for later

Dusk Blocks will be a paid in-app purchase (price not set yet). The "continue" feature is a placeholder while we build. The privacy policy link is a placeholder and the settings row hides itself while it is empty. Screenshots were taken by a script that plays the game by dragging pieces, so the website images come from the real app.
