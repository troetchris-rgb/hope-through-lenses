#!/usr/bin/env python3
"""Regression check for the mobile nav menu bug found in final review.

cdn.tailwindcss.com (Tailwind v3) has no spacing-scale step for 18 or 22,
so classes like `h-22`, `top-22`, `md:py-18` silently produce no CSS.
This broke the mobile hamburger menu: the header collapsed to its
content height, the open menu positioned itself off-screen, and it
rendered as `display: block` (never `flex`) because the class list had
no unconditional `flex` utility for the open (non-hidden) state.

This script scans every .html file in the repo for:
1. Any spacing-utility class using a numeric step outside Tailwind's
   default scale (a hardcoded allowlist below).
2. Every `id="nav-menu"` element's class list containing both `hidden`
   and `flex` (so removing `hidden` at runtime actually yields
   `display: flex`, not the browser default `display: block` for <nav>).
"""
import re
import sys
from pathlib import Path

# Tailwind v3's default spacing scale (the numeric steps that exist).
VALID_STEPS = {
    "0", "px", "0.5", "1", "1.5", "2", "2.5", "3", "3.5", "4", "5", "6",
    "7", "8", "9", "10", "11", "12", "14", "16", "20", "24", "28", "32",
    "36", "40", "44", "48", "52", "56", "60", "64", "72", "80", "96",
}

SPACING_PROPS = ("h", "w", "top", "bottom", "left", "right", "p", "px",
                  "py", "pt", "pb", "pl", "pr", "m", "mx", "my", "mt",
                  "mb", "ml", "mr", "gap")

CLASS_RE = re.compile(r'class="([^"]*)"')
# matches e.g. h-22, md:top-22, py-18 but not h-[88px] (arbitrary values
# are always valid — they compile to literal CSS regardless of scale)
TOKEN_RE = re.compile(
    r'^(?:[a-z]+:)*(' + "|".join(SPACING_PROPS) + r')-(\d+(?:\.\d+)?)$'
)


def find_invalid_spacing(html, path):
    failures = []
    for class_attr in CLASS_RE.findall(html):
        for token in class_attr.split():
            m = TOKEN_RE.match(token)
            if m and m.group(2) not in VALID_STEPS:
                failures.append(f"{path}: invalid Tailwind spacing class {token!r}")
    return failures


def find_nav_menu_toggle_issue(html, path):
    failures = []
    m = re.search(r'<nav id="nav-menu" class="([^"]*)"', html)
    if not m:
        failures.append(f"{path}: no <nav id=\"nav-menu\"> found")
        return failures
    classes = set(m.group(1).split())
    if "hidden" not in classes:
        failures.append(f"{path}: nav-menu is missing the 'hidden' class (closed state)")
    if "flex" not in classes:
        failures.append(
            f"{path}: nav-menu has no unconditional 'flex' class — removing "
            "'hidden' will fall back to the browser default display (block), "
            "not a flex layout"
        )
    return failures


def main():
    root = Path(__file__).resolve().parent.parent
    html_files = sorted(root.glob("*.html")) + sorted(root.glob("en/*.html"))
    all_failures = []
    for path in html_files:
        html = path.read_text(encoding="utf-8")
        all_failures += find_invalid_spacing(html, path.relative_to(root))
        all_failures += find_nav_menu_toggle_issue(html, path.relative_to(root))

    if all_failures:
        for f in all_failures:
            print(f"FAIL: {f}")
        sys.exit(1)
    print(f"OK ({len(html_files)} pages checked)")
    sys.exit(0)


if __name__ == "__main__":
    main()
