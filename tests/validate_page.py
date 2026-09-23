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
