#!/usr/bin/env python
"""Сбор идей по Турции на украинском и английском, городскими формулировками."""
import io, os, sys, time
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from google.oauth2 import service_account

CID = "3432200766"
LANG = sys.argv[1]

CONF = {
    "uk": {
        "id": 1036,
        "geo": [2804, 2616, 2276, 2203, 2792, 2380, 2724, 2826, 2840, 2528],
        "cities": ["аланії", "анталії", "стамбулі", "мерсіні", "бодрумі", "кемері", "ізмірі",
                    "махмутларі", "фетхіє", "мармарісі", "сіде", "белеку", "кушадаси", "бурсі",
                    "анкарі", "трабзоні"],
        "patterns": ["нерухомість в {}", "квартира в {}", "купити квартиру в {}", "апартаменти в {}"],
        "general": [
            ["нерухомість в туреччині", "купити квартиру в туреччині", "апартаменти туреччина",
             "будинок в туреччині", "вілла в туреччині"],
            ["пмж в туреччині", "посвідка на проживання туреччина", "ікамет туреччина",
             "громадянство туреччини", "переїзд до туреччини"],
            ["життя в туреччині", "оренда квартири в туреччині", "податки на нерухомість туреччина",
             "тапу туреччина", "документи на нерухомість туреччина"],
        ],
    },
    "en": {
        "id": 1000,
        "geo": [2826, 2840, 2124, 2372, 2036, 2276, 2528, 2792, 2784, 2376],
        "cities": ["alanya", "antalya", "istanbul", "mersin", "bodrum", "kemer", "izmir",
                    "mahmutlar", "fethiye", "marmaris", "side", "belek", "kusadasi", "bursa",
                    "ankara", "trabzon"],
        "patterns": ["property in {}", "apartments in {}", "buy property in {}", "real estate {}"],
        "general": [
            ["property in turkey", "buy property in turkey", "turkish real estate",
             "apartments for sale turkey", "villas in turkey"],
            ["turkey residence permit", "turkish citizenship by investment", "moving to turkey",
             "living in turkey", "ikamet turkey"],
            ["title deed turkey", "tapu turkey", "property taxes turkey",
             "cost of living in turkey", "rental yield turkey"],
        ],
    },
}
conf = CONF[LANG]

batches = list(conf["general"])
for pattern in conf["patterns"]:
    group = [pattern.format(c) for c in conf["cities"]]
    for i in range(0, len(group), 5):
        batches.append(group[i:i + 5])

client = GoogleAdsClient(
    credentials=service_account.Credentials.from_service_account_file(
        ".secrets/gstar-sa.json", scopes=["https://www.googleapis.com/auth/adwords"]),
    developer_token="t8wOf5cvS7HV5V7gjHnH2w", login_customer_id="8522851042",
    version="v22", use_proto_plus=True)
service = client.get_service("KeywordPlanIdeaService")

rows = {}
for n, batch in enumerate(batches, 1):
    request = client.get_type("GenerateKeywordIdeasRequest")
    request.customer_id = CID
    request.language = f"languageConstants/{conf['id']}"
    request.geo_target_constants = [f"geoTargetConstants/{g}" for g in conf["geo"]]
    request.include_adult_keywords = False
    request.keyword_plan_network = client.enums.KeywordPlanNetworkEnum.GOOGLE_SEARCH
    request.keyword_seed.keywords.extend(batch)
    ideas = []
    for attempt in range(5):
        try:
            ideas = list(service.generate_keyword_ideas(request=request)); break
        except GoogleAdsException as err:
            msgs = "; ".join(e.message for e in err.failure.errors)
            if "Too many requests" in msgs:
                time.sleep(8 * (attempt + 1)); continue
            print(f"  ошибка [{batch[0]}]: {msgs[:90]}"); break
        except Exception as err:
            if "RESOURCE_EXHAUSTED" in str(err) or "429" in str(err):
                time.sleep(8 * (attempt + 1)); continue
            print(f"  сбой [{batch[0]}]: {str(err)[:90]}"); break
    for idea in ideas:
        m = idea.keyword_idea_metrics
        vol = m.avg_monthly_searches or 0
        if idea.text not in rows or vol > rows[idea.text][0]:
            rows[idea.text] = (vol, m.competition.name)
    print(f"  {n}/{len(batches)} {batch[0][:34]} -> {len(rows)}")
    time.sleep(3)

os.makedirs("data/ads", exist_ok=True)
path = f"data/ads/semantics-turkey-{LANG}.tsv"
with io.open(path, "w", encoding="utf-8") as fh:
    fh.write("keyword\tsearches\tcompetition\n")
    for text, (vol, comp) in sorted(rows.items(), key=lambda kv: -kv[1][0]):
        fh.write(f"{text}\t{vol}\t{comp}\n")
nonzero = [v for v, _ in rows.values() if v > 0]
print(f"\n{LANG}: собрано {len(rows)}, с ненулевой частотой {len(nonzero)}, объём {sum(nonzero)}")
print("Файл:", path)
