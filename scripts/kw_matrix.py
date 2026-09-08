#!/usr/bin/env python
"""Частотность турецких запросов по каждой стране отдельно.

Люди, ищущие недвижимость в Турции, живут не в Турции — поэтому меряем
спрос в каждой стране по отдельности, а не суммой. Только чтение.
"""
import io, os, time
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from google.oauth2 import service_account

CID = "3432200766"
COUNTRIES = [
    ("RU", 2643, "Россия"), ("UA", 2804, "Украина"), ("KZ", 2398, "Казахстан"),
    ("BY", 2112, "Беларусь"), ("PL", 2616, "Польша"), ("DE", 2276, "Германия"),
    ("CZ", 2203, "Чехия"), ("IL", 2376, "Израиль"), ("US", 2840, "США"),
    ("CA", 2124, "Канада"), ("GB", 2826, "Британия"), ("TR", 2792, "Турция"),
    ("AE", 2784, "ОАЭ"), ("GE", 2268, "Грузия"), ("MD", 2498, "Молдова"),
    ("LV", 2428, "Латвия"), ("LT", 2440, "Литва"), ("EE", 2233, "Эстония"),
    ("AZ", 2031, "Азербайджан"), ("UZ", 2860, "Узбекистан"), ("ES", 2724, "Испания"),
    ("IT", 2380, "Италия"), ("NL", 2528, "Нидерланды"), ("AT", 2040, "Австрия"),
    ("CH", 2756, "Швейцария"), ("SK", 2703, "Словакия"), ("HU", 2348, "Венгрия"),
    ("RO", 2642, "Румыния"), ("BG", 2100, "Болгария"), ("FI", 2246, "Финляндия"),
    ("SE", 2752, "Швеция"),
]

keywords = []
with io.open("data/ads/semantics-turkey.tsv", encoding="utf-8") as fh:
    next(fh)
    for line in fh:
        kw, lang, vol, comp, bid = line.rstrip("\n").split("\t")
        if lang == "ru" and int(vol) > 0:
            keywords.append(kw)
keywords = keywords[:1800]
print(f"Запросов в замере: {len(keywords)}, стран: {len(COUNTRIES)}")

client = GoogleAdsClient(
    credentials=service_account.Credentials.from_service_account_file(
        ".secrets/gstar-sa.json", scopes=["https://www.googleapis.com/auth/adwords"]),
    developer_token="t8wOf5cvS7HV5V7gjHnH2w", login_customer_id="8522851042",
    version="v22", use_proto_plus=True)
service = client.get_service("KeywordPlanIdeaService")

matrix = {kw: {} for kw in keywords}
for code, geo, name in COUNTRIES:
    request = client.get_type("GenerateKeywordHistoricalMetricsRequest")
    request.customer_id = CID
    request.keywords.extend(keywords)
    request.language = "languageConstants/1031"
    request.geo_target_constants = [f"geoTargetConstants/{geo}"]
    request.keyword_plan_network = client.enums.KeywordPlanNetworkEnum.GOOGLE_SEARCH
    got = None
    for attempt in range(5):
        try:
            got = service.generate_keyword_historical_metrics(request=request)
            break
        except GoogleAdsException as err:
            msgs = "; ".join(e.message for e in err.failure.errors)
            if "Too many requests" in msgs:
                time.sleep(8 * (attempt + 1)); continue
            print(f"  {name}: ошибка {msgs[:90]}"); break
        except Exception as err:
            if "RESOURCE_EXHAUSTED" in str(err) or "429" in str(err):
                time.sleep(8 * (attempt + 1)); continue
            print(f"  {name}: сбой {str(err)[:90]}"); break
    total = 0
    if got:
        for res in got.results:
            v = res.keyword_metrics.avg_monthly_searches or 0
            if v and res.text in matrix:
                matrix[res.text][code] = v
                total += v
    print(f"  {name:<12} {code}: суммарно {total}/мес")
    time.sleep(2)

os.makedirs("data/ads", exist_ok=True)
codes = [c[0] for c in COUNTRIES]
with io.open("data/ads/turkey-by-country.tsv", "w", encoding="utf-8") as fh:
    fh.write("keyword\ttotal\t" + "\t".join(codes) + "\n")
    ordered = sorted(matrix.items(), key=lambda kv: -sum(kv[1].values()))
    for kw, per in ordered:
        if not per:
            continue
        fh.write(f"{kw}\t{sum(per.values())}\t" + "\t".join(str(per.get(c, 0)) for c in codes) + "\n")
print("\nФайл: data/ads/turkey-by-country.tsv")
