#!/usr/bin/env python
"""Отчёт: где живёт спрос на турецкую недвижимость и через какие города его ищут."""
import io
from collections import defaultdict

CITIES = {
    "Алания": ["алани", "аланья"], "Анталия": ["анталь", "антали"], "Стамбул": ["стамбул"],
    "Махмутлар": ["махмутлар"], "Мерсин": ["мерсин"], "Кемер": ["кемер"], "Измир": ["измир"],
    "Бодрум": ["бодрум"], "Фетхие": ["фетхие"], "Мармарис": ["мармарис"], "Сиде": ["сиде"],
    "Белек": ["белек"], "Кушадасы": ["кушадас"], "Бурса": ["бурс"], "Анкара": ["анкар"],
    "Трабзон": ["трабзон"], "Каш и Калкан": ["калкан"], "Аланья-Оба": ["оба алани"],
}
NAMES = {"UA":"Украина","KZ":"Казахстан","BY":"Беларусь","PL":"Польша","DE":"Германия",
         "CZ":"Чехия","IL":"Израиль","US":"США","CA":"Канада","GB":"Британия","TR":"Турция",
         "AE":"ОАЭ","GE":"Грузия","MD":"Молдова","LV":"Латвия","LT":"Литва","EE":"Эстония",
         "AZ":"Азербайджан","UZ":"Узбекистан","ES":"Испания","IT":"Италия","NL":"Нидерланды",
         "AT":"Австрия","CH":"Швейцария","SK":"Словакия","HU":"Венгрия","RO":"Румыния",
         "BG":"Болгария","FI":"Финляндия","SE":"Швеция","RU":"Россия"}

with io.open("data/ads/turkey-by-country.tsv", encoding="utf-8") as fh:
    header = fh.readline().rstrip("\n").split("\t")
    codes = header[2:]
    rows = []
    for line in fh:
        p = line.rstrip("\n").split("\t")
        rows.append((p[0], int(p[1]), {c: int(v) for c, v in zip(codes, p[2:])}))

def city_of(kw):
    low = kw.lower()
    for name, marks in CITIES.items():
        if any(m in low for m in marks):
            return name
    return None

by_country = {c: sum(r[2].get(c, 0) for r in rows) for c in codes}
by_country = {c: v for c, v in by_country.items() if v > 0}
grand = sum(by_country.values())
non_tr = grand - by_country.get("TR", 0)

city_country = defaultdict(lambda: defaultdict(int))
city_total = defaultdict(int)
for kw, total, per in rows:
    c = city_of(kw)
    if not c:
        continue
    city_total[c] += total
    for code, v in per.items():
        city_country[c][code] += v

lines = ["# Спрос на недвижимость в Турции: где ищут и через какие города", "",
         "Источник: Google Keyword Planner, замер по каждой стране отдельно, русский язык.",
         f"В замере {len(rows)} запросов, 30 стран. Россия недоступна: Google не отдаёт по ней данные.", "",
         f"**Суммарный спрос: {grand} запросов в месяц.** Из них внутри Турции {by_country.get('TR',0)} "
         f"({by_country.get('TR',0)*100//grand}%), за пределами Турции **{non_tr} ({non_tr*100//grand}%)**.", "",
         "## Страны по объёму спроса", "",
         "| Страна | Запросов/мес | Доля |", "|---|---:|---:|"]
for code, v in sorted(by_country.items(), key=lambda kv: -kv[1]):
    lines.append(f"| {NAMES.get(code, code)} | {v} | {v*100/grand:.1f}% |")

lines += ["", "## Города: сколько ищут и откуда", "",
          "| Город | Всего/мес | Топ-5 стран |", "|---|---:|---|"]
for city, total in sorted(city_total.items(), key=lambda kv: -kv[1]):
    top = sorted(city_country[city].items(), key=lambda kv: -kv[1])[:5]
    top_s = ", ".join(f"{NAMES.get(c, c)} {v}" for c, v in top if v > 0)
    lines.append(f"| {city} | {total} | {top_s} |")

lines += ["", "## Топ-10 запросов в каждой стране", ""]
for code, _ in sorted(by_country.items(), key=lambda kv: -kv[1]):
    top = sorted(((r[2].get(code, 0), r[0]) for r in rows), reverse=True)[:10]
    top = [(v, k) for v, k in top if v > 0]
    if not top:
        continue
    lines += [f"### {NAMES.get(code, code)} — {by_country[code]}/мес", ""]
    for v, kw in top:
        lines.append(f"- {kw} — **{v}**")
    lines.append("")

lines += ["## Городские запросы: топ-60 по общему объёму", "",
          "| Запрос | Всего/мес | Где больше всего |", "|---|---:|---|"]
city_rows = [(kw, t, per) for kw, t, per in rows if city_of(kw)]
for kw, total, per in sorted(city_rows, key=lambda r: -r[1])[:60]:
    top = sorted(per.items(), key=lambda kv: -kv[1])[:3]
    lines.append(f"| {kw} | {total} | " + ", ".join(f"{NAMES.get(c,c)} {v}" for c, v in top if v) + " |")

io.open("data/ads/TURKEY-BY-COUNTRY.md", "w", encoding="utf-8").write("\n".join(lines) + "\n")
print(f"Всего {grand}/мес, вне Турции {non_tr} ({non_tr*100//grand}%)")
print("\nСтраны:")
for code, v in sorted(by_country.items(), key=lambda kv: -kv[1])[:12]:
    print(f"  {NAMES.get(code,code):<12} {v:>6}/мес  {v*100/grand:>5.1f}%")
print("\nГорода:")
for city, total in sorted(city_total.items(), key=lambda kv: -kv[1])[:10]:
    top = sorted(city_country[city].items(), key=lambda kv: -kv[1])[:3]
    print(f"  {city:<14} {total:>6}/мес  ← " + ", ".join(f"{NAMES.get(c,c)} {v}" for c, v in top))
