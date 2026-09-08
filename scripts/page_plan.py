#!/usr/bin/env python
"""План страниц: кластер -> страница, с реальными запросами и объёмами."""
import io, re
from collections import defaultdict

def load(path, kw=0, vol=1, lang=None):
    out = []
    with io.open(path, encoding="utf-8") as fh:
        next(fh)
        for line in fh:
            p = line.rstrip("\n").split("\t")
            out.append((p[kw], int(p[vol]), lang or "ru"))
    return out

ru_tur = load("data/ads/turkey-by-country.tsv")
en_tur = load("data/ads/turkey-by-country-en.tsv", lang="en")
core = []
with io.open("data/ads/old-core-revolumed.tsv", encoding="utf-8") as fh:
    next(fh)
    for line in fh:
        p = line.rstrip("\n").split("\t")
        core.append((p[0], int(p[5]), p[1]))

CLUSTERS = [
 # (имя, язык, маркеры, источник)
 ("Алания", "ru", ["алани","аланья"], ru_tur), ("Анталия","ru",["анталь","антали"], ru_tur),
 ("Стамбул","ru",["стамбул"], ru_tur), ("Мерсин","ru",["мерсин"], ru_tur),
 ("Бодрум","ru",["бодрум"], ru_tur), ("Кемер","ru",["кемер"], ru_tur),
 ("Измир","ru",["измир"], ru_tur), ("Махмутлар","ru",["махмутлар"], ru_tur),
 ("ВНЖ и икамет в Турции","ru",["икамет","вид на жительство","внж","резиденц"], ru_tur),
 ("Гражданство Турции","ru",["гражданств"], ru_tur),
 ("Налоги и содержание в Турции","ru",["налог","содержан","коммунал","айдат","расход"], ru_tur),
 ("Istanbul","en",["istanbul"], en_tur), ("Marmaris","en",["marmaris"], en_tur),
 ("Antalya","en",["antalya"], en_tur), ("Side","en",[" side","side "], en_tur),
 ("Alanya","en",["alanya"], en_tur), ("Bodrum","en",["bodrum"], en_tur),
 ("Fethiye","en",["fethiye"], en_tur), ("Kusadasi","en",["kusadasi"], en_tur),
 ("Turkey residence permit","en",["residence permit","ikamet","citizenship"], en_tur),
 ("Аликанте","ru",["аликанте"], core), ("Валенсия","ru",["валенси"], core),
 ("Барселона","ru",["барселон"], core), ("Торревьеха","ru",["торревьех"], core),
 ("Испания общая","ru",["испан"], core),
 ("Северный Кипр","ru",["кипр","искеле","фамагуст","кирени"], core),
 ("Бали","ru",["бали"], core), ("Болгария у моря","ru",["болгар"], core),
 ("Италия у моря","ru",["итали"], core), ("Греция у моря","ru",["греци"], core),
 ("Черногория у моря","ru",["черногор"], core), ("Хорватия у моря","ru",["хорват"], core),
 ("Грузия и Батуми","ru",["батуми","грузи"], core),
 ("Албания у моря","ru",["албани"], core), ("Португалия у моря","ru",["португал"], core),
]

used = defaultdict(set)
result = []
for name, lang, marks, source in CLUSTERS:
    hits = []
    for kw, vol, _ in source:
        low = kw.lower()
        if vol > 0 and any(m in low for m in marks) and kw.lower() not in used[lang]:
            hits.append((vol, kw))
    hits.sort(reverse=True)
    for _, kw in hits:
        used[lang].add(kw.lower())
    result.append((name, lang, sum(v for v, _ in hits), len(hits), hits[:12]))

result.sort(key=lambda r: -r[2])
lines = ["# План страниц под кластеры запросов", "",
         "Объём — среднее число запросов в месяц, суммарно по странам замера.",
         "Каждый запрос отнесён только к одному кластеру, двойного счёта нет.", "",
         "| Кластер | Яз. | Объём/мес | Запросов |", "|---|---|---:|---:|"]
for name, lang, vol, n, top in result:
    if vol:
        lines.append(f"| {name} | {lang} | {vol} | {n} |")
lines.append("")
for name, lang, vol, n, top in result:
    if not vol:
        continue
    lines += [f"## {name} ({lang}) — {vol}/мес, {n} запросов", ""]
    for v, kw in top:
        lines.append(f"- {kw} — {v}")
    lines.append("")
io.open("data/ads/CLUSTERS.md", "w", encoding="utf-8").write("\n".join(lines) + "\n")

print(f"{'Кластер':<32}{'яз':>4}{'объём':>9}{'ключей':>8}")
for name, lang, vol, n, top in result:
    if vol:
        print(f"{name:<32}{lang:>4}{vol:>9}{n:>8}")
