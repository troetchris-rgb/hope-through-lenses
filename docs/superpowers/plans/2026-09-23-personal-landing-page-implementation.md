# Hope through Lenses – Persönliche Landing Page Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the real, deployable 10-page (5 × DE/EN) static Hope through Lenses landing page described in the design spec, using the photos and copy already approved in the Claude Artifact mockup.

**Architecture:** Plain static HTML + Tailwind CSS (Play CDN, no build step) + minimal vanilla JS for the mobile nav toggle. Each page is a self-contained `.html` file (header/nav/footer markup is duplicated per page — there is no templating layer, by design, per the spec's "kein Build-Prozess" constraint). A small Python validator script checks structural requirements (lang attribute, title, meta description, nav completeness, image alt text, form wiring) on every page as its "test".

**Tech Stack:** HTML5, Tailwind CSS via `https://cdn.tailwindcss.com` + inline `tailwind.config`, vanilla JS, Python 3 (stdlib only) for the validator script, Netlify (hosting + Forms), Git.

**Spec:** `docs/superpowers/specs/2026-09-22-personal-landing-page-design.md`

## Global Constraints

- Colors — exactly these hex values, no others: Petrol `#0E4B44` (primary), Blau `#1B4B73` (accent), Mintblau `#8ED9D0` (secondary), Schwarz `#111111` (ink), Weiß `#FFFFFF` (paper). No gradients outside these tones (no purple/pink, no blue-to-turquoise "AI" gradient).
- Fonts — exactly two families: Fraunces (headings) and Inter (body). No third font.
- Buttons — one primary CTA per section max; everything else secondary/ghost.
- Cards — `bg-white rounded-xl shadow-sm` only, no `shadow-2xl`, no accent color bar on any edge.
- No emoji in headings or buttons. No centered body text (headings/quotes only). No glassmorphism.
- Mobile-first: every page must look correct at 390px width before desktop is considered done.
- Every `<img>` has a real, descriptive `alt` (never empty, never a filename).
- Every page has a unique `<title>` and `<meta name="description">`.
- `<html lang="de">` on all root-level pages, `<html lang="en">` on all `/en/` pages.
- Kontakt/Contact form uses Netlify Forms (`data-netlify="true"`, a `name` attribute, and a hidden `form-name` input matching it) — no custom backend.
- No placeholder copy ("Lorem ipsum", "Titel hier") anywhere in the shipped HTML.

## Review Focus

- Mobile hamburger menu that doesn't open/close on tap — the most common real-world way a mobile-first nav quietly breaks navigation.
- Kontakt form missing the hidden `form-name` input or a mismatched `name` attribute — Netlify silently fails to detect the form at deploy time, so submissions never arrive and nobody notices until a lead is lost.
- Language switcher linking to the wrong counterpart page (e.g. DE `ueber-mich.html` linking to EN `index.html` instead of `about.html`) — breaks cross-language navigation exactly where an international NGO visitor would use it.
- Duplicate or missing `<title>`/meta description across the 10 pages — hurts SEO and makes every page look the same in search results and browser tabs.
- Images with missing, empty, or filename-only `alt` text — an accessibility failure that's invisible unless specifically checked, and this project explicitly commits to accessibility in its spec.

---

## File Structure

```
KI Hope through lenses/
├── index.html                  (DE Start)
├── ueber-mich.html             (DE Über mich)
├── leistungen.html             (DE Leistungen)
├── geschichten.html            (DE Geschichten)
├── kontakt.html                (DE Kontakt)
├── en/
│   ├── index.html              (EN Home)
│   ├── about.html              (EN About)
│   ├── services.html           (EN Services)
│   ├── stories.html            (EN Stories)
│   └── contact.html            (EN Contact)
├── js/
│   ├── tailwind-config.js      (brand color/font tokens for the Play CDN)
│   └── main.js                 (mobile nav toggle)
├── styles.css                  (Google Fonts import + tiny base reset)
├── images/
│   ├── hero-orangutan.jpg
│   ├── portrait-mission.jpg
│   ├── shelter-dog.jpg
│   ├── lion.jpg
│   ├── leopard-night.jpg
│   ├── elephants-eagle.jpg
│   ├── gecko.jpg
│   ├── rhino.jpg
│   └── zebras-sunset.jpg
└── tests/
    ├── validate_page.py
    └── fixtures/
        ├── good.html
        └── bad.html
```

`images/tierbilder-web/` and `images/portrait/` (already committed) stay as the source library; Task 2 copies the specific files the site actually uses into the flat `images/` root under stable, descriptive names so page markup doesn't reference cryptic filenames like `2016p-315.jpeg`.

---

### Task 1: Page validator + fixtures

**Files:**
- Create: `tests/validate_page.py`
- Create: `tests/fixtures/good.html`
- Create: `tests/fixtures/bad.html`

**Interfaces:**
- Produces: `python3 tests/validate_page.py <path> --lang {de|en} --title-contains <substring> [--form]` — exits 0 and prints `OK` on success, exits 1 and prints one `FAIL: <reason>` line per failed check.

- [ ] **Step 1: Write the fixtures**

`tests/fixtures/good.html`:
```html
<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<title>Test Seite — Hope through Lenses</title>
<meta name="description" content="Eine Testbeschreibung für die Validierung.">
</head>
<body>
<header>
<nav>
<a class="navlink" href="index.html">Start</a>
<a class="navlink" href="ueber-mich.html">Über mich</a>
<a class="navlink" href="leistungen.html">Leistungen</a>
<a class="navlink" href="geschichten.html">Geschichten</a>
<a class="navlink" href="kontakt.html">Kontakt</a>
<a class="langlink" href="en/index.html">EN</a>
</nav>
</header>
<main>
<img src="images/test.jpg" alt="Ein Testbild mit echter Beschreibung">
<form name="contact" method="POST" data-netlify="true">
<input type="hidden" name="form-name" value="contact">
</form>
</main>
</body>
</html>
```

`tests/fixtures/bad.html`:
```html
<!doctype html>
<html>
<head>
<title></title>
</head>
<body>
<header>
<nav>
<a class="navlink" href="index.html">Start</a>
</nav>
</header>
<main>
<img src="images/test.jpg" alt="">
<form name="contact" method="POST">
</form>
</main>
</body>
</html>
```

- [ ] **Step 2: Write the validator**

```python
#!/usr/bin/env python3
"""Structural validator for Hope through Lenses static pages.

Checks (no external dependencies, stdlib html.parser only):
- <html lang="..."> matches the expected language
- <title> is non-empty and contains an expected substring
- <meta name="description" content="..."> is non-empty
- nav has exactly 5 links with class="navlink"
- a language-switch link with class="langlink" is present
- every <img> has a non-empty alt attribute
- if --form is passed: a <form> exists with data-netlify="true", a name
  attribute, and a hidden input named "form-name" whose value matches
  the form's name
"""
import argparse
import sys
from html.parser import HTMLParser


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.html_lang = None
        self.title_parts = []
        self.in_title = False
        self.meta_description = None
        self.nav_links = []
        self.lang_links = []
        self.images = []
        self.forms = []
        self._current_form = None

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == "html":
            self.html_lang = attrs_dict.get("lang")
        elif tag == "title":
            self.in_title = True
        elif tag == "meta" and attrs_dict.get("name") == "description":
            self.meta_description = attrs_dict.get("content", "")
        elif tag == "a" and "navlink" in (attrs_dict.get("class") or "").split():
            self.nav_links.append(attrs_dict.get("href"))
        elif tag == "a" and "langlink" in (attrs_dict.get("class") or "").split():
            self.lang_links.append(attrs_dict.get("href"))
        elif tag == "img":
            self.images.append(attrs_dict.get("alt"))
        elif tag == "form":
            self._current_form = {
                "name": attrs_dict.get("name"),
                "netlify": attrs_dict.get("data-netlify"),
                "hidden_form_name_value": None,
            }
            self.forms.append(self._current_form)
        elif tag == "input" and self._current_form is not None:
            if attrs_dict.get("type") == "hidden" and attrs_dict.get("name") == "form-name":
                self._current_form["hidden_form_name_value"] = attrs_dict.get("value")

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
        if tag == "form":
            self._current_form = None

    def handle_data(self, data):
        if self.in_title:
            self.title_parts.append(data)


def validate(path, lang, title_contains, require_form):
    with open(path, encoding="utf-8") as f:
        html = f.read()
    parser = PageParser()
    parser.feed(html)
    failures = []

    if parser.html_lang != lang:
        failures.append(f"expected <html lang=\"{lang}\">, got {parser.html_lang!r}")

    title = "".join(parser.title_parts).strip()
    if not title:
        failures.append("title is empty")
    elif title_contains not in title:
        failures.append(f"title {title!r} does not contain {title_contains!r}")

    if not parser.meta_description or not parser.meta_description.strip():
        failures.append("meta description is missing or empty")

    if len(parser.nav_links) != 5:
        failures.append(f"expected 5 nav links, found {len(parser.nav_links)}")

    if not parser.lang_links:
        failures.append("no language-switch link (class=\"langlink\") found")

    for alt in parser.images:
        if alt is None or not alt.strip():
            failures.append("an <img> is missing a real alt attribute")
            break

    if require_form:
        if not parser.forms:
            failures.append("no <form> found")
        else:
            form = parser.forms[0]
            if form["netlify"] != "true":
                failures.append("form is missing data-netlify=\"true\"")
            if not form["name"]:
                failures.append("form is missing a name attribute")
            elif form["hidden_form_name_value"] != form["name"]:
                failures.append(
                    "hidden form-name input value does not match the form's name "
                    f"(name={form['name']!r}, hidden value={form['hidden_form_name_value']!r})"
                )

    return failures


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    parser.add_argument("--lang", required=True, choices=["de", "en"])
    parser.add_argument("--title-contains", required=True)
    parser.add_argument("--form", action="store_true")
    args = parser.parse_args()

    failures = validate(args.path, args.lang, args.title_contains, args.form)
    if failures:
        for f in failures:
            print(f"FAIL: {f}")
        sys.exit(1)
    print("OK")
    sys.exit(0)


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Run the validator against both fixtures to confirm it discriminates correctly**

Run: `python3 tests/validate_page.py tests/fixtures/good.html --lang de --title-contains "Test Seite" --form`
Expected: `OK` (exit 0)

Run: `python3 tests/validate_page.py tests/fixtures/bad.html --lang de --title-contains "Test Seite" --form`
Expected: multiple `FAIL:` lines (wrong/missing lang, empty title, missing meta description, nav link count, missing langlink, empty alt, missing data-netlify) (exit 1)

- [ ] **Step 4: Commit**

```bash
git add tests/validate_page.py tests/fixtures/good.html tests/fixtures/bad.html
git commit -m "Add structural validator for static HTML pages"
```

---

### Task 2: Finalize images

**Files:**
- Create: `images/hero-orangutan.jpg`
- Create: `images/portrait-mission.jpg`
- Create: `images/shelter-dog.jpg`
- Create: `images/lion.jpg`
- Create: `images/leopard-night.jpg`
- Create: `images/elephants-eagle.jpg`
- Create: `images/gecko.jpg`
- Create: `images/rhino.jpg`
- Create: `images/zebras-sunset.jpg`

**Interfaces:**
- Produces: the exact filenames every later page task's `<img src="images/...">` refers to.

- [ ] **Step 1: Copy the approved mockup photos to their final, descriptive filenames**

```bash
cd "/Users/admin/Documents/KI Hope through lenses"
cp images/tierbilder-web/2012-422.jpeg images/hero-orangutan.jpg
cp images/portrait/portrait-monkey.jpg images/portrait-mission.jpg
cp images/portrait/shelter-dog.jpg images/shelter-dog.jpg
cp images/tierbilder-web/2008-156.jpeg images/lion.jpg
cp images/tierbilder-web/2016p-315.jpeg images/leopard-night.jpg
cp images/tierbilder-web/2016p-67.jpeg images/elephants-eagle.jpg
cp images/tierbilder-web/2008-238.jpeg images/gecko.jpg
cp images/tierbilder-web/2010-154.jpeg images/rhino.jpg
cp images/tierbilder-web/2016p-231.jpeg images/zebras-sunset.jpg
```

- [ ] **Step 2: Verify all nine files exist and are under 1MB each (they were already resized to max 1800px earlier this session)**

Run: `ls -lh images/*.jpg | awk '{print $5, $9}'`
Expected: 9 lines, each file between roughly 250K and 1.2M

- [ ] **Step 3: Commit**

```bash
git add images/hero-orangutan.jpg images/portrait-mission.jpg images/shelter-dog.jpg images/lion.jpg images/leopard-night.jpg images/elephants-eagle.jpg images/gecko.jpg images/rhino.jpg images/zebras-sunset.jpg
git commit -m "Add final, descriptively-named images for the live site"
```

---

### Task 3: Shared Tailwind config, styles, and nav JS

**Files:**
- Create: `js/tailwind-config.js`
- Create: `styles.css`
- Create: `js/main.js`

**Interfaces:**
- Produces: `js/tailwind-config.js` (loaded via `<script src="js/tailwind-config.js">` right after the Tailwind CDN `<script>` tag on every page — sets `window.tailwind.config`), `styles.css` (linked on every page), `js/main.js` exposing no globals, just wiring a click handler to `#nav-toggle` / `#nav-menu`.

- [ ] **Step 1: Write the Tailwind brand config**

```javascript
tailwind.config = {
  theme: {
    extend: {
      colors: {
        primary: "#0E4B44",
        secondary: "#8ED9D0",
        accent: "#1B4B73",
        ink: "#111111",
        paper: "#FFFFFF",
      },
      fontFamily: {
        heading: ["Fraunces", "serif"],
        body: ["Inter", "sans-serif"],
      },
    },
  },
};
```

- [ ] **Step 2: Write the base stylesheet**

```css
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600&family=Inter:wght@400;500;600&display=swap');

body {
  font-family: 'Inter', sans-serif;
}

h1, h2, h3 {
  font-family: 'Fraunces', serif;
}

#nav-menu.hidden {
  display: none;
}
```

- [ ] **Step 3: Write the mobile nav toggle script**

```javascript
document.addEventListener("DOMContentLoaded", function () {
  var toggle = document.getElementById("nav-toggle");
  var menu = document.getElementById("nav-menu");
  if (!toggle || !menu) return;
  toggle.addEventListener("click", function () {
    var isHidden = menu.classList.contains("hidden");
    menu.classList.toggle("hidden", !isHidden === false ? true : false);
    menu.classList.toggle("hidden");
    toggle.setAttribute("aria-expanded", isHidden ? "true" : "false");
  });
});
```

- [ ] **Step 4: Manually verify the toggle logic in isolation**

Create a scratch file `/tmp/nav-test.html`:
```html
<!doctype html>
<html><body>
<button id="nav-toggle" aria-expanded="false">Menu</button>
<div id="nav-menu" class="hidden"><a href="#">Start</a></div>
<script src="/Users/admin/Documents/KI Hope through lenses/js/main.js"></script>
</body></html>
```
Open it in a browser, click the button twice. Expected: the menu div's `hidden` class toggles off then on each click (inspect via browser dev tools), and `aria-expanded` flips `false → true → false`.

- [ ] **Step 5: Commit**

```bash
git add js/tailwind-config.js styles.css js/main.js
git commit -m "Add shared Tailwind config, base styles, and mobile nav toggle"
```

---

### Task 4: DE Start (`index.html`)

**Files:**
- Create: `index.html`
- Test: manual (`tests/validate_page.py`)

**Interfaces:**
- Consumes: `js/tailwind-config.js`, `styles.css`, `js/main.js`, `images/hero-orangutan.jpg`, `images/portrait-mission.jpg`, `images/gecko.jpg`, `images/rhino.jpg`, `images/zebras-sunset.jpg`, `images/shelter-dog.jpg`, `images/lion.jpg`, `images/leopard-night.jpg`.
- Produces: the DE home page other DE pages' nav links target as `index.html`, and the EN home page's language switcher targets as `../index.html`.

- [ ] **Step 1: Run the validator against the not-yet-created file to confirm it fails**

Run: `python3 tests/validate_page.py index.html --lang de --title-contains "Hope through Lenses"`
Expected: `FAIL` — file not found (script raises `FileNotFoundError`; this is the expected "red" state)

- [ ] **Step 2: Write the page**

```html
<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Hope through Lenses — Gemeinsam Wirkung für Tiere, Natur und Planet</title>
<meta name="description" content="Wissenschaftlich fundierte Strategie, KI und internationale Führungserfahrung für Tierschutz- und Naturschutz-NGOs. Ein Partner, kein Berater auf Distanz.">
<script src="https://cdn.tailwindcss.com"></script>
<script src="js/tailwind-config.js"></script>
<link rel="stylesheet" href="styles.css">
</head>
<body class="bg-white text-ink font-body">

<header class="h-22 px-6 md:px-16 flex items-center justify-between border-b border-black/10">
  <a href="index.html" class="font-heading text-xl font-semibold text-accent">Hope through Lenses</a>
  <button id="nav-toggle" aria-expanded="false" aria-controls="nav-menu" class="md:hidden w-9 h-9 flex flex-col justify-center gap-1.5 items-center">
    <span class="w-5 h-0.5 bg-ink"></span>
    <span class="w-5 h-0.5 bg-ink"></span>
    <span class="w-5 h-0.5 bg-ink"></span>
  </button>
  <nav id="nav-menu" class="hidden md:flex md:items-center gap-9 absolute md:static top-22 left-0 right-0 bg-white md:bg-transparent flex-col md:flex-row p-6 md:p-0 border-b md:border-0 border-black/10">
    <a class="navlink py-2 md:py-0 text-sm font-medium text-primary" href="index.html">Start</a>
    <a class="navlink py-2 md:py-0 text-sm font-medium" href="ueber-mich.html">Über mich</a>
    <a class="navlink py-2 md:py-0 text-sm font-medium" href="leistungen.html">Leistungen</a>
    <a class="navlink py-2 md:py-0 text-sm font-medium" href="geschichten.html">Geschichten</a>
    <a class="navlink py-2 md:py-0 text-sm font-medium" href="kontakt.html">Kontakt</a>
    <div class="flex items-center gap-1.5 md:ml-3 md:pl-6 md:border-l border-black/10 pt-2 md:pt-0">
      <span class="text-xs font-semibold text-primary">DE</span>
      <span class="text-xs text-black/30">/</span>
      <a class="langlink text-xs font-medium text-black/50" href="en/index.html">EN</a>
    </div>
  </nav>
</header>

<section class="relative h-[520px] md:h-[620px] flex items-center overflow-hidden">
  <img src="images/hero-orangutan.jpg" alt="Orang-Utan-Jungtier blickt direkt in die Kamera" class="absolute inset-0 w-full h-full object-cover object-[50%_45%]">
  <div class="absolute inset-0 bg-[linear-gradient(270deg,rgba(10,26,24,0.90)_0%,rgba(10,26,24,0.62)_35%,rgba(10,26,24,0.12)_62%)] md:bg-[linear-gradient(270deg,rgba(10,26,24,0.90)_0%,rgba(10,26,24,0.62)_35%,rgba(10,26,24,0.12)_62%)]"></div>
  <div class="relative w-full px-6 md:px-16 flex md:justify-end">
    <div class="max-w-xl flex flex-col items-start md:items-end text-left md:text-right gap-5">
      <span class="text-sm font-semibold tracking-wide uppercase text-secondary">Für Tiere, Natur und unseren Planeten</span>
      <h1 class="font-heading font-medium text-4xl md:text-5xl leading-tight text-paper">Gemeinsam handeln.<br>Gemeinsam Wirkung schaffen.</h1>
      <p class="text-base md:text-lg leading-relaxed text-paper/90 max-w-md">Ich verbinde Passion, wissenschaftliche Expertise, internationale Führungserfahrung und moderne Technologien, um NGOs dabei zu unterstützen, ihre Wirkung nachhaltig zu vergrößern — als Partner, nicht als Berater auf Distanz.</p>
      <div class="flex flex-wrap gap-3.5 mt-2">
        <a href="geschichten.html" class="bg-secondary text-primary rounded-lg px-7 py-3.5 font-semibold text-sm">Meine Geschichte entdecken</a>
        <a href="kontakt.html" class="border border-white/70 text-paper rounded-lg px-6 py-3 font-semibold text-sm">Kontakt aufnehmen</a>
      </div>
    </div>
  </div>
</section>

<section class="py-16 md:py-24 px-6 md:px-16 flex flex-col md:flex-row gap-12 md:gap-16 items-center bg-secondary/10">
  <div class="flex-1 flex flex-col gap-5">
    <span class="text-sm font-semibold tracking-wide uppercase text-primary">Wonder — der Moment, der bleibt</span>
    <h2 class="font-heading font-medium text-3xl leading-snug text-accent">Jede Spezies, jeder geschützte Lebensraum ist ein Grund weiterzumachen.</h2>
    <p class="text-base leading-relaxed text-ink/90 max-w-prose">Als Tierarzt und Wissenschaftler habe ich gesehen, was möglich ist, wenn Wissen, Führungsstärke und echte Partnerschaft zusammenkommen. Nach vielen erfolgreichen Berufsjahren bin ich dankbar für all die Erfahrungen — und es ist Zeit, etwas zurückzugeben. Als Tierarzt möchte ich meinen Fokus auf Tierschutz legen und stelle meine Fähigkeiten Tierschutzorganisationen zur Verfügung, für mehr Wirkung bei Tieren, Natur und unserem Planeten.</p>
    <a href="ueber-mich.html" class="mt-1 text-sm font-semibold text-primary inline-flex items-center gap-1.5">Mehr über meinen Weg →</a>
  </div>
  <img src="images/portrait-mission.jpg" alt="Portrait im Feld, mit einem Totenkopfäffchen auf der Schulter" class="flex-1 w-full h-[280px] md:h-[340px] rounded-xl object-cover object-[75%_40%]">
</section>

<section class="py-16 md:py-24 px-6 md:px-16 bg-primary flex flex-col md:flex-row gap-12 md:gap-16 items-center">
  <div class="flex-1 grid grid-cols-2 grid-rows-2 gap-3 h-[280px] md:h-[280px]">
    <img src="images/gecko.jpg" alt="Wüstengecko im Nahporträt auf Sand" class="row-span-2 w-full h-full object-cover rounded-xl">
    <img src="images/rhino.jpg" alt="Spitzmaulnashorn im dichten Gebüsch" class="w-full h-full object-cover rounded-xl">
    <img src="images/zebras-sunset.jpg" alt="Zebraherde bei Sonnenuntergang in der Savanne" class="w-full h-full object-cover rounded-xl">
  </div>
  <div class="flex-1 flex flex-col gap-5">
    <span class="text-sm font-semibold tracking-wide uppercase text-secondary">Hope Through The Lens</span>
    <h2 class="font-heading font-medium text-3xl leading-snug text-paper">Bilder, die berühren — und zum Handeln bewegen.</h2>
    <p class="text-base leading-relaxed text-paper/85 max-w-prose">Neben Strategie und Wissenschaft bringe ich meine fotografische Arbeit ein: authentische, emotionale Bilder in hoher Qualität — keine Stockfotos, keine gestellten Szenen. Sie zeigen das Tier, den Lebensraum und die Menschen, die ihn schützen, und erhöhen so die Wirkung und Reichweite eurer Kommunikation.</p>
    <a href="geschichten.html" class="mt-1 text-sm font-semibold text-secondary inline-flex items-center gap-1.5">Fotografische Arbeit ansehen →</a>
  </div>
</section>

<section class="py-16 md:py-24 px-6 md:px-16">
  <h2 class="font-heading font-medium text-2xl md:text-3xl mb-10">Wie wir gemeinsam Wirkung vergrößern</h2>
  <div class="grid grid-cols-1 md:grid-cols-3 gap-6 md:gap-8">
    <a href="ueber-mich.html" class="flex flex-col rounded-xl overflow-hidden border border-black/10 shadow-sm">
      <img src="images/shelter-dog.jpg" alt="Welpe blickt durch Gitterstäbe in einem Tierheim" class="h-44 w-full object-cover object-[50%_35%]">
      <div class="p-6 flex flex-col gap-2.5">
        <span class="text-xs font-semibold tracking-wide uppercase text-accent">Über mich</span>
        <h3 class="font-heading font-medium text-lg">Warum diese Mission mich trägt</h3>
        <p class="text-sm leading-relaxed text-ink/70">Vom Tierarzt zum internationalen Executive — meine Geschichte und was mich antreibt.</p>
      </div>
    </a>
    <a href="leistungen.html" class="flex flex-col rounded-xl overflow-hidden border border-black/10 shadow-sm">
      <img src="images/lion.jpg" alt="Löwe im Nahporträt mit direktem Blickkontakt" class="h-44 w-full object-cover object-[50%_32%]">
      <div class="p-6 flex flex-col gap-2.5">
        <span class="text-xs font-semibold tracking-wide uppercase text-primary">Leistungen</span>
        <h3 class="font-heading font-medium text-lg">So vergrößern wir eure Wirkung</h3>
        <p class="text-sm leading-relaxed text-ink/70">Wissenschaftlich fundierte Strategie, KI und Leadership-Erfahrung für eure Organisation.</p>
      </div>
    </a>
    <a href="geschichten.html" class="flex flex-col rounded-xl overflow-hidden border border-black/10 shadow-sm">
      <img src="images/leopard-night.jpg" alt="Leopard nachts auf einem Ast" class="h-44 w-full object-cover">
      <div class="p-6 flex flex-col gap-2.5">
        <span class="text-xs font-semibold tracking-wide uppercase text-secondary bg-primary px-2 py-0.5 rounded w-fit">Geschichten</span>
        <h3 class="font-heading font-medium text-lg">Wonder → Connection → Hope</h3>
        <p class="text-sm leading-relaxed text-ink/70">Echte Momente aus Projekten — dort, wo Wissenschaft auf Hoffnung trifft.</p>
      </div>
    </a>
  </div>
</section>

<section class="py-14 md:py-18 px-6 md:px-16 bg-accent flex flex-col md:flex-row items-center justify-between gap-8">
  <h2 class="font-heading font-medium text-xl md:text-2xl text-paper max-w-lg">Lass uns gemeinsam herausfinden, wie eure Organisation ihre Wirkung vergrößern kann.</h2>
  <a href="kontakt.html" class="bg-secondary text-primary rounded-lg px-7 py-3.5 font-semibold text-sm whitespace-nowrap">Gespräch vereinbaren</a>
</section>

<footer class="py-12 px-6 md:px-16 bg-[#0B120F] flex flex-col md:flex-row items-center justify-between gap-6">
  <span class="font-heading text-base text-paper">Hope through Lenses</span>
  <div class="flex flex-wrap justify-center gap-6">
    <a href="ueber-mich.html" class="text-sm text-paper/65">Über mich</a>
    <a href="leistungen.html" class="text-sm text-paper/65">Leistungen</a>
    <a href="geschichten.html" class="text-sm text-paper/65">Geschichten</a>
    <a href="kontakt.html" class="text-sm text-paper/65">Kontakt</a>
  </div>
  <div class="flex gap-1.5">
    <span class="text-sm font-semibold text-secondary">DE</span>
    <span class="text-sm text-paper/30">/</span>
    <a class="langlink text-sm text-paper/50" href="en/index.html">EN</a>
  </div>
</footer>

<script src="js/main.js"></script>
</body>
</html>
```

- [ ] **Step 3: Run the validator to confirm it passes**

Run: `python3 tests/validate_page.py index.html --lang de --title-contains "Hope through Lenses"`
Expected: `OK`

- [ ] **Step 4: Open the page in a browser and manually check both viewports**

Open `index.html` directly in a browser. Resize to 390px wide: confirm the hamburger menu appears and opens/closes the nav; confirm the hero text and image both remain legible; confirm no horizontal scrollbar. Resize to 1280px: confirm the hero shows text right-aligned over the visible (unobstructed) side of the orangutan's face, and the three-column teaser grid lays out side by side.

- [ ] **Step 5: Commit**

```bash
git add index.html
git commit -m "Add DE start page"
```

---

### Task 5: DE Über mich (`ueber-mich.html`)

**Files:**
- Create: `ueber-mich.html`

**Interfaces:**
- Consumes: same shared assets as Task 4, plus `images/shelter-dog.jpg` as the page's lead image.
- Produces: `ueber-mich.html`, the target of every other DE page's "Über mich" nav link.

- [ ] **Step 1: Run the validator to confirm it fails (file doesn't exist yet)**

Run: `python3 tests/validate_page.py ueber-mich.html --lang de --title-contains "Über mich"`
Expected: `FAIL` — file not found

- [ ] **Step 2: Write the page**

Use the identical `<head>` and `<header>`/`<nav>`/`<footer>` markup from Task 4's `index.html`, with two changes: the `<title>`/`<meta description>` below, and the "Start" navlink loses its `text-primary` highlight while "Über mich" gains it (`class="navlink py-2 md:py-0 text-sm font-medium text-primary"` on the Über mich link, plain `font-medium` on Start). Replace the `<title>` and `<meta name="description">` with:

```html
<title>Über mich — Hope through Lenses</title>
<meta name="description" content="Vom Tierarzt und Wissenschaftler zum internationalen Executive: warum ich meine Erfahrung heute in den Dienst von Tierschutz-NGOs stelle.">
```

Replace everything between `</header>` and `<footer>` with:

```html
<section class="pt-14 pb-10 md:pt-20 md:pb-14 px-6 md:px-16">
  <span class="text-sm font-semibold tracking-wide uppercase text-primary">Über mich</span>
  <h1 class="font-heading font-medium text-3xl md:text-4xl leading-tight text-accent mt-4 max-w-2xl">Vom Tierarzt zum Partner internationaler NGOs</h1>
</section>

<section class="px-6 md:px-16 pb-12 md:pb-16">
  <img src="images/shelter-dog.jpg" alt="Welpe blickt durch Gitterstäbe in einem Tierheim" class="w-full h-[260px] md:h-[420px] rounded-xl object-cover object-[50%_35%]">
</section>

<section class="px-6 md:px-16 pb-16 md:pb-24 flex flex-col gap-6 max-w-prose">
  <p class="text-base leading-relaxed text-ink/90">Meine Laufbahn begann am OP-Tisch: als Tierarzt habe ich gelernt, unter Druck klar zu entscheiden, und dass jedes einzelne Leben, um das man sich kümmert, zählt. Aus der klinischen Praxis hat mich der Weg über die Wissenschaft in internationale Führungspositionen geführt — dort habe ich gelernt, wie man Organisationen aufbaut, Teams über Ländergrenzen hinweg führt und komplexe Vorhaben tatsächlich zum Abschluss bringt.</p>
  <p class="text-base leading-relaxed text-ink/90">Diese drei Welten — Tiermedizin, Wissenschaft, internationale Führung — liefen lange getrennt nebeneinander her. Heute führe ich sie zusammen. Nach vielen erfolgreichen Berufsjahren bin ich dankbar für all die Erfahrungen, die ich sammeln durfte, und es ist Zeit, etwas zurückzugeben. Nicht als Ruhestandsprojekt, sondern als das, was mich am meisten antreibt: Tieren, Natur und unserem Planeten mit genau den Werkzeugen zu helfen, die ich mir über Jahrzehnte erarbeitet habe.</p>
  <p class="text-base leading-relaxed text-ink/90">Deshalb arbeite ich heute mit Tierschutz- und Naturschutzorganisationen zusammen — nicht als externer Berater auf Distanz, sondern als Partner, der zuhört, versteht und gemeinsam Lösungen entwickelt und umsetzt. Wissenschaftlich fundiert, ehrlich auch dann, wenn etwas nicht passt, und immer mit dem Ziel, echte Wirkung für Tiere, Natur und Planet zu schaffen.</p>
  <a href="leistungen.html" class="mt-2 text-sm font-semibold text-primary inline-flex items-center gap-1.5">Wie das konkret aussieht →</a>
</section>
```

- [ ] **Step 3: Run the validator to confirm it passes**

Run: `python3 tests/validate_page.py ueber-mich.html --lang de --title-contains "Über mich"`
Expected: `OK`

- [ ] **Step 4: Manually verify in browser at 390px and 1280px widths** (same checklist as Task 4 step 4, applied to this page)

- [ ] **Step 5: Commit**

```bash
git add ueber-mich.html
git commit -m "Add DE Über mich page"
```

---

### Task 6: DE Leistungen (`leistungen.html`)

**Files:**
- Create: `leistungen.html`

**Interfaces:**
- Consumes: same shared assets as Task 4, plus `images/lion.jpg`, `images/elephants-eagle.jpg`, `images/rhino.jpg`.
- Produces: `leistungen.html`, the target of every other DE page's "Leistungen" nav link.

- [ ] **Step 1: Run the validator to confirm it fails**

Run: `python3 tests/validate_page.py leistungen.html --lang de --title-contains "Leistungen"`
Expected: `FAIL` — file not found

- [ ] **Step 2: Write the page**

Same shared `<head>`/`<header>`/`<footer>` pattern as Task 5 (with "Leistungen" highlighted in nav instead of "Über mich"). `<title>`/`<meta description>`:

```html
<title>Leistungen — Hope through Lenses</title>
<meta name="description" content="Wissenschaftlich fundierte Strategie, moderne Technologien wie KI und internationale Führungserfahrung — so vergrößern wir gemeinsam die Wirkung eurer Organisation.">
```

Content between `</header>` and `<footer>`:

```html
<section class="pt-14 pb-10 md:pt-20 md:pb-14 px-6 md:px-16 max-w-2xl">
  <span class="text-sm font-semibold tracking-wide uppercase text-primary">Leistungen</span>
  <h1 class="font-heading font-medium text-3xl md:text-4xl leading-tight text-accent mt-4">So vergrößern wir gemeinsam eure Wirkung</h1>
  <p class="text-base leading-relaxed text-ink/90 mt-5">Kein fertiges Patentrezept, sondern drei Werkzeuge, die ich je nach eurer Situation gemeinsam mit euch einsetze — als Partner, der mitentwickelt, nicht als Berater, der liefert und wieder geht.</p>
</section>

<section class="px-6 md:px-16 pb-16 md:pb-24 grid grid-cols-1 md:grid-cols-3 gap-6 md:gap-8">
  <div class="flex flex-col rounded-xl overflow-hidden border border-black/10 shadow-sm">
    <img src="images/lion.jpg" alt="Löwe im Nahporträt mit direktem Blickkontakt" class="h-48 w-full object-cover object-[50%_32%]">
    <div class="p-6 flex flex-col gap-3">
      <h2 class="font-heading font-medium text-xl">Wissenschaftlich fundierte Strategie</h2>
      <p class="text-sm leading-relaxed text-ink/80">Entscheidungen, die auf Evidenz beruhen statt auf Trends: gemeinsam analysieren wir, wo eure Organisation heute steht, welche Maßnahmen nachweislich wirken, und priorisieren die Schritte, die den größten Unterschied für Tiere, Natur und Menschen vor Ort machen.</p>
    </div>
  </div>
  <div class="flex flex-col rounded-xl overflow-hidden border border-black/10 shadow-sm">
    <img src="images/elephants-eagle.jpg" alt="Elefantenherde am Wasser mit einem fliegenden Schreiseeadler" class="h-48 w-full object-cover">
    <div class="p-6 flex flex-col gap-3">
      <h2 class="font-heading font-medium text-xl">Moderne Technologie, als Werkzeug</h2>
      <p class="text-sm leading-relaxed text-ink/80">KI ist kein Selbstzweck, sondern ein Hebel: für mehr Reichweite in eurer Kommunikation, effizientere Prozesse im Alltag und bessere Entscheidungsgrundlagen — eingeführt so, dass euer Team es versteht und selbst weiterträgt.</p>
    </div>
  </div>
  <div class="flex flex-col rounded-xl overflow-hidden border border-black/10 shadow-sm">
    <img src="images/rhino.jpg" alt="Spitzmaulnashorn im dichten Gebüsch" class="h-48 w-full object-cover">
    <div class="p-6 flex flex-col gap-3">
      <h2 class="font-heading font-medium text-xl">Internationale Führungserfahrung</h2>
      <p class="text-sm leading-relaxed text-ink/80">Jahre in internationalen Executive-Rollen bedeuten: ich weiß, wie man Teams über Kulturen und Zeitzonen hinweg führt, Organisationen strukturiert und ambitionierte Vorhaben tatsächlich zum Abschluss bringt — Erfahrung, die ich unmittelbar in eure Organisation einbringe.</p>
    </div>
  </div>
</section>

<section class="px-6 md:px-16 pb-16 md:pb-24 max-w-prose flex flex-col gap-5">
  <h2 class="font-heading font-medium text-2xl text-accent">Wie wir zusammenarbeiten</h2>
  <p class="text-base leading-relaxed text-ink/90">Jede Zusammenarbeit beginnt mit Zuhören: Was funktioniert bei euch bereits gut? Wo fehlen Ressourcen, nicht guter Wille? Aus diesem Gespräch entsteht ein konkreter, realistischer erster Schritt — kein hundertseitiges Strategiepapier, das in der Schublade landet. Ich verspreche keine Wunder und keine Patentlösungen. Wenn etwas für eure Organisation nicht passt, sage ich das offen.</p>
  <a href="kontakt.html" class="mt-1 text-sm font-semibold text-primary inline-flex items-center gap-1.5">Lasst uns über eure Situation sprechen →</a>
</section>
```

- [ ] **Step 3: Run the validator to confirm it passes**

Run: `python3 tests/validate_page.py leistungen.html --lang de --title-contains "Leistungen"`
Expected: `OK`

- [ ] **Step 4: Manually verify in browser at 390px and 1280px widths**

- [ ] **Step 5: Commit**

```bash
git add leistungen.html
git commit -m "Add DE Leistungen page"
```

---

### Task 7: DE Geschichten (`geschichten.html`)

**Files:**
- Create: `geschichten.html`

**Interfaces:**
- Consumes: same shared assets as Task 4, plus `images/lion.jpg`, `images/leopard-night.jpg`, `images/gecko.jpg`, `images/rhino.jpg`, `images/zebras-sunset.jpg`.
- Produces: `geschichten.html`, the target of every other DE page's "Geschichten" nav link and of the Start page's two "Geschichte entdecken" links.

- [ ] **Step 1: Run the validator to confirm it fails**

Run: `python3 tests/validate_page.py geschichten.html --lang de --title-contains "Geschichten"`
Expected: `FAIL` — file not found

- [ ] **Step 2: Write the page**

Shared `<head>`/`<header>`/`<footer>` as before ("Geschichten" highlighted). `<title>`/`<meta description>`:

```html
<title>Geschichten — Hope through Lenses</title>
<meta name="description" content="Zwei Geschichten aus der Praxis nach dem Hope-Through-The-Lens-Framework: Wonder, Connection, Knowledge, Action, Hope.">
```

Content between `</header>` and `<footer>`:

```html
<section class="pt-14 pb-10 md:pt-20 md:pb-14 px-6 md:px-16 max-w-2xl">
  <span class="text-sm font-semibold tracking-wide uppercase text-primary">Geschichten</span>
  <h1 class="font-heading font-medium text-3xl md:text-4xl leading-tight text-accent mt-4">Hope Through The Lens</h1>
  <p class="text-base leading-relaxed text-ink/90 mt-5">Jede Geschichte hier folgt demselben Weg: vom Moment des Staunens über die persönliche Verbindung und das nötige Wissen bis zur konkreten Handlung — und zurück zur Hoffnung. So entstehen Bilder und Geschichten, die nicht nur informieren, sondern bewegen.</p>
</section>

<article class="px-6 md:px-16 pb-16 md:pb-24 max-w-prose flex flex-col gap-8">
  <h2 class="font-heading font-medium text-2xl text-accent">Der Blick eines Löwen</h2>

  <div class="flex flex-col gap-3">
    <span class="text-xs font-semibold tracking-wide uppercase text-primary">Wonder</span>
    <img src="images/lion.jpg" alt="Löwe im Nahporträt mit direktem Blickkontakt" class="w-full h-[260px] md:h-[360px] rounded-xl object-cover object-[50%_32%]">
    <p class="text-base leading-relaxed text-ink/90">Ein Löwe blickt direkt in die Kamera. Kein Zoo, kein Zaun im Bild — nur dieser eine Moment, in dem sich zwei Blicke treffen und die Zeit kurz stehen bleibt. Genau das ist der Anfang jeder guten Geschichte: der Moment, der einen innehalten lässt.</p>
  </div>

  <div class="flex flex-col gap-3">
    <span class="text-xs font-semibold tracking-wide uppercase text-primary">Connection</span>
    <p class="text-base leading-relaxed text-ink/90">Dieser Löwe lebt in einer Landschaft, die zunehmend von Menschen geteilt wird — Weideland, Siedlungen, Straßen rücken näher an die letzten großen Lebensräume heran. Sein Überleben hängt nicht nur von ihm selbst ab, sondern von den Menschen, Rangern und Organisationen, die täglich zwischen den Bedürfnissen von Mensch und Wildtier vermitteln.</p>
  </div>

  <div class="flex flex-col gap-3">
    <span class="text-xs font-semibold tracking-wide uppercase text-primary">Knowledge</span>
    <img src="images/leopard-night.jpg" alt="Leopard nachts auf einem Ast" class="w-full h-[220px] md:h-[300px] rounded-xl object-cover">
    <p class="text-base leading-relaxed text-ink/90">Großkatzen wie Löwe und Leopard brauchen große, zusammenhängende Reviere, um genug Beute zu finden und sich fortzupflanzen. Zerschneiden Straßen und Zäune diese Reviere in immer kleinere Inseln, sinkt die genetische Vielfalt, und Konflikte mit Menschen und Nutztieren nehmen zu — ein Muster, das sich weltweit in schrumpfenden Wildtierpopulationen zeigt.</p>
  </div>

  <div class="flex flex-col gap-3">
    <span class="text-xs font-semibold tracking-wide uppercase text-primary">Action</span>
    <p class="text-base leading-relaxed text-ink/90">Wirksamer Schutz beginnt mit guten Daten: wo genau bewegen sich die Tiere, wo entstehen Konflikte, welche Korridore verbinden Lebensräume noch miteinander? Genau hier setzt meine Arbeit an — wissenschaftlich fundierte Analysen, die Organisationen vor Ort in konkrete, priorisierte Maßnahmen übersetzen, statt in weitere Studien, die niemand umsetzt.</p>
  </div>

  <div class="flex flex-col gap-3">
    <span class="text-xs font-semibold tracking-wide uppercase text-primary">Hope</span>
    <p class="text-base leading-relaxed text-ink/90">Es gibt keine einfache Lösung — aber es gibt engagierte Menschen, Organisationen und mittlerweile auch bessere Werkzeuge, die gemeinsam echten Unterschied machen. Jeder erhaltene Korridor, jedes entschärfte Konflikt ist ein Schritt, der zählt.</p>
  </div>
</article>

<article class="px-6 md:px-16 pb-16 md:pb-24 max-w-prose flex flex-col gap-8 border-t border-black/10 pt-16 md:pt-24">
  <h2 class="font-heading font-medium text-2xl text-accent">Wüste und Wandel</h2>

  <div class="flex flex-col gap-3">
    <span class="text-xs font-semibold tracking-wide uppercase text-primary">Wonder</span>
    <img src="images/gecko.jpg" alt="Wüstengecko im Nahporträt auf Sand" class="w-full h-[260px] md:h-[360px] rounded-xl object-cover">
    <p class="text-base leading-relaxed text-ink/90">Ein Wüstengecko, kaum größer als ein Finger, mit Augen wie kleine Kunstwerke — mitten in einer Landschaft, die auf den ersten Blick leer wirkt. Wer genau hinschaut, sieht: diese Wüste ist voller Leben.</p>
  </div>

  <div class="flex flex-col gap-3">
    <span class="text-xs font-semibold tracking-wide uppercase text-primary">Connection</span>
    <img src="images/rhino.jpg" alt="Spitzmaulnashorn im dichten Gebüsch" class="w-full h-[220px] md:h-[300px] rounded-xl object-cover">
    <p class="text-base leading-relaxed text-ink/90">Derselbe Lebensraum, der diesem winzigen Gecko Schutz bietet, ist auch Heimat des vom Aussterben bedrohten Spitzmaulnashorns. Zwei völlig unterschiedliche Tiere, ein gemeinsames Schicksal: Ihr Überleben hängt an denselben intakten, unzerschnittenen Landschaften.</p>
  </div>

  <div class="flex flex-col gap-3">
    <span class="text-xs font-semibold tracking-wide uppercase text-primary">Knowledge</span>
    <p class="text-base leading-relaxed text-ink/90">Trockengebiete gelten oft als wenig schützenswert, weil sie weniger spektakulär wirken als Regenwald oder Savanne — dabei beherbergen sie hochspezialisierte, oft endemische Arten, die es nirgendwo sonst gibt. Wilderei, Wasserknappheit und ausbleibender Regen durch den Klimawandel setzen diesen Lebensräumen zusätzlich zu.</p>
  </div>

  <div class="flex flex-col gap-3">
    <span class="text-xs font-semibold tracking-wide uppercase text-primary">Action</span>
    <img src="images/zebras-sunset.jpg" alt="Zebraherde bei Sonnenuntergang in der Savanne" class="w-full h-[220px] md:h-[300px] rounded-xl object-cover">
    <p class="text-base leading-relaxed text-ink/90">Organisationen vor Ort brauchen vor allem eines: verlässliche Unterstützung, um Anti-Wilderei-Einheiten, Monitoring und Aufklärungsarbeit langfristig zu finanzieren, statt von Projekt zu Projekt zu hangeln. Genau dabei helfe ich — mit Strategie, die auf Kontinuität statt auf einmalige Kampagnen setzt.</p>
  </div>

  <div class="flex flex-col gap-3">
    <span class="text-xs font-semibold tracking-wide uppercase text-primary">Hope</span>
    <p class="text-base leading-relaxed text-ink/90">Diese Welt ist außergewöhnlich, in jedem noch so kleinen Detail — vom Gecko bis zum Nashorn. Sie ist es wert, geschützt zu werden. Und jede Organisation, jeder Mensch, der sich dafür einsetzt, vergrößert die Chance, dass sie es bleibt.</p>
  </div>
</article>

<section class="px-6 md:px-16 pb-16 md:pb-24">
  <a href="kontakt.html" class="text-sm font-semibold text-primary inline-flex items-center gap-1.5">Lasst uns eure Geschichte gemeinsam erzählen →</a>
</section>
```

- [ ] **Step 3: Run the validator to confirm it passes**

Run: `python3 tests/validate_page.py geschichten.html --lang de --title-contains "Geschichten"`
Expected: `OK`

- [ ] **Step 4: Manually verify in browser at 390px and 1280px widths**

- [ ] **Step 5: Commit**

```bash
git add geschichten.html
git commit -m "Add DE Geschichten page"
```

---

### Task 8: DE Kontakt (`kontakt.html`)

**Files:**
- Create: `kontakt.html`

**Interfaces:**
- Consumes: same shared assets as Task 4.
- Produces: `kontakt.html`, the Netlify-detected form named `kontakt`.

- [ ] **Step 1: Run the validator to confirm it fails**

Run: `python3 tests/validate_page.py kontakt.html --lang de --title-contains "Kontakt" --form`
Expected: `FAIL` — file not found

- [ ] **Step 2: Write the page**

Shared `<head>`/`<header>`/`<footer>` as before ("Kontakt" highlighted). `<title>`/`<meta description>`:

```html
<title>Kontakt — Hope through Lenses</title>
<meta name="description" content="Lasst uns ins Gespräch kommen: wie eure Organisation ihre Wirkung für Tiere, Natur und Planet vergrößern kann.">
```

Content between `</header>` and `<footer>`:

```html
<section class="pt-14 pb-10 md:pt-20 md:pb-14 px-6 md:px-16 max-w-2xl">
  <span class="text-sm font-semibold tracking-wide uppercase text-primary">Kontakt</span>
  <h1 class="font-heading font-medium text-3xl md:text-4xl leading-tight text-accent mt-4">Lass uns gemeinsam ins Gespräch kommen</h1>
  <p class="text-base leading-relaxed text-ink/90 mt-5">Egal ob ihr schon eine konkrete Frage habt oder einfach herausfinden wollt, ob eine Zusammenarbeit für eure Organisation Sinn ergibt — schreibt mir. Ich melde mich persönlich zurück.</p>
</section>

<section class="px-6 md:px-16 pb-16 md:pb-24 max-w-xl">
  <form name="kontakt" method="POST" data-netlify="true" class="flex flex-col gap-5">
    <input type="hidden" name="form-name" value="kontakt">
    <div class="flex flex-col gap-2">
      <label for="name" class="text-sm font-semibold">Name</label>
      <input id="name" name="name" type="text" required class="border border-black/20 rounded-lg px-4 py-3 text-sm">
    </div>
    <div class="flex flex-col gap-2">
      <label for="email" class="text-sm font-semibold">E-Mail</label>
      <input id="email" name="email" type="email" required class="border border-black/20 rounded-lg px-4 py-3 text-sm">
    </div>
    <div class="flex flex-col gap-2">
      <label for="organisation" class="text-sm font-semibold">Organisation</label>
      <input id="organisation" name="organisation" type="text" class="border border-black/20 rounded-lg px-4 py-3 text-sm">
    </div>
    <div class="flex flex-col gap-2">
      <label for="nachricht" class="text-sm font-semibold">Nachricht</label>
      <textarea id="nachricht" name="nachricht" rows="5" required class="border border-black/20 rounded-lg px-4 py-3 text-sm"></textarea>
    </div>
    <button type="submit" class="bg-primary text-paper rounded-lg px-7 py-3.5 font-semibold text-sm w-fit">Nachricht senden</button>
  </form>
  <p class="text-sm text-ink/70 mt-8">Oder direkt per E-Mail: <a href="mailto:troetchris@gmail.com" class="text-primary font-semibold">troetchris@gmail.com</a></p>
</section>
```

- [ ] **Step 3: Run the validator to confirm it passes**

Run: `python3 tests/validate_page.py kontakt.html --lang de --title-contains "Kontakt" --form`
Expected: `OK`

- [ ] **Step 4: Manually verify in browser at 390px and 1280px widths.** Additionally: submit the form once with dummy data on `localhost` and confirm the browser doesn't error before deployment (real Netlify Forms delivery can only be tested after Task 14's deployment).

- [ ] **Step 5: Commit**

```bash
git add kontakt.html
git commit -m "Add DE Kontakt page with Netlify contact form"
```

---

### Task 9: EN Home (`en/index.html`)

**Files:**
- Create: `en/index.html`

**Interfaces:**
- Consumes: `../js/tailwind-config.js`, `../styles.css`, `../js/main.js`, `../images/*.jpg` (note the `../` prefix — this file lives one directory down).
- Produces: `en/index.html`, the target of the DE start page's language switcher and every other EN page's "Home" nav link.

- [ ] **Step 1: Run the validator to confirm it fails**

Run: `python3 tests/validate_page.py en/index.html --lang en --title-contains "Hope through Lenses"`
Expected: `FAIL` — file not found

- [ ] **Step 2: Write the page**

Same structure as Task 4's `index.html`, translated to English, all asset/link paths prefixed with `../` (or, for links to other EN pages, no prefix since they're siblings), `<html lang="en">`, and DE as the langlink target:

```html
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Hope through Lenses — Creating impact together for animals, nature and planet</title>
<meta name="description" content="Evidence-based strategy, AI, and international leadership experience for animal welfare and conservation NGOs. A partner, not a distant consultant.">
<script src="https://cdn.tailwindcss.com"></script>
<script src="../js/tailwind-config.js"></script>
<link rel="stylesheet" href="../styles.css">
</head>
<body class="bg-white text-ink font-body">

<header class="h-22 px-6 md:px-16 flex items-center justify-between border-b border-black/10">
  <a href="index.html" class="font-heading text-xl font-semibold text-accent">Hope through Lenses</a>
  <button id="nav-toggle" aria-expanded="false" aria-controls="nav-menu" class="md:hidden w-9 h-9 flex flex-col justify-center gap-1.5 items-center">
    <span class="w-5 h-0.5 bg-ink"></span>
    <span class="w-5 h-0.5 bg-ink"></span>
    <span class="w-5 h-0.5 bg-ink"></span>
  </button>
  <nav id="nav-menu" class="hidden md:flex md:items-center gap-9 absolute md:static top-22 left-0 right-0 bg-white md:bg-transparent flex-col md:flex-row p-6 md:p-0 border-b md:border-0 border-black/10">
    <a class="navlink py-2 md:py-0 text-sm font-medium text-primary" href="index.html">Home</a>
    <a class="navlink py-2 md:py-0 text-sm font-medium" href="about.html">About</a>
    <a class="navlink py-2 md:py-0 text-sm font-medium" href="services.html">Services</a>
    <a class="navlink py-2 md:py-0 text-sm font-medium" href="stories.html">Stories</a>
    <a class="navlink py-2 md:py-0 text-sm font-medium" href="contact.html">Contact</a>
    <div class="flex items-center gap-1.5 md:ml-3 md:pl-6 md:border-l border-black/10 pt-2 md:pt-0">
      <a class="langlink text-xs font-medium text-black/50" href="../index.html">DE</a>
      <span class="text-xs text-black/30">/</span>
      <span class="text-xs font-semibold text-primary">EN</span>
    </div>
  </nav>
</header>

<section class="relative h-[520px] md:h-[620px] flex items-center overflow-hidden">
  <img src="../images/hero-orangutan.jpg" alt="Young orangutan looking directly into the camera" class="absolute inset-0 w-full h-full object-cover object-[50%_45%]">
  <div class="absolute inset-0 bg-[linear-gradient(270deg,rgba(10,26,24,0.90)_0%,rgba(10,26,24,0.62)_35%,rgba(10,26,24,0.12)_62%)]"></div>
  <div class="relative w-full px-6 md:px-16 flex md:justify-end">
    <div class="max-w-xl flex flex-col items-start md:items-end text-left md:text-right gap-5">
      <span class="text-sm font-semibold tracking-wide uppercase text-secondary">For animals, nature and our planet</span>
      <h1 class="font-heading font-medium text-4xl md:text-5xl leading-tight text-paper">Act together.<br>Create impact together.</h1>
      <p class="text-base md:text-lg leading-relaxed text-paper/90 max-w-md">I bring together passion, scientific expertise, international leadership experience, and modern technology to help NGOs sustainably grow their impact — as a partner, not a distant consultant.</p>
      <div class="flex flex-wrap gap-3.5 mt-2">
        <a href="stories.html" class="bg-secondary text-primary rounded-lg px-7 py-3.5 font-semibold text-sm">Discover my story</a>
        <a href="contact.html" class="border border-white/70 text-paper rounded-lg px-6 py-3 font-semibold text-sm">Get in touch</a>
      </div>
    </div>
  </div>
</section>

<section class="py-16 md:py-24 px-6 md:px-16 flex flex-col md:flex-row gap-12 md:gap-16 items-center bg-secondary/10">
  <div class="flex-1 flex flex-col gap-5">
    <span class="text-sm font-semibold tracking-wide uppercase text-primary">Wonder — the moment that stays</span>
    <h2 class="font-heading font-medium text-3xl leading-snug text-accent">Every species, every protected habitat is a reason to keep going.</h2>
    <p class="text-base leading-relaxed text-ink/90 max-w-prose">As a veterinarian and scientist, I've seen what's possible when knowledge, leadership, and genuine partnership come together. After many rewarding years in my career, I'm grateful for everything I've learned — and it's time to give something back. As a vet, I want to focus on animal welfare and put my skills at the service of animal protection organizations, for greater impact for animals, nature, and our planet.</p>
    <a href="about.html" class="mt-1 text-sm font-semibold text-primary inline-flex items-center gap-1.5">More about my path →</a>
  </div>
  <img src="../images/portrait-mission.jpg" alt="Portrait in the field, with a squirrel monkey on the shoulder" class="flex-1 w-full h-[280px] md:h-[340px] rounded-xl object-cover object-[75%_40%]">
</section>

<section class="py-16 md:py-24 px-6 md:px-16 bg-primary flex flex-col md:flex-row gap-12 md:gap-16 items-center">
  <div class="flex-1 grid grid-cols-2 grid-rows-2 gap-3 h-[280px] md:h-[280px]">
    <img src="../images/gecko.jpg" alt="Close-up portrait of a desert gecko on sand" class="row-span-2 w-full h-full object-cover rounded-xl">
    <img src="../images/rhino.jpg" alt="Black rhinoceros in dense brush" class="w-full h-full object-cover rounded-xl">
    <img src="../images/zebras-sunset.jpg" alt="Herd of zebras at sunset on the savanna" class="w-full h-full object-cover rounded-xl">
  </div>
  <div class="flex-1 flex flex-col gap-5">
    <span class="text-sm font-semibold tracking-wide uppercase text-secondary">Hope Through The Lens</span>
    <h2 class="font-heading font-medium text-3xl leading-snug text-paper">Images that move people — and move them to act.</h2>
    <p class="text-base leading-relaxed text-paper/85 max-w-prose">Alongside strategy and science, I bring my photographic work: authentic, emotional, high-quality images — never stock photos, never staged scenes. They show the animal, the habitat, and the people protecting it, increasing the impact and reach of your communications.</p>
    <a href="stories.html" class="mt-1 text-sm font-semibold text-secondary inline-flex items-center gap-1.5">See the photographic work →</a>
  </div>
</section>

<section class="py-16 md:py-24 px-6 md:px-16">
  <h2 class="font-heading font-medium text-2xl md:text-3xl mb-10">How we grow your impact together</h2>
  <div class="grid grid-cols-1 md:grid-cols-3 gap-6 md:gap-8">
    <a href="about.html" class="flex flex-col rounded-xl overflow-hidden border border-black/10 shadow-sm">
      <img src="../images/shelter-dog.jpg" alt="Puppy looking through the bars of a shelter enclosure" class="h-44 w-full object-cover object-[50%_35%]">
      <div class="p-6 flex flex-col gap-2.5">
        <span class="text-xs font-semibold tracking-wide uppercase text-accent">About me</span>
        <h3 class="font-heading font-medium text-lg">Why this mission drives me</h3>
        <p class="text-sm leading-relaxed text-ink/70">From veterinarian to international executive — my story, and what drives me.</p>
      </div>
    </a>
    <a href="services.html" class="flex flex-col rounded-xl overflow-hidden border border-black/10 shadow-sm">
      <img src="../images/lion.jpg" alt="Close-up portrait of a lion in direct eye contact" class="h-44 w-full object-cover object-[50%_32%]">
      <div class="p-6 flex flex-col gap-2.5">
        <span class="text-xs font-semibold tracking-wide uppercase text-primary">Services</span>
        <h3 class="font-heading font-medium text-lg">How we grow your impact</h3>
        <p class="text-sm leading-relaxed text-ink/70">Evidence-based strategy, AI, and leadership experience for your organization.</p>
      </div>
    </a>
    <a href="stories.html" class="flex flex-col rounded-xl overflow-hidden border border-black/10 shadow-sm">
      <img src="../images/leopard-night.jpg" alt="Leopard on a branch at night" class="h-44 w-full object-cover">
      <div class="p-6 flex flex-col gap-2.5">
        <span class="text-xs font-semibold tracking-wide uppercase text-secondary bg-primary px-2 py-0.5 rounded w-fit">Stories</span>
        <h3 class="font-heading font-medium text-lg">Wonder → Connection → Hope</h3>
        <p class="text-sm leading-relaxed text-ink/70">Real moments from the field — where science meets hope.</p>
      </div>
    </a>
  </div>
</section>

<section class="py-14 md:py-18 px-6 md:px-16 bg-accent flex flex-col md:flex-row items-center justify-between gap-8">
  <h2 class="font-heading font-medium text-xl md:text-2xl text-paper max-w-lg">Let's find out together how your organization can grow its impact.</h2>
  <a href="contact.html" class="bg-secondary text-primary rounded-lg px-7 py-3.5 font-semibold text-sm whitespace-nowrap">Schedule a call</a>
</section>

<footer class="py-12 px-6 md:px-16 bg-[#0B120F] flex flex-col md:flex-row items-center justify-between gap-6">
  <span class="font-heading text-base text-paper">Hope through Lenses</span>
  <div class="flex flex-wrap justify-center gap-6">
    <a href="about.html" class="text-sm text-paper/65">About</a>
    <a href="services.html" class="text-sm text-paper/65">Services</a>
    <a href="stories.html" class="text-sm text-paper/65">Stories</a>
    <a href="contact.html" class="text-sm text-paper/65">Contact</a>
  </div>
  <div class="flex gap-1.5">
    <a class="langlink text-sm text-paper/50" href="../index.html">DE</a>
    <span class="text-sm text-paper/30">/</span>
    <span class="text-sm font-semibold text-secondary">EN</span>
  </div>
</footer>

<script src="../js/main.js"></script>
</body>
</html>
```

- [ ] **Step 3: Run the validator to confirm it passes**

Run: `python3 tests/validate_page.py en/index.html --lang en --title-contains "Hope through Lenses"`
Expected: `OK`

- [ ] **Step 4: Manually verify in browser at 390px and 1280px widths, and click the DE langlink to confirm it lands back on the root `index.html`**

- [ ] **Step 5: Commit**

```bash
git add en/index.html
git commit -m "Add EN home page"
```

---

### Task 10: EN About (`en/about.html`)

**Files:**
- Create: `en/about.html`

**Interfaces:**
- Consumes: same shared assets as Task 9.
- Produces: `en/about.html`, the language-switch target of DE `ueber-mich.html`.

- [ ] **Step 1: Run the validator to confirm it fails**

Run: `python3 tests/validate_page.py en/about.html --lang en --title-contains "About"`
Expected: `FAIL` — file not found

- [ ] **Step 2: Write the page**

Same shared `<head>`/`<header>`/`<footer>` as Task 9 ("About" highlighted in nav, langlink target `../ueber-mich.html`). `<title>`/`<meta description>`:

```html
<title>About — Hope through Lenses</title>
<meta name="description" content="From veterinarian and scientist to international executive: why I now put my experience to work for animal welfare NGOs.">
```

Content between `</header>` and `<footer>`:

```html
<section class="pt-14 pb-10 md:pt-20 md:pb-14 px-6 md:px-16">
  <span class="text-sm font-semibold tracking-wide uppercase text-primary">About me</span>
  <h1 class="font-heading font-medium text-3xl md:text-4xl leading-tight text-accent mt-4 max-w-2xl">From veterinarian to partner for international NGOs</h1>
</section>

<section class="px-6 md:px-16 pb-12 md:pb-16">
  <img src="../images/shelter-dog.jpg" alt="Puppy looking through the bars of a shelter enclosure" class="w-full h-[260px] md:h-[420px] rounded-xl object-cover object-[50%_35%]">
</section>

<section class="px-6 md:px-16 pb-16 md:pb-24 flex flex-col gap-6 max-w-prose">
  <p class="text-base leading-relaxed text-ink/90">My career began at the operating table: as a veterinarian, I learned to make clear decisions under pressure, and that every single life you care for matters. From clinical practice, my path led through science into international leadership roles — where I learned how to build organizations, lead teams across borders, and actually see ambitious projects through to completion.</p>
  <p class="text-base leading-relaxed text-ink/90">For a long time, these three worlds — veterinary medicine, science, international leadership — ran side by side, separately. Today I bring them together. After many rewarding years in my career, I'm grateful for everything I've had the chance to learn, and it's time to give something back. Not as a retirement project, but as what drives me most: helping animals, nature, and our planet with exactly the tools I've built over decades.</p>
  <p class="text-base leading-relaxed text-ink/90">That's why I work with animal welfare and conservation organizations today — not as a distant outside consultant, but as a partner who listens, understands, and develops and implements solutions together. Evidence-based, honest even when something isn't the right fit, and always aimed at creating real impact for animals, nature, and our planet.</p>
  <a href="services.html" class="mt-2 text-sm font-semibold text-primary inline-flex items-center gap-1.5">What that looks like in practice →</a>
</section>
```

- [ ] **Step 3: Run the validator to confirm it passes**

Run: `python3 tests/validate_page.py en/about.html --lang en --title-contains "About"`
Expected: `OK`

- [ ] **Step 4: Manually verify in browser at 390px and 1280px widths**

- [ ] **Step 5: Commit**

```bash
git add en/about.html
git commit -m "Add EN about page"
```

---

### Task 11: EN Services (`en/services.html`)

**Files:**
- Create: `en/services.html`

**Interfaces:**
- Consumes: same shared assets as Task 9.
- Produces: `en/services.html`, the language-switch target of DE `leistungen.html`.

- [ ] **Step 1: Run the validator to confirm it fails**

Run: `python3 tests/validate_page.py en/services.html --lang en --title-contains "Services"`
Expected: `FAIL` — file not found

- [ ] **Step 2: Write the page**

Same shared `<head>`/`<header>`/`<footer>` as Task 9 ("Services" highlighted, langlink target `../leistungen.html`). `<title>`/`<meta description>`:

```html
<title>Services — Hope through Lenses</title>
<meta name="description" content="Evidence-based strategy, modern technology like AI, and international leadership experience — how we grow your organization's impact together.">
```

Content between `</header>` and `<footer>`:

```html
<section class="pt-14 pb-10 md:pt-20 md:pb-14 px-6 md:px-16 max-w-2xl">
  <span class="text-sm font-semibold tracking-wide uppercase text-primary">Services</span>
  <h1 class="font-heading font-medium text-3xl md:text-4xl leading-tight text-accent mt-4">How we grow your impact together</h1>
  <p class="text-base leading-relaxed text-ink/90 mt-5">Not a fixed package, but three tools I apply together with you, depending on your situation — as a partner who co-develops, not a consultant who delivers and leaves.</p>
</section>

<section class="px-6 md:px-16 pb-16 md:pb-24 grid grid-cols-1 md:grid-cols-3 gap-6 md:gap-8">
  <div class="flex flex-col rounded-xl overflow-hidden border border-black/10 shadow-sm">
    <img src="../images/lion.jpg" alt="Close-up portrait of a lion in direct eye contact" class="h-48 w-full object-cover object-[50%_32%]">
    <div class="p-6 flex flex-col gap-3">
      <h2 class="font-heading font-medium text-xl">Evidence-based strategy</h2>
      <p class="text-sm leading-relaxed text-ink/80">Decisions grounded in evidence, not trends: together we analyze where your organization stands today, which measures demonstrably work, and prioritize the steps that make the biggest difference for animals, nature, and the people on the ground.</p>
    </div>
  </div>
  <div class="flex flex-col rounded-xl overflow-hidden border border-black/10 shadow-sm">
    <img src="../images/elephants-eagle.jpg" alt="Herd of elephants by the water with a fish eagle in flight" class="h-48 w-full object-cover">
    <div class="p-6 flex flex-col gap-3">
      <h2 class="font-heading font-medium text-xl">Modern technology, as a tool</h2>
      <p class="text-sm leading-relaxed text-ink/80">AI isn't an end in itself, it's a lever: for greater reach in your communications, more efficient day-to-day processes, and better-informed decisions — introduced in a way your team understands and can carry forward on its own.</p>
    </div>
  </div>
  <div class="flex flex-col rounded-xl overflow-hidden border border-black/10 shadow-sm">
    <img src="../images/rhino.jpg" alt="Black rhinoceros in dense brush" class="h-48 w-full object-cover">
    <div class="p-6 flex flex-col gap-3">
      <h2 class="font-heading font-medium text-xl">International leadership experience</h2>
      <p class="text-sm leading-relaxed text-ink/80">Years in international executive roles mean I know how to lead teams across cultures and time zones, structure organizations, and actually see ambitious projects through — experience I bring directly into your organization.</p>
    </div>
  </div>
</section>

<section class="px-6 md:px-16 pb-16 md:pb-24 max-w-prose flex flex-col gap-5">
  <h2 class="font-heading font-medium text-2xl text-accent">How we work together</h2>
  <p class="text-base leading-relaxed text-ink/90">Every collaboration starts with listening: what's already working well for you? Where are resources missing, not goodwill? From that conversation comes a concrete, realistic first step — not a hundred-page strategy document that ends up in a drawer. I don't promise miracles or one-size-fits-all solutions. If something isn't the right fit for your organization, I'll say so, openly.</p>
  <a href="contact.html" class="mt-1 text-sm font-semibold text-primary inline-flex items-center gap-1.5">Let's talk about your situation →</a>
</section>
```

- [ ] **Step 3: Run the validator to confirm it passes**

Run: `python3 tests/validate_page.py en/services.html --lang en --title-contains "Services"`
Expected: `OK`

- [ ] **Step 4: Manually verify in browser at 390px and 1280px widths**

- [ ] **Step 5: Commit**

```bash
git add en/services.html
git commit -m "Add EN services page"
```

---

### Task 12: EN Stories (`en/stories.html`)

**Files:**
- Create: `en/stories.html`

**Interfaces:**
- Consumes: same shared assets as Task 9.
- Produces: `en/stories.html`, the language-switch target of DE `geschichten.html`.

- [ ] **Step 1: Run the validator to confirm it fails**

Run: `python3 tests/validate_page.py en/stories.html --lang en --title-contains "Stories"`
Expected: `FAIL` — file not found

- [ ] **Step 2: Write the page**

Same shared `<head>`/`<header>`/`<footer>` as Task 9 ("Stories" highlighted, langlink target `../geschichten.html`). `<title>`/`<meta description>`:

```html
<title>Stories — Hope through Lenses</title>
<meta name="description" content="Two stories from the field, told through the Hope Through The Lens framework: Wonder, Connection, Knowledge, Action, Hope.">
```

Content between `</header>` and `<footer>` — direct translation of Task 7's two stories, same image references (with `../` prefix), same five-step structure per story:

```html
<section class="pt-14 pb-10 md:pt-20 md:pb-14 px-6 md:px-16 max-w-2xl">
  <span class="text-sm font-semibold tracking-wide uppercase text-primary">Stories</span>
  <h1 class="font-heading font-medium text-3xl md:text-4xl leading-tight text-accent mt-4">Hope Through The Lens</h1>
  <p class="text-base leading-relaxed text-ink/90 mt-5">Every story here follows the same path: from a moment of wonder, through personal connection and the knowledge you need, to concrete action — and back to hope. That's how images and stories emerge that don't just inform, but move people.</p>
</section>

<article class="px-6 md:px-16 pb-16 md:pb-24 max-w-prose flex flex-col gap-8">
  <h2 class="font-heading font-medium text-2xl text-accent">A lion's gaze</h2>

  <div class="flex flex-col gap-3">
    <span class="text-xs font-semibold tracking-wide uppercase text-primary">Wonder</span>
    <img src="../images/lion.jpg" alt="Close-up portrait of a lion in direct eye contact" class="w-full h-[260px] md:h-[360px] rounded-xl object-cover object-[50%_32%]">
    <p class="text-base leading-relaxed text-ink/90">A lion looks straight into the camera. No zoo, no fence in frame — just this one moment where two gazes meet and time seems to pause. That's the beginning of every good story: the moment that makes you stop.</p>
  </div>

  <div class="flex flex-col gap-3">
    <span class="text-xs font-semibold tracking-wide uppercase text-primary">Connection</span>
    <p class="text-base leading-relaxed text-ink/90">This lion lives in a landscape increasingly shared with people — grazing land, settlements, and roads pressing closer to the last large habitats. His survival depends not only on himself, but on the people, rangers, and organizations who mediate daily between the needs of people and wildlife.</p>
  </div>

  <div class="flex flex-col gap-3">
    <span class="text-xs font-semibold tracking-wide uppercase text-primary">Knowledge</span>
    <img src="../images/leopard-night.jpg" alt="Leopard on a branch at night" class="w-full h-[220px] md:h-[300px] rounded-xl object-cover">
    <p class="text-base leading-relaxed text-ink/90">Big cats like lions and leopards need large, connected territories to find enough prey and reproduce. When roads and fences cut these territories into ever-smaller islands, genetic diversity drops and conflict with people and livestock rises — a pattern seen worldwide in shrinking wildlife populations.</p>
  </div>

  <div class="flex flex-col gap-3">
    <span class="text-xs font-semibold tracking-wide uppercase text-primary">Action</span>
    <p class="text-base leading-relaxed text-ink/90">Effective protection starts with good data: exactly where do animals move, where does conflict arise, which corridors still connect habitats? That's exactly where my work comes in — evidence-based analysis that translates into concrete, prioritized action for organizations on the ground, instead of yet another study nobody implements.</p>
  </div>

  <div class="flex flex-col gap-3">
    <span class="text-xs font-semibold tracking-wide uppercase text-primary">Hope</span>
    <p class="text-base leading-relaxed text-ink/90">There's no simple fix — but there are dedicated people, organizations, and now better tools that together make a real difference. Every preserved corridor, every defused conflict is a step that counts.</p>
  </div>
</article>

<article class="px-6 md:px-16 pb-16 md:pb-24 max-w-prose flex flex-col gap-8 border-t border-black/10 pt-16 md:pt-24">
  <h2 class="font-heading font-medium text-2xl text-accent">Desert and change</h2>

  <div class="flex flex-col gap-3">
    <span class="text-xs font-semibold tracking-wide uppercase text-primary">Wonder</span>
    <img src="../images/gecko.jpg" alt="Close-up portrait of a desert gecko on sand" class="w-full h-[260px] md:h-[360px] rounded-xl object-cover">
    <p class="text-base leading-relaxed text-ink/90">A desert gecko, barely bigger than a finger, with eyes like tiny works of art — in a landscape that at first glance looks empty. Look closely, though, and this desert is full of life.</p>
  </div>

  <div class="flex flex-col gap-3">
    <span class="text-xs font-semibold tracking-wide uppercase text-primary">Connection</span>
    <img src="../images/rhino.jpg" alt="Black rhinoceros in dense brush" class="w-full h-[220px] md:h-[300px] rounded-xl object-cover">
    <p class="text-base leading-relaxed text-ink/90">The same habitat that shelters this tiny gecko is also home to the critically endangered black rhino. Two completely different animals, one shared fate: their survival depends on the same intact, unfragmented landscapes.</p>
  </div>

  <div class="flex flex-col gap-3">
    <span class="text-xs font-semibold tracking-wide uppercase text-primary">Knowledge</span>
    <p class="text-base leading-relaxed text-ink/90">Drylands are often seen as less worth protecting because they look less spectacular than rainforest or savanna — yet they hold highly specialized, often endemic species found nowhere else. Poaching, water scarcity, and reduced rainfall due to climate change put additional pressure on these habitats.</p>
  </div>

  <div class="flex flex-col gap-3">
    <span class="text-xs font-semibold tracking-wide uppercase text-primary">Action</span>
    <img src="../images/zebras-sunset.jpg" alt="Herd of zebras at sunset on the savanna" class="w-full h-[220px] md:h-[300px] rounded-xl object-cover">
    <p class="text-base leading-relaxed text-ink/90">Organizations on the ground need one thing above all: reliable support to fund anti-poaching units, monitoring, and community education long-term, rather than moving from project to project. That's exactly what I help with — strategy built for continuity rather than one-off campaigns.</p>
  </div>

  <div class="flex flex-col gap-3">
    <span class="text-xs font-semibold tracking-wide uppercase text-primary">Hope</span>
    <p class="text-base leading-relaxed text-ink/90">This world is extraordinary, down to the smallest detail — from the gecko to the rhino. It's worth protecting. And every organization, every person who stands up for it, increases the chance that it stays that way.</p>
  </div>
</article>

<section class="px-6 md:px-16 pb-16 md:pb-24">
  <a href="contact.html" class="text-sm font-semibold text-primary inline-flex items-center gap-1.5">Let's tell your story together →</a>
</section>
```

- [ ] **Step 3: Run the validator to confirm it passes**

Run: `python3 tests/validate_page.py en/stories.html --lang en --title-contains "Stories"`
Expected: `OK`

- [ ] **Step 4: Manually verify in browser at 390px and 1280px widths**

- [ ] **Step 5: Commit**

```bash
git add en/stories.html
git commit -m "Add EN stories page"
```

---

### Task 13: EN Contact (`en/contact.html`)

**Files:**
- Create: `en/contact.html`

**Interfaces:**
- Consumes: same shared assets as Task 9.
- Produces: `en/contact.html`, the language-switch target of DE `kontakt.html`, and a second Netlify-detected form named `contact-en`.

- [ ] **Step 1: Run the validator to confirm it fails**

Run: `python3 tests/validate_page.py en/contact.html --lang en --title-contains "Contact" --form`
Expected: `FAIL` — file not found

- [ ] **Step 2: Write the page**

Same shared `<head>`/`<header>`/`<footer>` as Task 9 ("Contact" highlighted, langlink target `../kontakt.html`). `<title>`/`<meta description>`:

```html
<title>Contact — Hope through Lenses</title>
<meta name="description" content="Let's talk: how your organization can grow its impact for animals, nature, and our planet.">
```

Content between `</header>` and `<footer>` — note the form is named `contact-en` (distinct from the DE form's `kontakt`, so Netlify treats them as two separate form inboxes and it's obvious in the Netlify dashboard which language a submission came from):

```html
<section class="pt-14 pb-10 md:pt-20 md:pb-14 px-6 md:px-16 max-w-2xl">
  <span class="text-sm font-semibold tracking-wide uppercase text-primary">Contact</span>
  <h1 class="font-heading font-medium text-3xl md:text-4xl leading-tight text-accent mt-4">Let's start a conversation</h1>
  <p class="text-base leading-relaxed text-ink/90 mt-5">Whether you already have a specific question or just want to find out if working together makes sense for your organization — reach out. I'll get back to you personally.</p>
</section>

<section class="px-6 md:px-16 pb-16 md:pb-24 max-w-xl">
  <form name="contact-en" method="POST" data-netlify="true" class="flex flex-col gap-5">
    <input type="hidden" name="form-name" value="contact-en">
    <div class="flex flex-col gap-2">
      <label for="name" class="text-sm font-semibold">Name</label>
      <input id="name" name="name" type="text" required class="border border-black/20 rounded-lg px-4 py-3 text-sm">
    </div>
    <div class="flex flex-col gap-2">
      <label for="email" class="text-sm font-semibold">Email</label>
      <input id="email" name="email" type="email" required class="border border-black/20 rounded-lg px-4 py-3 text-sm">
    </div>
    <div class="flex flex-col gap-2">
      <label for="organisation" class="text-sm font-semibold">Organization</label>
      <input id="organisation" name="organisation" type="text" class="border border-black/20 rounded-lg px-4 py-3 text-sm">
    </div>
    <div class="flex flex-col gap-2">
      <label for="message" class="text-sm font-semibold">Message</label>
      <textarea id="message" name="message" rows="5" required class="border border-black/20 rounded-lg px-4 py-3 text-sm"></textarea>
    </div>
    <button type="submit" class="bg-primary text-paper rounded-lg px-7 py-3.5 font-semibold text-sm w-fit">Send message</button>
  </form>
  <p class="text-sm text-ink/70 mt-8">Or directly by email: <a href="mailto:troetchris@gmail.com" class="text-primary font-semibold">troetchris@gmail.com</a></p>
</section>
```

- [ ] **Step 3: Run the validator to confirm it passes**

Run: `python3 tests/validate_page.py en/contact.html --lang en --title-contains "Contact" --form`
Expected: `OK`

- [ ] **Step 4: Manually verify in browser at 390px and 1280px widths**

- [ ] **Step 5: Commit**

```bash
git add en/contact.html
git commit -m "Add EN contact page with Netlify contact form"
```

---

### Task 14: Full-site check and Netlify deployment

**Files:**
- None created; this task wires up hosting and does the final cross-page verification the spec's own Testing section calls for.

**Interfaces:**
- Consumes: all 10 pages plus shared assets.
- Produces: a live Netlify URL (a `*.netlify.app` subdomain — no custom domain per the spec's explicit scope).

- [ ] **Step 1: Run the validator against all 10 pages in one pass**

```bash
python3 tests/validate_page.py index.html --lang de --title-contains "Hope through Lenses" && \
python3 tests/validate_page.py ueber-mich.html --lang de --title-contains "Über mich" && \
python3 tests/validate_page.py leistungen.html --lang de --title-contains "Leistungen" && \
python3 tests/validate_page.py geschichten.html --lang de --title-contains "Geschichten" && \
python3 tests/validate_page.py kontakt.html --lang de --title-contains "Kontakt" --form && \
python3 tests/validate_page.py en/index.html --lang en --title-contains "Hope through Lenses" && \
python3 tests/validate_page.py en/about.html --lang en --title-contains "About" && \
python3 tests/validate_page.py en/services.html --lang en --title-contains "Services" && \
python3 tests/validate_page.py en/stories.html --lang en --title-contains "Stories" && \
python3 tests/validate_page.py en/contact.html --lang en --title-contains "Contact" --form && \
echo "ALL 10 PAGES PASS"
```
Expected: `ALL 10 PAGES PASS`

- [ ] **Step 2: Manually click through every nav link and every language-switch link on every page**

Starting from `index.html`, click all 5 nav links, confirm each loads the right page; on each page click the EN/DE switcher and confirm it lands on the matching-content page in the other language (not just the other language's home page). Repeat starting from `en/index.html`.

- [ ] **Step 3: Sign in to (or create) a Netlify account and connect this Git repository**

This is a manual step in the Netlify web UI, done by the user (it requires their own account credentials, which Claude cannot enter): New site from Git → select this repository → build command: none (leave blank) → publish directory: `.` (repo root) → Deploy site.

- [ ] **Step 4: After the first deploy, verify Netlify detected both forms**

In the Netlify dashboard, open the site → Forms. Expected: two forms listed, named `kontakt` and `contact-en`.

- [ ] **Step 5: Submit a real test message through both `kontakt.html` and `en/contact.html` on the live URL**

Expected: each submission redirects to Netlify's default success page and appears within a minute under Forms → (form name) → Submissions in the dashboard.

- [ ] **Step 6: Commit the Netlify site ID/URL to memory for next steps**

No git commit needed for this step (nothing changed in the repo) — just note the live `*.netlify.app` URL for the next conversation, since a custom domain and further content (e.g. the site's second sub-project) are out of scope here per the spec.

---

## Self-Review Notes

- **Spec coverage:** all 5 page types × 2 languages (Tasks 4–13), shared header/nav/footer with language switcher (every page task), Tailwind-based color/type system from the brand palette (Task 3), mobile-first responsive classes throughout, Netlify Forms wiring (Tasks 8, 13), image alt text and SEO title/description on every page (validator-enforced), Netlify hosting/deployment (Task 14). Out-of-scope items (blog, more languages, CMS, own domain, analytics) are intentionally absent — confirmed no task touches them.
- **Placeholder scan:** no "TBD"/"Lorem ipsum"/"fill in later" anywhere in the HTML content; every page has real, finished copy.
- **Type consistency:** the validator's CLI flags (`--lang`, `--title-contains`, `--form`) and class-name contracts (`navlink`, `langlink`, `form-name` hidden input matching the form's `name`) are identical across all 10 page tasks.
- **Review Focus coverage:** mobile nav toggle is exercised manually in Task 3 Step 4 and again per-page; Netlify form wiring is checked structurally by the validator's `--form` assertions in Tasks 8 and 13, and end-to-end in Task 14 Steps 4–5; language-switcher correctness is checked per-page in Step 4 of Tasks 4–13 and exhaustively in Task 14 Step 2; title/meta-description uniqueness is enforced by the validator's `--title-contains` argument differing per task; image alt text is enforced structurally by the validator on every page.
