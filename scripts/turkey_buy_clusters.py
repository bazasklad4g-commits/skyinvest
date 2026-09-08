#!/usr/bin/env python
"""Кластеры: только Турция, только покупка. Аренда, отели, туризм, работа исключены."""
import io
from collections import defaultdict

EXCL_RU = ["аренд","оренд","снять","сдать","посуточ","отел","гостиниц","тур ","туры","путёвк",
           "путевк","работа","вакан","виза","авиабилет","погода","школ","ресторан","отдых",
           "курорт ","всё включено","все включено","хостел","апарт-отель","базар","экскурс"]
EXCL_EN = ["rent","rental","hotel","hostel","holiday","vacation","flight","job","weather",
           "tour","resort","booking","all inclusive","excursion","airbnb"]
CITIES = {
 "Алания":["алани","аланья"],"Анталия":["анталь","антали"],"Стамбул":["стамбул"],
 "Мерсин":["мерсин"],"Бодрум":["бодрум"],"Кемер":["кемер"],"Измир":["измир"],
 "Махмутлар":["махмутлар"],"Мармарис":["мармарис"],"Фетхие":["фетхие"],"Сиде":["сиде"],
 "Белек":["белек"],"Кушадасы":["кушадас"],"Бурса":["бурс"],"Анкара":["анкар"],
 "Трабзон":["трабзон"],"Конаклы":["конаклы"],"Калкан":["калкан"],"Оба":["оба алани"],
}
CITIES_EN = {
 "Alanya":["alanya"],"Antalya":["antalya"],"Istanbul":["istanbul"],"Mersin":["mersin"],
 "Bodrum":["bodrum"],"Kemer":["kemer"],"Izmir":["izmir"],"Mahmutlar":["mahmutlar"],
 "Marmaris":["marmaris"],"Fethiye":["fethiye"],"Side":["side"],"Belek":["belek"],
 "Kusadasi":["kusadasi"],"Bursa":["bursa"],"Ankara":["ankara"],"Trabzon":["trabzon"],
 "Didim":["didim","altinkum"],"Cesme":["cesme"],
}
SUPPORT_RU = {
 "Документы и тапу":["тапу","искан","документ","право собственност","реестр","проверк"],
 "Налоги и содержание":["налог","содержан","коммунал","айдат","расход","обслуживан"],
 "ВНЖ через покупку":["икамет","вид на жительство","внж","резиденц","посвідк"],
 "Гражданство за покупку":["гражданств"],
 "Как проходит сделка":["сделк","оформлен","процедур","этап","как купить","как проходит","задаток"],
}
SUPPORT_EN = {
 "Documents and title deed":["tapu","title deed","documents","land registry","due diligence"],
 "Taxes and running costs":["tax","aidat","running cost","maintenance fee","utility"],
 "Residence permit":["residence permit","ikamet"],
 "Citizenship by investment":["citizenship"],
 "Buying process":["buying process","how to buy","purchase process","conveyanc"],
}

def load(path, lang):
    out = []
    with io.open(path, encoding="utf-8") as fh:
        next(fh)
        for line in fh:
            p = line.rstrip("\n").split("\t")
            out.append((p[0], int(p[1])))
    return out

def clusterize(rows, cities, support, excl, label):
    used = set()
    res = []
    dropped = 0
    kept = [(k, v) for k, v in rows if v > 0 and not any(e in k.lower() for e in excl)]
    dropped = sum(v for k, v in rows if v > 0 and any(e in k.lower() for e in excl))
    for name, marks in support.items():
        hits = sorted(((v, k) for k, v in kept
                       if k.lower() not in used and any(m in k.lower() for m in marks)), reverse=True)
        for _, k in hits: used.add(k.lower())
        if hits: res.append((name, "интент", sum(v for v, _ in hits), len(hits), hits[:10]))
    for name, marks in cities.items():
        hits = sorted(((v, k) for k, v in kept
                       if k.lower() not in used and any(m in k.lower() for m in marks)), reverse=True)
        for _, k in hits: used.add(k.lower())
        if hits: res.append((name, "город", sum(v for v, _ in hits), len(hits), hits[:10]))
    rest = sorted(((v, k) for k, v in kept if k.lower() not in used), reverse=True)
    res.append(("Турция общее", "хаб", sum(v for v, _ in rest), len(rest), rest[:10]))
    res.sort(key=lambda r: -r[2])
    print(f"\n=== {label} ===")
    print(f"отсеяно аренды/отелей/туризма: {dropped}/мес")
    for name, kind, vol, n, top in res:
        if vol: print(f"  {name:<26}{kind:<8}{vol:>8}/мес{n:>6} запр.")
    return res

ru = clusterize(load("data/ads/turkey-by-country.tsv","ru"), CITIES, SUPPORT_RU, EXCL_RU, "Русский")
en = clusterize(load("data/ads/turkey-by-country-en.tsv","en"), CITIES_EN, SUPPORT_EN, EXCL_EN, "Английский")

L = ["# Кластеры: покупка квартир в Турции", "",
     "Аренда, отели, туры, работа и визы без привязки к покупке исключены.", ""]
for label, res in (("Русский", ru), ("Английский", en)):
    L += [f"## {label}", "", "| Кластер | Тип | Объём/мес | Запросов |", "|---|---|---:|---:|"]
    for name, kind, vol, n, top in res:
        if vol: L.append(f"| {name} | {kind} | {vol} | {n} |")
    L.append("")
    for name, kind, vol, n, top in res:
        if not vol: continue
        L += [f"### {name} — {vol}/мес", ""] + [f"- {k} — {v}" for v, k in top] + [""]
io.open("data/ads/TURKEY-BUY-CLUSTERS.md","w",encoding="utf-8").write("\n".join(L)+"\n")
print("\nФайл: data/ads/TURKEY-BUY-CLUSTERS.md")
