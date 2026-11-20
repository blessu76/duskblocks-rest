---
title: The Dusk Blocks Board Fits the Width of the Screen
date: 2026-11-20
time: "14:15"
slug: board-fits-the-width
lang: en
translation_of: ko
description: Dusk Blocks draws an 8×8 square board sized to the screen width, stays in portrait, and centers on iPad. Here is the layout rule and what we still have not tested.
category: design
---

[한국어로 읽기 →](/ko/journal/board-fits-the-width/)

The board is 8 by 8, and it is always square. The layout question is only how big that square can be on each screen.

## The rule

The board takes the full width of the screen, minus a margin on each side. On a 320-point-wide phone, that leaves room for the board without any overflow, and the tray of three pieces sits below it. The board is never wider than 440 logical points, so on large screens it stops growing and stays in the middle.

- **Portrait only.** For the first version the game locks to portrait. A landscape board would push the tray off the bottom, and we did not want a second layout to maintain.
- **Safe areas.** The board and tray respect the system safe area, so the notch and the home indicator do not cover the play field.
- **iPad.** The board is centered in the app's shared content frame. It does not stretch across the whole tablet.

## Why not fill the screen

A board that fills a tablet would make every cell large and the piece tray far away from the finger. The cap keeps the drag distance comfortable. It also keeps the proportions the same on every device, so a piece that fits on a phone fits on a tablet.

## What we have not tested

We have checked the layout at 320 points wide, and the start and main screens hold up at that width. We have not yet run the full matrix for the game screen, the game-over overlay and the settings sheet across several widths and all languages. Long translated labels are the likeliest thing to break. That check is open work, and this post does not claim it is done.
