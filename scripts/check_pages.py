"""Gate the landing pages against the limits that actually bite.

RSA headlines are capped at 30 characters and descriptions at 90; heroText longer
than the template's proven range overflows the hero image on mobile and turns
white-on-cream. Pages carrying their own article must render it high.
"""
import io
import json
import re
import sys
import urllib.error
import urllib.request

SOURCE = "content/landing-pages.ts"
BASE = "http://localhost:3057"
HERO_MAX = 200
HEADLINE_MAX = 30
DESCRIPTION_MAX = 90
COMMERCIAL = ("for sale", " buy ", "cheap", "купить", "продаж", "недорого", "дешев")


def entries(text):
    out = []
    for match in re.finditer(r'\n    slug: "([a-z0-9-]+)",', text):
        start = match.start()
        end = text.find('\n  },\n', start)
        out.append((match.group(1), text[start:end]))
    return out


def field(block, name):
    m = re.search(name + r': "((?:[^"\\]|\\.)*)"', block)
    return m.group(1) if m else None


def strings(block, name):
    m = re.search(name + r': \[(.*?)\]', block, re.S)
    if not m:
        return []
    return re.findall(r'"((?:[^"\\]|\\.)*)"', m.group(1))


def fetch(path):
    try:
        with urllib.request.urlopen(BASE + path, timeout=20) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception as e:
        return 0, str(e)


def main():
    text = io.open(SOURCE, encoding="utf-8").read()
    only = set(sys.argv[1:])
    problems = []
    checked = 0
    for slug, block in entries(text):
        if only and slug not in only:
            continue
        checked += 1
        hero = field(block, "heroText") or ""
        if len(hero) > HERO_MAX:
            problems.append("%s: heroText %d chars (max %d)" % (slug, len(hero), HERO_MAX))
        for h in strings(block, "headlines"):
            if len(h) > HEADLINE_MAX:
                problems.append("%s: headline %d chars -- %s" % (slug, len(h), h))
        for d in strings(block, "descriptions"):
            if len(d) > DESCRIPTION_MAX:
                problems.append("%s: description %d chars -- %s" % (slug, len(d), d))
        has_article = "seoSections:" in block
        status, html = fetch("/" + slug)
        if status != 200:
            problems.append("%s: HTTP %s" % (slug, status))
            continue
        order = re.findall(r'class="(seo-notes|trust-strip|landing-intro)"', html)
        if has_article:
            if "seo-notes" not in order:
                problems.append("%s: article block missing from the page" % slug)
            elif order.index("seo-notes") != order.index("trust-strip") + 1:
                problems.append("%s: article block is not right after the trust strip" % slug)
        plain = re.sub(r"<[^>]*>", " ", html).lower()
        hits = sorted({c.strip() for c in COMMERCIAL if c in plain})
        if hits:
            print("  %-26s commercial wording present: %s" % (slug, ", ".join(hits)))
    print("checked %d pages" % checked)
    if problems:
        print("\nPROBLEMS")
        for p in problems:
            print(" -", p)
        raise SystemExit(1)
    print("all clear")


if __name__ == "__main__":
    main()
