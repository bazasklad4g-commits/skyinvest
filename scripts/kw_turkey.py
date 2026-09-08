#!/usr/bin/env python
"""Семантика по Турции: недвижимость, переезд, ПМЖ, новостройки, по городам.

Только чтение. Результат в data/ads/semantics-turkey.tsv
"""
import os
import time

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from google.oauth2 import service_account

CID = "3432200766"
GEO = [2792, 2804, 2616, 2276, 2203, 2376, 2840, 2826, 2724, 2784]  # TR UA PL DE CZ IL US GB ES AE

CITIES_RU = ["алании", "анталии", "стамбуле", "измире", "бодруме", "фетхие", "мерсине",
             "кемере", "сиде", "белеке", "мармарисе", "кушадасы", "бурсе", "анкаре", "трабзоне"]
CITIES_UK = ["аланії", "анталії", "стамбулі", "ізмірі", "бодрумі", "фетхіє", "мерсіні",
             "кемері", "сіде", "белеку", "мармарісі"]

def chunk(items, size):
    return [items[i:i + size] for i in range(0, len(items), size)]

SEEDS = {1031: [], 1036: []}

SEEDS[1031] += [
    ["недвижимость в турции", "купить квартиру в турции", "апартаменты в турции",
     "новостройки в турции", "квартира в новостройке турция"],
    ["эмиграция в турцию", "переезд в турцию", "пмж в турции",
     "вид на жительство в турции", "гражданство турции"],
    ["жизнь в турции", "переехать в турцию на пмж", "икамет в турции",
     "как получить вэ в турции", "türkiye пмж"],
]
for group in chunk(CITIES_RU, 5):
    SEEDS[1031].append([f"недвижимость в {c}" for c in group])
for group in chunk(CITIES_RU[:10], 5):
    SEEDS[1031].append([f"квартира в {c}" for c in group])

SEEDS[1036] += [
    ["нерухомість в туреччині", "купити квартиру в туреччині", "апартаменти в туреччині",
     "новобудови в туреччині", "квартира в новобудові туреччина"],
    ["еміграція в туреччину", "переїзд до туреччини", "пмж в туреччині",
     "посвідка на проживання в туреччині", "громадянство туреччини"],
]
for group in chunk(CITIES_UK, 6):
    SEEDS[1036].append([f"нерухомість в {c}" for c in group])

client = GoogleAdsClient(
    credentials=service_account.Credentials.from_service_account_file(
        ".secrets/gstar-sa.json", scopes=["https://www.googleapis.com/auth/adwords"]),
    developer_token="t8wOf5cvS7HV5V7gjHnH2w", login_customer_id="8522851042",
    version="v22", use_proto_plus=True)
service = client.get_service("KeywordPlanIdeaService")

rows = {}
total_batches = sum(len(v) for v in SEEDS.values())
done = 0
for lang, batches in SEEDS.items():
    for batch in batches:
        done += 1
        request = client.get_type("GenerateKeywordIdeasRequest")
        request.customer_id = CID
        request.language = f"languageConstants/{lang}"
        request.geo_target_constants = [f"geoTargetConstants/{g}" for g in GEO]
        request.include_adult_keywords = False
        request.keyword_plan_network = client.enums.KeywordPlanNetworkEnum.GOOGLE_SEARCH
        request.keyword_seed.keywords.extend(batch)
        ideas = []
        for attempt in range(5):
            try:
                ideas = list(service.generate_keyword_ideas(request=request))
                break
            except GoogleAdsException as err:
                msgs = "; ".join(e.message for e in err.failure.errors)
                if "Too many requests" in msgs:
                    time.sleep(8 * (attempt + 1)); continue
                print(f"  ошибка [{batch[0]}]: {msgs[:110]}"); break
            except Exception as err:
                if "RESOURCE_EXHAUSTED" in str(err) or "429" in str(err):
                    time.sleep(8 * (attempt + 1)); continue
                print(f"  сбой [{batch[0]}]: {str(err)[:110]}"); break
        for idea in ideas:
            m = idea.keyword_idea_metrics
            key = (idea.text, lang)
            vol = m.avg_monthly_searches or 0
            if key not in rows or vol > rows[key][0]:
                rows[key] = (vol, m.competition.name,
                             (m.high_top_of_page_bid_micros or 0) / 1_000_000)
        print(f"  пачка {done}/{total_batches}: {batch[0][:38]} -> всего {len(rows)}")
        time.sleep(3)

os.makedirs("data/ads", exist_ok=True)
names = {1031: "ru", 1036: "uk"}
with open("data/ads/semantics-turkey.tsv", "w", encoding="utf-8") as fh:
    fh.write("keyword\tlang\tsearches\tcompetition\tbid_high\n")
    for (text, lang), (vol, comp, bid) in sorted(rows.items(), key=lambda kv: -kv[1][0]):
        fh.write(f"{text}\t{names[lang]}\t{vol}\t{comp}\t{bid:.2f}\n")

print(f"\nСобрано: {len(rows)}")
for lang in names:
    n = [rows[k][0] for k in rows if k[1] == lang]
    print(f"  {names[lang]}: {len(n)} запросов, объём {sum(n)}/мес")
