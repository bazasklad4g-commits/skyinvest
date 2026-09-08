#!/usr/bin/env python
"""Кластеризация турецкой семантики по интентам и городам."""
import io, re
from collections import defaultdict

CITIES = {
    "Алания": ["алани", "аланья", "аланії"], "Анталия": ["анталь", "анталі", "антали"],
    "Стамбул": ["стамбул"], "Измир": ["измир", "ізмір"], "Бодрум": ["бодрум"],
    "Фетхие": ["фетхие", "фетхіє"], "Мерсин": ["мерсин", "мерсін"], "Кемер": ["кемер"],
    "Сиде": ["сиде", "сіде"], "Белек": ["белек"], "Мармарис": ["мармарис", "мармаріс"],
    "Кушадасы": ["кушадас"], "Бурса": ["бурса", "бурсе"], "Анкара": ["анкар"],
    "Трабзон": ["трабзон"], "Аланья-Махмутлар": ["махмутлар"], "Каш/Калкан": ["калкан", " каш"],
}
INTENT = [
    ("Покупка / коммерческий", ["купить", "купити", "продажа", "продаж", "цена", "цін",
                                 "стоимост", "недорого", "дешев", "от застройщика"]),
    ("Новостройки", ["новострой", "новобуд", "новостройк", "строящ", "off plan", "от девелопера"]),
    ("Аренда", ["аренд", "оренд", "снять", "зняти", "долгосрочн"]),
    ("ВНЖ / ПМЖ / икамет", ["икамет", "ікамет", "вид на жительство", "пмж", "внж",
                             "посвідка", "резиденц", "туристический вэ"]),
    ("Гражданство", ["гражданств", "громадянств", "паспорт турци"]),
    ("Переезд / эмиграция", ["переезд", "переїзд", "эмиграц", "еміграц", "перееха",
                              "жизнь в турции", "життя в туреччині", "релокац"]),
    ("Налоги и расходы", ["налог", "податк", "содержан", "утримання", "коммунал", "айдат"]),
    ("Документы и проверка", ["тапу", "искан", "iskan", "документ", "проверк", "перевірк", "реестр"]),
]

rows = []
with io.open("data/ads/semantics-turkey.tsv", encoding="utf-8") as fh:
    next(fh)
    for line in fh:
        kw, lang, vol, comp, bid = line.rstrip("\n").split("\t")
        rows.append((kw, lang, int(vol), comp, float(bid)))

def city_of(kw):
    low = kw.lower()
    for name, marks in CITIES.items():
        if any(m in low for m in marks):
            return name
    return None

def intent_of(kw):
    low = kw.lower()
    for name, marks in INTENT:
        if any(m in low for m in marks):
            return name
    return "Общий интерес / информационный"

by_city = defaultdict(list)
by_intent = defaultdict(list)
for kw, lang, vol, comp, bid in rows:
    if vol <= 0:
        continue
    by_intent[intent_of(kw)].append((vol, kw, lang, comp))
    c = city_of(kw)
    if c:
        by_city[c].append((vol, kw, lang, comp))

lines = ["# Семантика по Турции", "",
         f"Источник: Google Keyword Planner, {len(rows)} запросов, из них с ненулевой частотой "
         f"{sum(1 for r in rows if r[2] > 0)}.",
         "Гео: Турция, Украина, Польша, Германия, Чехия, Израиль, США, Британия, Испания, ОАЭ.",
         "Частота — среднее число запросов в месяц по этой сумме стран.", "",
         "## По интентам", "",
         "| Кластер | Запросов | Суммарный объём | Топ-запрос |", "|---|---:|---:|---|"]
for name, items in sorted(by_intent.items(), key=lambda kv: -sum(i[0] for i in kv[1])):
    items.sort(reverse=True)
    lines.append(f"| {name} | {len(items)} | {sum(i[0] for i in items)} | "
                 f"{items[0][1]} ({items[0][0]}) |")

lines += ["", "## По городам", "",
          "| Город | Запросов | Суммарный объём | Топ-запрос |", "|---|---:|---:|---|"]
for name, items in sorted(by_city.items(), key=lambda kv: -sum(i[0] for i in kv[1])):
    items.sort(reverse=True)
    lines.append(f"| {name} | {len(items)} | {sum(i[0] for i in items)} | "
                 f"{items[0][1]} ({items[0][0]}) |")

for name, items in sorted(by_intent.items(), key=lambda kv: -sum(i[0] for i in kv[1])):
    items.sort(reverse=True)
    lines += ["", f"## {name}: топ-25", "", "| Запрос | Яз. | Частота | Конкуренция |", "|---|---|---:|---|"]
    for vol, kw, lang, comp in items[:25]:
        lines.append(f"| {kw} | {lang} | {vol} | {comp} |")

io.open("data/ads/TURKEY-SEMANTICS.md", "w", encoding="utf-8").write("\n".join(lines) + "\n")
print("интентов:", len(by_intent), "| городов:", len(by_city))
for name, items in sorted(by_intent.items(), key=lambda kv: -sum(i[0] for i in kv[1])):
    print(f"  {name:<34} {len(items):>4} запр., {sum(i[0] for i in items):>6}/мес")
print("\nГорода:")
for name, items in sorted(by_city.items(), key=lambda kv: -sum(i[0] for i in kv[1])):
    print(f"  {name:<20} {len(items):>4} запр., {sum(i[0] for i in items):>6}/мес")
