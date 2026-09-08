#!/usr/bin/env python
"""Извлечение старого семантического ядра из выгрузки таблицы."""
import io, json, re
from collections import Counter, defaultdict

tables = json.load(io.open("data/ads/old-sheet.json", encoding="utf-8"))

UK_MARKS = ["нерухом", "іспан", "туреччин", "аланія", "аланії", "купити", "балі", "кіпр",
            "італія", "болгарі", "квартиру в", "будинок"]

def is_uk(s):
    return any(m in s.lower() for m in UK_MARKS) and ("недвиж" not in s.lower())

TOPIC = {
    "испан": "Испания", "іспан": "Испания", "кипр": "Северный Кипр", "кіпр": "Северный Кипр",
    "бали": "Бали", "балі": "Бали", "италь": "Италия", "італ": "Италия", "итали": "Италия",
    "болгар": "Болгария", "алани": "Алания", "аланія": "Алания", "аланії": "Алания",
    "турци": "Турция", "туреччин": "Турция", "турция": "Турция",
}
def topic_of(kw, topo):
    low = (kw + " " + topo).lower()
    for mark, name in TOPIC.items():
        if mark in low:
            return name
    return "Прочее"

rows = []
for t in tables:
    header = [h.strip() for h in t["header"]]
    if not header or header[0] != "Ключевые фразы":
        continue
    idx = {name: i for i, name in enumerate(header)}
    for r in t["rows"]:
        if not r or not r[0].strip():
            continue
        def get(name):
            i = idx.get(name)
            return r[i].strip() if i is not None and i < len(r) else ""
        kw = r[0].strip()
        rows.append({
            "keyword": kw,
            "topo": get("Топонимы"),
            "intent": get("Интент"),
            "difficulty": get("Сложность"),
            "freq": get("Частотность"),
            "ppc": get("Конкуренция в PPC, %"),
            "lang": "uk" if is_uk(kw) else "ru",
            "topic": topic_of(kw, get("Топонимы")),
        })

seen = set(); uniq = []
for r in rows:
    k = r["keyword"].lower()
    if k not in seen:
        seen.add(k); uniq.append(r)

print(f"строк всего {len(rows)}, уникальных ключей {len(uniq)}\n")
print("По темам:")
for name, n in Counter(r["topic"] for r in uniq).most_common():
    langs = Counter(r["lang"] for r in uniq if r["topic"] == name)
    print(f"  {name:<16} {n:>4}   ru {langs.get('ru',0):>3}, uk {langs.get('uk',0):>3}")
print("\nПо интентам (метка из таблицы):")
for name, n in Counter(r["intent"] for r in uniq).most_common(8):
    print(f"  {name or '(пусто)':<10} {n}")
print("\nЧастотность — какие значения встречаются:")
for name, n in Counter(r["freq"] for r in uniq).most_common(8):
    print(f"  {name or '(пусто)':<10} {n}")

with io.open("data/ads/old-semantics.tsv", "w", encoding="utf-8") as fh:
    fh.write("keyword\tlang\ttopic\tintent\tdifficulty\tfreq_sheet\tppc\n")
    for r in uniq:
        fh.write(f"{r['keyword']}\t{r['lang']}\t{r['topic']}\t{r['intent']}\t"
                 f"{r['difficulty']}\t{r['freq']}\t{r['ppc']}\n")
print("\nФайл: data/ads/old-semantics.tsv")
