---
title: Why a Combo in Dusk Blocks Lasts Three Moves
date: 2026-11-19
time: "12:45"
slug: combo-lasts-three-moves
lang: en
translation_of: ko
description: A combo in Dusk Blocks survives three placements without a clear. Here is the score formula and why we added a simple sum instead of a multiplier.
category: design
---

[한국어로 읽기 →](/ko/journal/combo-lasts-three-moves/)

Dusk Blocks has no timer and no levels. The score is the only thing that tells you how well a run is going, so it has to reward the right moves without making the number explode.

## The base score

Every placement scores the same way:

- **Each cell you place** is worth 1 point.
- **Each cleared line** is worth `10 × L × L`, where `L` is the number of lines cleared at once. One line gives 10, two give 40, three give 90, four give 160. Clearing lines together is worth more than clearing them one at a time.
- **A single-colour line** adds 30 points for each such line. Each line has eight cells, so a line counts only when all eight are the same colour.

## The combo

A combo starts when you clear lines in consecutive placements. The rule is simple:

- A placement that clears a line raises the combo by one.
- A placement that clears nothing adds one to a counter of moves since the last clear. After **three** such moves with no clear, the combo resets.
- From the second clear in a row, each clear adds `20 × (combo − 1)`.

Three is not arbitrary. The player gets three new pieces at a time, so a combo window of three placements means one tray is enough time to set up the next clear. Players can follow the rhythm without counting.

## Why a sum, not a multiplier

We considered a multiplier that grows with each combo. It is more exciting on paper. We picked a flat bonus for two reasons:

- **Scores stay readable.** With a multiplier, a long combo quickly produces numbers that are hard to compare. With a sum, the best score still means something after months of play.
- **The rules can be tested exactly.** Each rule is a short formula, so the test table can state the expected score for every case.

A full clear of the board adds a flat 300 points. It is rare, and it is a reward, not a route to the top score.

## One check

The on-screen message can say "×3" for a combo, which might suggest a multiplier. It does not. The number is a count, and the points come from the sum above.
