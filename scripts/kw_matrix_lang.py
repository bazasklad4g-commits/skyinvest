#!/usr/bin/env python
"""Матрица «запрос × страна» для украинского и английского. Только чтение."""
import io, sys, time
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from google.oauth2 import service_account

CID = "3432200766"
LANG = sys.argv[1]

MARKS = {
    "uk": ["туреччин", "аланії", "аланія", "анталії", "анталія", "стамбул", "мерсін", "бодрум",
           "кемер", "ізмір", "махмутлар", "фетхіє", "мармаріс", "сіде", "белек", "кушадаси",
           "бурс", "анкар", "трабзон", "ікамет", "тапу"],
    "en": ["turkey", "turkish", "turkiye", "alanya", "antalya", "istanbul", "mersin", "bodrum",
           "kemer", "izmir", "mahmutlar", "fethiye", "marmaris", "belek", "kusadasi", "bursa",
           "ankara", "trabzon", "ikamet", "tapu", "didim", "altinkum", "oba ", "cesme"],
}
COUNTRIES = {
    "uk": [("UA",2804,"Украина"),("PL",2616,"Польша"),("DE",2276,"Германия"),("CZ",2203,"Чехия"),
           ("IT",2380,"Италия"),("ES",2724,"Испания"),("GB",2826,"Британия"),("US",2840,"США"),
           ("CA",2124,"Канада"),("PT",2620,"Португалия"),("NL",2528,"Нидерланды"),("TR",2792,"Турция")],
    "en": [("GB",2826,"Британия"),("US",2840,"США"),("DE",2276,"Германия"),("NL",2528,"Нидерланды"),
           ("TR",2792,"Турция"),("AE",2784,"ОАЭ"),("CA",2124,"Канада"),("IE",2372,"Ирландия"),
           ("AU",2036,"Австралия"),("IL",2376,"Израиль"),("SA",2682,"Саудовская Аравия"),
           ("QA",2634,"Катар"),("KW",2414,"Кувейт"),("IN",2356,"Индия"),("ZA",2710,"ЮАР"),
           ("SG",2702,"Сингапур"),("BE",2056,"Бельгия"),("SE",2752,"Швеция"),("NO",2578,"Норвегия"),
           ("DK",2208,"Дания"),("FI",2246,"Финляндия"),("CH",2756,"Швейцария"),("AT",2040,"Австрия"),
           ("FR",2250,"Франция"),("GR",2300,"Греция"),("CY",2196,"Кипр"),("MY",2458,"Малайзия"),
           ("NZ",2554,"Новая Зеландия"),("PL",2616,"Польша"),("RO",2642,"Румыния")],
}
LANG_ID = {"uk": 1036, "en": 1000}

keywords = []
with io.open(f"data/ads/semantics-turkey-{LANG}.tsv", encoding="utf-8") as fh:
    next(fh)
    for line in fh:
        kw, vol, comp = line.rstrip("\n").split("\t")
        low = kw.lower()
        if int(vol) > 0 and any(m in low for m in MARKS[LANG]):
            keywords.append(kw)
keywords = keywords[:1800]
countries = COUNTRIES[LANG]
print(f"{LANG}: в замере {len(keywords)} запросов по теме Турции, стран {len(countries)}")

client = GoogleAdsClient(
    credentials=service_account.Credentials.from_service_account_file(
        ".secrets/gstar-sa.json", scopes=["https://www.googleapis.com/auth/adwords"]),
    developer_token="t8wOf5cvS7HV5V7gjHnH2w", login_customer_id="8522851042",
    version="v22", use_proto_plus=True)
service = client.get_service("KeywordPlanIdeaService")

matrix = {kw: {} for kw in keywords}
for code, geo, name in countries:
    request = client.get_type("GenerateKeywordHistoricalMetricsRequest")
    request.customer_id = CID
    request.keywords.extend(keywords)
    request.language = f"languageConstants/{LANG_ID[LANG]}"
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
            print(f"  {name}: {msgs[:80]}"); break
        except Exception as err:
            if "RESOURCE_EXHAUSTED" in str(err) or "429" in str(err):
                time.sleep(8 * (attempt + 1)); continue
            print(f"  {name}: {str(err)[:80]}"); break
    total = 0
    if got:
        for res in got.results:
            v = res.keyword_metrics.avg_monthly_searches or 0
            if v and res.text in matrix:
                matrix[res.text][code] = v
                total += v
    print(f"  {name:<18} {code}: {total}/мес")
    time.sleep(2)

codes = [c[0] for c in countries]
path = f"data/ads/turkey-by-country-{LANG}.tsv"
with io.open(path, "w", encoding="utf-8") as fh:
    fh.write("keyword\ttotal\t" + "\t".join(codes) + "\n")
    for kw, per in sorted(matrix.items(), key=lambda kv: -sum(kv[1].values())):
        if per:
            fh.write(f"{kw}\t{sum(per.values())}\t" + "\t".join(str(per.get(c, 0)) for c in codes) + "\n")
grand = sum(sum(p.values()) for p in matrix.values())
print(f"\nИтого {LANG}: {grand}/мес. Файл: {path}")
