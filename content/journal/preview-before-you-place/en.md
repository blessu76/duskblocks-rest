---
title: Dusk Blocks Shows Which Lines Will Clear Before You Place
date: 2026-11-21
time: "13:45"
slug: preview-before-you-place
lang: en
translation_of: ko
description: Dusk Blocks can show which rows and columns a piece would clear before you let go. Here is how the preview is computed and why it never touches the board.
category: design
---

[한국어로 읽기 →](/ko/journal/preview-before-you-place/)

A block puzzle is mostly decisions made with a piece in your hand. We wanted the game to answer one question while you hold it: if I put it here, what disappears?

## What the preview does

For a given piece and a given position, the game works out which rows and columns would be full after the piece lands. Those are the lines that would clear. If the piece does not fit at that position, the answer is simply "nothing", so an impossible spot never shows a false promise.

## How it is computed

The board is 8×8, so the whole board fits in a single 64-bit mask, one bit per cell. The preview does three small things:

- It checks that the piece fits at the chosen position.
- It adds the piece's cells to a copy of the mask.
- It compares each of the eight rows and eight columns against a full-line mask. Every line that matches would clear.

Rows and columns are checked together, so a placement that completes one of each is reported as both.

## Why it never touches the board

The preview is a pure function. It reads the board's occupancy and returns two lists, one of rows and one of columns, and it changes nothing. That matters for two reasons:

- **Dragging stays safe.** You can move a piece across the board, and nothing is placed, scored or counted until you release it.
- **It is easy to test.** The same inputs always give the same lines, so a test can set up a board, name a position and state the expected rows and columns.

## What it does not do

The preview shows lines, not points. It does not tell you the score, and it does not tell you whether the move is a good one. Choosing between clearing now and setting up a bigger clear later stays with you.
