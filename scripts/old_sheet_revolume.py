#!/usr/bin/env python
"""Реальные частоты для старого ядра через Keyword Planner. Только чтение."""
import io, time
from collections import defaultdict
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from google.oauth2 import service_account

CID = "3432200766"
COUNTRIES = [("UA",2804,"Украина"),("KZ",2398,"Казахстан"),("BY",2112,"Беларусь"),
             ("PL",2616,"Польша"),("DE",2276,"Германия"),("CZ",2203,"Чехия"),
             ("IL",2376,"Израиль"),("US",2840,"США"),("GB",2826,"Британия"),
             ("TR",2792,"Турция"),("ES",2724,"Испания"),("IT",2380,"Италия"),
             ("BG",2100,"Болгария"),("MD",2498,"Молдова"),("UZ",2860,"Узбекистан")]

rows = []
with io.open("data/ads/old-semantics.tsv", encoding="utf-8") as fh:
    next(fh)
    for line in fh:
        p = line.rstrip("\n").split("\t")
        rows.append(p)
by_lang = defaultdict(list)
for p in rows:
    by_lang[p[1]].append(p[0])
print({k: len(v) for k, v in by_lang.items()})

client = GoogleAdsClient(
    credentials=service_account.Credentials.from_service_account_file(
        ".secrets/gstar-sa.json", scopes=["https://www.googleapis.com/auth/adwords"]),
    developer_token="t8wOf5cvS7HV5V7gjHnH2w", login_customer_id="8522851042",
    version="v22", use_proto_plus=True)
service = client.get_service("KeywordPlanIdeaService")
LANG_ID = {"ru": 1031, "uk": 1036}

matrix = defaultdict(dict)
for lang, kws in by_lang.items():
    for code, geo, name in COUNTRIES:
        request = client.get_type("GenerateKeywordHistoricalMetricsRequest")
        request.customer_id = CID
        request.keywords.extend(kws[:1800])
        request.language = f"languageConstants/{LANG_ID[lang]}"
        request.geo_target_constants = [f"geoTargetConstants/{geo}"]
        request.keyword_plan_network = client.enums.KeywordPlanNetworkEnum.GOOGLE_SEARCH
        got = None
        for attempt in range(5):
            try:
                got = service.generate_keyword_historical_metrics(request=request); break
            except GoogleAdsException as err:
                msgs = "; ".join(e.message for e in err.failure.errors)
                if "Too many requests" in msgs:
                    time.sleep(8 * (attempt + 1)); continue
                print(f"  {lang}/{name}: {msgs[:70]}"); break
            except Exception as err:
                if "RESOURCE_EXHAUSTED" in str(err) or "429" in str(err):
                    time.sleep(8 * (attempt + 1)); continue
                print(f"  {lang}/{name}: {str(err)[:70]}"); break
        if got:
            for res in got.results:
                v = res.keyword_metrics.avg_monthly_searches or 0
                if v:
                    matrix[res.text][code] = matrix[res.text].get(code, 0) + v
        time.sleep(2)
    print(f"  {lang}: обработано")

codes = [c[0] for c in COUNTRIES]
out = []
with io.open("data/ads/old-semantics-revolumed.tsv", "w", encoding="utf-8") as fh:
    fh.write("keyword\tlang\ttopic\tintent\tfreq_sheet\ttotal_real\t" + "\t".join(codes) + "\n")
    for p in rows:
        kw = p[0]
        per = matrix.get(kw, {})
        total = sum(per.values())
        out.append((total, kw, p[1], p[2]))
        fh.write(f"{kw}\t{p[1]}\t{p[2]}\t{p[3]}\t{p[5]}\t{total}\t"
                 + "\t".join(str(per.get(c, 0)) for c in codes) + "\n")

out.sort(reverse=True)
print(f"\nКлючей с реальной частотой: {sum(1 for t,_,_,_ in out if t>0)} из {len(out)}")
print(f"Суммарный объём: {sum(t for t,_,_,_ in out)}/мес\n")
print("Топ-20 их ядра по реальной частоте:")
for total, kw, lang, topic in out[:20]:
    print(f"  {total:>6}/мес  [{lang}] {topic:<14} {kw[:52]}")
by_topic = defaultdict(int)
for total, kw, lang, topic in out:
    by_topic[topic] += total
print("\nПо темам, реальный объём:")
for name, v in sorted(by_topic.items(), key=lambda kv: -kv[1]):
    print(f"  {name:<16} {v:>7}/мес")
