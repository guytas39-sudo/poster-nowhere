#!/usr/bin/env python3
"""Entry program for the-poster-for-a-place-that-i-2-20261121-0539.

Places the pre-drawn poster at $MAKEFUN_OUTPUT_DIR/entry.png
(or /output/entry.png). The poster itself is drawn at build time by
draw_image.py; this program is standard library only, because the
grader runs it in a stock Python image with nothing installed.
"""
import os
import shutil

out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
os.makedirs(out_dir, exist_ok=True)
here = os.path.dirname(os.path.abspath(__file__))
src = os.path.join(here, "entry.png")
dest = os.path.join(out_dir, "entry.png")
shutil.copyfile(src, dest)
print("wrote", dest)
