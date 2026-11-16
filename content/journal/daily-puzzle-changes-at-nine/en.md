---
title: Why the Daily Puzzle Changes at 9 a.m. in Korea
date: 2026-11-16
time: "17:45"
slug: daily-puzzle-changes-at-nine
lang: en
translation_of: ko
description: Dusk Blocks' daily puzzle follows the UTC date, so in Korea a new puzzle starts at 9 a.m. instead of midnight. Why we chose that, and the one thing that is the same for everyone.
category: design
---

[한국어로 읽기 →](/ko/journal/daily-puzzle-changes-at-nine/)

Dusk Blocks has a daily puzzle: one board per day, generated from the date. The question that looks small is: *whose* date?

## Two choices

- **The phone's local date.** It matches "my day", and our prototype did it. But then every country has a different puzzle at the same moment, and changing the phone's clock lets you peek ahead.
- **The UTC date.** Everyone in the world gets the same puzzle at the same moment. The cost: in Korea the day flips at 9 a.m., not at midnight.

We chose UTC. The reason is less about today than about later: the best-score record is stored under the date key, so changing the date rule after release is hard. If anything shared (rankings, sharing a result) is ever added, it needs the same date for everyone. Better to settle it now.

## How the seed is made

The date turns into a number with a small hash (FNV-1a) of a text string that includes a version label. If we ever change the rules of the puzzle, bumping the version gives a fresh set of boards without touching old saved games. The random generator is a 32-bit one we wrote ourselves, so its state can be saved and a game resumed exactly where it stopped.

## What "same for everyone" really means

Only the **first tray** is identical for everyone. After that, the fairness check (see [the first post](/journal/never-deal-an-unplaceable-tray/)) depends on how you filled the board, so trays diverge between players. We considered giving everyone the same fixed sequence of pieces regardless of the board, but that cannot be combined with "every tray is solvable", so we dropped it.

## Tested

The tests cover the UTC day boundary and what happens when midnight UTC passes while a game is open.
