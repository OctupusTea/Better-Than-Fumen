# Better-Than-Fumen

A Python-based Fumen editor aims to enahnce usability and simplify Fumen sharing

## Current Status

- Fully working canvas with lineclear highlight, placement, placement ghost, and field shifting
- Scroll or click to change drawing mino
- Shift-scroll or click to change placement rotation
- Click and shift-click to draw mino/placement
	- If the ONLY minos labelled with rotation symbols are selected, the shifting behaviour inverses
	- If the empty (black) or the garbage (grey) is selected, only mino drawing is available regardless of shift
- Right click to erase mino/placement
- (Temporary) Middle click to export Fumen code
- Buttons for page browsing and shift the whole field around
	- Shift-arrowkeys (up/down/left/right) can also be used to shift the whole field around
	- PageUp, PageDown, Home and End can also be used for browsing.
- Buttons to copy or delete the current page, or insert a new page before the current page.

> I'll add more control methods similar to those in [Fumen for Mobile](https://knewjade.github.io/fumen-for-mobile/) or [Fumen Editor](fumen.zui.jp/)

## Dependencies

### Required

- [`py-fumen-py`](https://github.com/OctupusTea/py-fumen-py): Python implementation of knewjade's `tetris-fumen` Node JS module.

### Recommended

- Currently utilized:
	- None
- Currenlty not utilized:
	- [`py-fumen-util`](https://github.com/OctupusTea/py-fumen-util): Python implememtation of swng's `FumenUtil`.
	- [`solution-finder`](https://github.com/knewjade/solution-finder/): knewjade's Tetris solution finder.

```Python
# To be continued
```
