---
title: Twenty Pieces, Not Eighteen
date: 2026-11-17
time: "13:30"
slug: twenty-pieces-not-eighteen
lang: en
translation_of: ko
description: The brief said 18 pieces, its own list had 20, and the prototype had 19. How we settled the piece set of Dusk Blocks.
category: design
---

[한국어로 읽기 →](/ko/journal/twenty-pieces-not-eighteen/)

When we started building, the piece set was written down in three places, and they disagreed.

- The brief said **18** shapes.
- The list in the same brief, counted one by one, had **20**: single and square pieces, lines of 2, 3, 4 and 5 both horizontal and vertical, and a few corners and a T.
- The prototype code had **19**. It was missing the vertical line of 5.

## The problem with 19

The prototype had a horizontal 5-line but no vertical one. With no rotation in the game, that is a real asymmetry: if only your columns are blocked, a long piece that would help only exists in one direction.

## Three options

- Keep the prototype's 19. Same as the prototype, but keeps the asymmetry.
- **Add the vertical 5-line and make it 20.** Symmetric, and matches the list in the brief. One piece different from the prototype.
- Add every rotation of every shape. More variety, but every new piece adds weights to tune, and the feel drifts from the prototype.

We took the second. The cost is almost nothing, and the benefit is that horizontal and vertical are treated alike. The T stays in a single orientation, as in the prototype.

## One practical detail

Piece ids are written into the save file, so they are fixed once chosen. Adding a piece later is easy; renaming one would break saved games. A test checks the piece table, so the next person to touch it sees right away if the count or shapes change.
