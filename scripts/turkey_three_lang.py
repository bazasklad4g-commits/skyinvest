#!/usr/bin/env python
"""Сводный отчёт по трём языкам: страны, города, топ-запросы."""
import io
from collections import defaultdict

NAMES = {"UA":"Украина","KZ":"Казахстан","BY":"Беларусь","PL":"Польша","DE":"Германия","CZ":"Чехия",
 "IL":"Израиль","US":"США","CA":"Канада","GB":"Британия","TR":"Турция","AE":"ОАЭ","GE":"Грузия",
 "MD":"Молдова","LV":"Латвия","LT":"Литва","EE":"Эстония","AZ":"Азербайджан","UZ":"Узбекистан",
 "ES":"Испания","IT":"Италия","NL":"Нидерланды","AT":"Австрия","CH":"Швейцария","SK":"Словакия",
 "HU":"Венгрия","RO":"Румыния","BG":"Болгария","FI":"Финляндия","SE":"Швеция","IE":"Ирландия",
 "AU":"Австралия","SA":"Саудовская Аравия","QA":"Катар","KW":"Кувейт","IN":"Индия","ZA":"ЮАР",
 "SG":"Сингапур","BE":"Бельгия","NO":"Норвегия","DK":"Дания","FR":"Франция","GR":"Греция",
 "CY":"Кипр","MY":"Малайзия","NZ":"Новая Зеландия","PT":"Португалия"}

CITY_MARKS = {
 "Алания":["алани","аланья","аланії","alanya"], "Анталия":["анталь","антали","анталії","antalya"],
 "Стамбул":["стамбул","istanbul"], "Махмутлар":["махмутлар","mahmutlar"],
 "Мерсин":["мерсин","мерсін","mersin"], "Кемер":["кемер","kemer"], "Измир":["измир","ізмір","izmir"],
 "Бодрум":["бодрум","bodrum"], "Фетхие":["фетхие","фетхіє","fethiye"],
 "Мармарис":["мармарис","мармаріс","marmaris"], "Сиде":["сиде","сіде"," side"],
 "Белек":["белек","belek"], "Кушадасы":["кушадас","kusadasi"], "Бурса":["бурс","bursa"],
 "Анкара":["анкар","ankara"], "Трабзон":["трабзон","trabzon"], "Дидим":["дидим","didim","altinkum"],
 "Чешме":["чешме","cesme"],
}

def load(path):
    with io.open(path, encoding="utf-8") as fh:
        codes = fh.readline().rstrip("\n").split("\t")[2:]
        rows = []
        for line in fh:
            p = line.rstrip("\n").split("\t")
            rows.append((p[0], int(p[1]), {c: int(v) for c, v in zip(codes, p[2:])}))
    return codes, rows

DATA = {
    "Русский": load("data/ads/turkey-by-country.tsv"),
    "Английский": load("data/ads/turkey-by-country-en.tsv"),
    "Украинский": load("data/ads/turkey-by-country-uk.tsv"),
}

def city_of(kw):
    low = kw.lower()
    for name, marks in CITY_MARKS.items():
        if any(m in low for m in marks):
            return name
    return None

lines = ["# Спрос по Турции на трёх языках", "",
         "Источник: Google Keyword Planner. Замер по каждой стране отдельно.",
         "Английский и украинский отфильтрованы по упоминанию Турции или турецкого города —",
         "иначе в выборку попадают общие «real estate» без привязки к стране.", "",
         "## Итог по языкам", "", "| Язык | Запросов | Объём/мес | Стран в замере |", "|---|---:|---:|---:|"]
totals = {}
for lang, (codes, rows) in DATA.items():
    grand = sum(sum(r[2].values()) for r in rows)
    totals[lang] = grand
    lines.append(f"| {lang} | {len(rows)} | {grand} | {len(codes)} |")
lines += ["", f"**Английский даёт {totals['Английский']/max(totals['Русский'],1):.1f}× русского "
              f"и {totals['Английский']/max(totals['Украинский'],1):.0f}× украинского.**", ""]

for lang, (codes, rows) in DATA.items():
    by_c = {c: sum(r[2].get(c, 0) for r in rows) for c in codes}
    by_c = {c: v for c, v in by_c.items() if v > 0}
    grand = sum(by_c.values()) or 1
    tr = by_c.get("TR", 0)
    lines += [f"## {lang}: страны", "",
              f"Внутри Турции {tr} ({tr*100//grand}%), за её пределами **{grand-tr} ({(grand-tr)*100//grand}%)**.", "",
              "| Страна | Запросов/мес | Доля |", "|---|---:|---:|"]
    for c, v in sorted(by_c.items(), key=lambda kv: -kv[1]):
        lines.append(f"| {NAMES.get(c,c)} | {v} | {v*100/grand:.1f}% |")
    lines.append("")

    ct = defaultdict(int); cc = defaultdict(lambda: defaultdict(int))
    for kw, total, per in rows:
        c = city_of(kw)
        if not c:
            continue
        ct[c] += total
        for code, v in per.items():
            cc[c][code] += v
    if ct:
        lines += [f"## {lang}: города", "", "| Город | Запросов/мес | Топ-5 стран |", "|---|---:|---|"]
        for city, total in sorted(ct.items(), key=lambda kv: -kv[1]):
            top = sorted(cc[city].items(), key=lambda kv: -kv[1])[:5]
            lines.append(f"| {city} | {total} | " +
                         ", ".join(f"{NAMES.get(c,c)} {v}" for c, v in top if v) + " |")
        lines.append("")

    lines += [f"## {lang}: топ-40 запросов", "", "| Запрос | Всего/мес | Где больше всего |", "|---|---:|---|"]
    for kw, total, per in sorted(rows, key=lambda r: -r[1])[:40]:
        top = sorted(per.items(), key=lambda kv: -kv[1])[:3]
        lines.append(f"| {kw} | {total} | " + ", ".join(f"{NAMES.get(c,c)} {v}" for c, v in top if v) + " |")
    lines.append("")

io.open("data/ads/TURKEY-THREE-LANGUAGES.md", "w", encoding="utf-8").write("\n".join(lines) + "\n")
for lang in DATA:
    print(f"{lang}: {totals[lang]}/мес")
print("\nГорода по-английски:")
codes, rows = DATA["Английский"]
ct = defaultdict(int)
for kw, total, per in rows:
    c = city_of(kw)
    if c: ct[c] += total
for city, total in sorted(ct.items(), key=lambda kv: -kv[1])[:10]:
    print(f"  {city:<12} {total:>7}/мес")
