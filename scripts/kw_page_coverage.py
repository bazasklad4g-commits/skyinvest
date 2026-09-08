# -*- coding: utf-8 -*-
"""How much of each cluster's informational demand the page's own text already covers.

A query counts as covered when every one of its tokens appears somewhere in the
page's visible text (hero, article sections, FAQ). Volume-weighted, because one
880/mo query is worth more than ten 10/mo ones.
"""
import collections
import io
import re

PAGES = "content/landing-pages.ts"
TSV = "data/ads/city-informational.tsv"
OUT = "data/ads/KEYWORDS-BY-PAGE.md"

SLUG_CLUSTER = [
    ("stambul-ru", "Istanbul", "ru"), ("antaliya-ru", "Antalya", "ru"),
    ("alania-ru", "Alanya", "ru"), ("mersin-ru", "Mersin", "ru"),
    ("turciya-vnzh-ikamet", "Residence permit", "ru"),
    ("grazhdanstvo-turcii", "Citizenship", "ru"),
    ("istanbul-property", "Istanbul", "en"), ("antalya-property", "Antalya", "en"),
    ("alanya-property", "Alanya", "en"), ("bodrum-property", "Bodrum", "en"),
    ("fethiye-property", "Fethiye", "en"), ("marmaris-property", "Marmaris", "en"),
    ("kusadasi-property", "Kusadasi", "en"), ("izmir-property", "Izmir", "en"),
    ("kemer-property", "Kemer", "en"),
    ("turkey-residence-permit", "Residence permit", "en"),
    ("turkish-citizenship", "Citizenship", "en"),
]
STOP = set("the a an in of for to and or on at is are it with my how what where can do i".split())


def norm(s):
    return re.sub(r"[^0-9a-z\u0400-\u04ff]+", " ", s.lower()).strip()


def tokens(s):
    return [t for t in norm(s).split() if t not in STOP and len(t) > 2]


def page_texts():
    src = io.open(PAGES, encoding="utf-8").read()
    marks = [(m.start(), m.group(1)) for m in re.finditer(r'slug:\s*"([^"]+)"', src)]
    out = {}
    for i, (pos, slug) in enumerate(marks):
        end = marks[i + 1][0] if i + 1 < len(marks) else len(src)
        out[slug] = src[pos:end]
    return out


def main():
    pages = page_texts()
    rows = collections.defaultdict(list)
    for line in io.open(TSV, encoding="utf-8").read().splitlines()[1:]:
        p = line.split("\t")
        if len(p) < 4:
            continue
        try:
            vol = int(p[2])
        except ValueError:
            continue
        rows[(p[1], p[0])].append((vol, p[3]))

    out = ["# Какие ключи какой странице принадлежат и сколько текст уже покрывает\n"]
    out.append("Запрос считается покрытым, если все его значимые слова встречаются "
               "в тексте страницы. Доля считается по объёму, а не по числу запросов.\n")
    out.append("| Страница | Кластер | Яз. | Запросов | Объём/мес | Покрыто по объёму |")
    out.append("|---|---|---|---:|---:|---:|")
    detail = []
    for slug, cluster, lang in SLUG_CLUSTER:
        body = norm(pages.get(slug, ""))
        words = set(body.split())
        # Russian is inflected: "недвижимости" on the page must satisfy the query
        # word "недвижимость". Match on a five-letter stem instead of the full form.
        stems = {w[:5] for w in words}

        def seen(t):
            return t in words or t[:5] in stems
        qs = rows.get((cluster, lang), [])
        tot = sum(v for v, _ in qs)
        hit = miss = 0
        missed = []
        for vol, q in qs:
            tk = tokens(q)
            if tk and all(seen(t) for t in tk):
                hit += vol
            else:
                miss += vol
                missed.append((vol, q, [t for t in tk if not seen(t)]))
        pct = (100.0 * hit / tot) if tot else 0.0
        out.append("| `/%s` | %s | %s | %d | %d | **%.0f%%** |" % (
            slug, cluster, lang, len(qs), tot, pct))
        missed.sort(key=lambda x: -x[0])
        detail.append((slug, cluster, lang, tot, pct, missed[:25]))

    out.append("\n---\n\n## Что в тексте страницы ещё не сказано\n")
    for slug, cluster, lang, tot, pct, missed in detail:
        out.append("### `/%s` — %s (%s), %d/мес, покрыто %.0f%%\n" % (slug, cluster, lang, tot, pct))
        if not missed:
            out.append("Всё покрыто.\n")
            continue
        for vol, q, gap in missed:
            out.append("- **%d/мес** — %s  ·  не хватает слов: %s" % (vol, q, ", ".join(gap) or "—"))
        out.append("")
    io.open(OUT, "w", encoding="utf-8").write("\n".join(out) + "\n")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
