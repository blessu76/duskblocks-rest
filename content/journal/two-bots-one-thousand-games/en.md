---
title: Two Bots, One Thousand Games
date: 2026-11-15
time: "19:05"
slug: two-bots-one-thousand-games
lang: en
translation_of: ko
description: Before any human played Dusk Blocks, two bots played 1,000 games each to test whether the piece generator is fair. What we measured, and what the numbers can't tell us.
category: playtest
---

[한국어로 읽기 →](/ko/journal/two-bots-one-thousand-games/)

Before a person plays a puzzle, you want evidence that the generator is not cheating them. So the first playtest of Dusk Blocks was done by bots: `tool/sim.dart` plays 1,000 games with seeds 1 to 1000, capped at 5,000 moves per game.

## The two players

- **Random bot:** picks any legal move with equal chance.
- **Greedy bot:** prefers the move that clears the most lines and scores the most, leaves fewer cells filled afterwards, and gets a bonus for a perfect clear.

## What came out (1,000 games each)

- Random bot: average score 123, median 76, about 17 placements in a median game.
- Greedy bot: average score 3,440, median 2,564, about 98 placements in a median game. The best tenth of games scored above 7,104.
- Neither bot ever hit the move cap.
- Fallback dealing (the rule we described in [the first post](/journal/never-deal-an-unplaceable-tray/)): 0.01% for the greedy bot, 0.00% for the random bot.
- Single-colour line clears per 100 games: 72.5 for the greedy bot, 1.8 for the random bot. The random bot ignores colour, so the low number is expected. A person plays somewhere between the two.

## What we changed, and what we didn't

We had set targets before running: a greedy-bot median of 60 to 150 placements, fallback under 1%, dealing time under 8 ms. All were met, so **we changed no numbers** after this run.

## The honest limits

A greedy bot is far better than a person, so its score says nothing about how hard the game feels. This table is evidence for one claim only: the generator does not create unfair deaths. How hard the game is for people will be judged on real phones. We have a few tuning candidates ready for after that: the score stage thresholds, the "crowded board" limit, and the single-colour bonus.
