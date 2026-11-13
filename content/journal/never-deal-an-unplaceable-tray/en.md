---
title: Why Dusk Blocks Never Deals a Tray You Can't Place
date: 2026-11-13
time: "22:35"
slug: never-deal-an-unplaceable-tray
lang: en
translation_of: ko
description: A block puzzle can end with no mistake from the player if the three pieces simply don't fit. Here is how Dusk Blocks checks every tray before you see it.
category: design
---

[한국어로 읽기 →](/ko/journal/never-deal-an-unplaceable-tray/)

The most common complaint about block puzzles is the unfair piece: the board is crowded, the tray shows three pieces, and none of them fits anywhere. The run ends, and nothing you did caused it. When we planned Dusk Blocks we wrote down what "fair" should mean: **a game may only end because of your own placements.**

## Three options we weighed

- **Random pieces, no guarantee.** Simplest, and exactly the unfair ending we wanted to avoid.
- **At least one piece fits.** Cheap to check, but only postpones the problem. One piece fits, the other two don't, and the run ends one move later.
- **All three pieces can be placed, in some order.** This is the weakest rule that actually matches the goal, and it is the one we chose. Clearing a line in between counts: a piece that only fits after an earlier piece cleared a row is allowed.

We also considered handing the player helpful pieces by reading the board. We dropped it: if the game always gives the "right" piece, the tension is gone.

## How the check works

The board is stored as one 64-bit number, one bit per cell, so "does this piece fit here" and "which rows are full" are a few bit operations. A small solver tries the three pieces in every order, with line clears applied, and answers yes or no.

Because Dusk Blocks has a daily puzzle and saved games, the dealing has to be reproducible. So there are three rules:

1. Draw three weighted-random pieces and ask the solver. If the answer is no, draw again, up to 16 times, continuing the same random sequence.
2. The solver stops after a fixed number of search steps (50,000) instead of a time limit. Running out of steps counts as "not proven", so we redraw. The result does not depend on how fast the phone is.
3. If all 16 draws fail, a fixed fallback picks pieces that fit right now and checks the next ones greedily, so a solvable tray always exists.

## What we measured

In a 1,000-game bot simulation a tray needed on average about 1.08 draws, and the fallback was used in 0.01% of deals for the greedy bot and 0.00% for the random bot. The test suite also deals 2,000 trays and checks that none is unsolvable. Timing on a desktop VM was in microseconds; on a real phone it is not yet measured.
