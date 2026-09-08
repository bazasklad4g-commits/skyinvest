# -*- coding: utf-8 -*-
"""Does a page's own text contain the keywords its enabled campaigns run on?

A keyword counts as covered when every one of its meaningful words appears in the
page text. Words are compared by Snowball stem with "ё" folded to "е", because
Google treats "жильё"/"жилье" and "Дубай"/"Дубае" as one word. Snowball has no
Ukrainian stemmer, so a five-letter prefix match is accepted as well.
"""
import collections
import io
import re
import sys
import urllib.request

import snowballstemmer

STEMMER = snowballstemmer.stemmer("russian")

TSV = "data/ads/ads-with-keywords.tsv"
PREFIX = "https://m.nezalezhnist.org.ua/"


def norm(s):
    return re.sub(r"[^0-9a-z\u0400-\u04ff]+", " ", s.lower().replace("\u0451", "\u0435"))


def keys(w):
    return {STEMMER.stemWord(w), w[:5]}


def keywords():
    out = collections.defaultdict(set)
    for line in io.open(TSV, encoding="utf-8").read().splitlines()[1:]:
        p = line.split("\t")
        if len(p) >= 8 and p[6] == "ENABLED" and p[7].startswith(PREFIX):
            out[p[7].rsplit("/", 1)[1]].add(p[4])
    return out


def measure(base, slug, kws):
    try:
        req = urllib.request.Request(base + slug, headers={"User-Agent": "Mozilla/5.0"})
        body = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
    except Exception:
        return None, []
    words = set()
    for w in norm(re.sub(r"<[^>]+>", " ", body)).split():
        words |= keys(w)
    miss = sorted(k for k in kws
                  if not all(keys(t) & words for t in norm(k).split() if len(t) > 2))
    return len(kws) - len(miss), miss


def main():
    base = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:3057/"
    kws = keywords()
    rows = []
    for slug, ks in sorted(kws.items(), key=lambda kv: -len(kv[1])):
        hit, miss = measure(base, slug, ks)
        rows.append((slug, len(ks), hit, miss))
    with io.open("data/ads/_coverage.txt", "w", encoding="utf-8") as fh:
        for slug, n, hit, miss in rows:
            fh.write("%-40s %6d %6d %5s\n" % (slug, n, hit if hit is not None else -1,
                                              "%d%%" % (100 * hit / n) if hit is not None else "нет"))
        fh.write("\n")
        for slug, n, hit, miss in rows:
            if miss:
                fh.write("\n=== %s — не покрыто %d\n" % (slug, len(miss)) + "\n".join("  " + m for m in miss) + "\n")
    print("pages", len(rows))


if __name__ == "__main__":
    main()
