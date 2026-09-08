#!/usr/bin/env python
"""Реальные частоты для полного старого ядра. Только чтение."""
import io, time
from collections import defaultdict
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from google.oauth2 import service_account

CID = "3432200766"
COUNTRIES = [("UA",2804,"Украина"),("KZ",2398,"Казахстан"),("BY",2112,"Беларусь"),
             ("PL",2616,"Польша"),("DE",2276,"Германия"),("CZ",2203,"Чехия"),
             ("IL",2376,"Израиль"),("US",2840,"США"),("GB",2826,"Британия"),
             ("TR",2792,"Турция"),("ES",2724,"Испания"),("MD",2498,"Молдова"),
             ("UZ",2860,"Узбекистан"),("GE",2268,"Грузия"),("AZ",2031,"Азербайджан")]
LANG_ID = {"ru": 1031, "uk": 1036}

meta = {}
by_lang = defaultdict(list)
with io.open("data/ads/old-core-clean.tsv", encoding="utf-8") as fh:
    header = fh.readline()
    for line in fh:
        p = line.rstrip("\n").split("\t")
        meta[(p[0], p[1])] = p
        by_lang[p[1]].append(p[0])
print({k: len(v) for k, v in by_lang.items()})

client = GoogleAdsClient(
    credentials=service_account.Credentials.from_service_account_file(
        ".secrets/gstar-sa.json", scopes=["https://www.googleapis.com/auth/adwords"]),
    developer_token="t8wOf5cvS7HV5V7gjHnH2w", login_customer_id="8522851042",
    version="v22", use_proto_plus=True)
service = client.get_service("KeywordPlanIdeaService")

matrix = defaultdict(lambda: defaultdict(int))
for lang, kws in by_lang.items():
    chunks = [kws[i:i + 1500] for i in range(0, len(kws), 1500)]
    for ci, chunk in enumerate(chunks, 1):
        for code, geo, name in COUNTRIES:
            request = client.get_type("GenerateKeywordHistoricalMetricsRequest")
            request.customer_id = CID
            request.keywords.extend(chunk)
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
                    print(f"  {lang}/{name}: {msgs[:60]}"); break
                except Exception as err:
                    if "RESOURCE_EXHAUSTED" in str(err) or "429" in str(err):
                        time.sleep(8 * (attempt + 1)); continue
                    print(f"  {lang}/{name}: {str(err)[:60]}"); break
            if got:
                for res in got.results:
                    v = res.keyword_metrics.avg_monthly_searches or 0
                    if v:
                        matrix[(res.text, lang)][code] += v
            time.sleep(2)
        print(f"  {lang} чанк {ci}/{len(chunks)} готов")

codes = [c[0] for c in COUNTRIES]
scored = []
with io.open("data/ads/old-core-revolumed.tsv", "w", encoding="utf-8") as fh:
    fh.write("keyword\tlang\ttopic\tintent\tfreq_sheet\ttotal_real\t" + "\t".join(codes) + "\n")
    for key, p in meta.items():
        per = matrix.get(key, {})
        total = sum(per.values())
        scored.append((total, p[0], p[1], p[2]))
        fh.write(f"{p[0]}\t{p[1]}\t{p[2]}\t{p[5]}\t{p[7]}\t{total}\t"
                 + "\t".join(str(per.get(c, 0)) for c in codes) + "\n")

scored.sort(reverse=True)
live = [s for s in scored if s[0] > 0]
print(f"\nВсего ключей {len(scored)}, с реальной частотой {len(live)}, объём {sum(s[0] for s in live)}/мес")
by_topic = defaultdict(int); cnt = defaultdict(int)
for total, kw, lang, topic in scored:
    by_topic[topic] += total
    if total: cnt[topic] += 1
print("\nПо темам:")
for name, v in sorted(by_topic.items(), key=lambda kv: -kv[1]):
    print(f"  {name:<16} {v:>8}/мес,  живых ключей {cnt[name]}")
print("\nТоп-15:")
for total, kw, lang, topic in scored[:15]:
    print(f"  {total:>6}/мес [{lang}] {topic:<14} {kw[:50]}")
