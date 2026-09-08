#!/usr/bin/env python
"""Сбор семантики через Keyword Planner. Только чтение, ничего не меняет.

Гео — страны, где живёт русско- и украиноязычная аудитория плюс рынки,
о которых пишет сайт. Результат в data/ads/semantics-raw.tsv.
"""
import os
import time
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from google.oauth2 import service_account

CID = "3432200766"
# Keyword Planner принимает не более 10 регионов на запрос.
GEO = [2804, 2616, 2276, 2203, 2376, 2840, 2826, 2724, 2792, 2784]

SEEDS = {
    1031: [  # русский
        ["недвижимость за рубежом", "инвестиции в недвижимость", "вид на жительство через недвижимость",
         "гражданство за инвестиции", "купить квартиру за границей", "дом у моря"],
        ["как проверить застройщика", "налоги на недвижимость за рубежом", "документы при покупке недвижимости",
         "переезд в другую страну", "аренда квартиры за границей", "доходность аренды"],
        ["курсы по недвижимости", "профессия риэлтор", "работа менеджером по недвижимости",
         "обучение рекрутингу", "как стать рекрутером", "бесплатное обучение профессии"],
    ],
    1036: [  # украинский
        ["нерухомість за кордоном", "інвестиції в нерухомість", "посвідка на проживання через нерухомість",
         "купити квартиру за кордоном", "будинок біля моря", "оренда квартири за кордоном"],
        ["як перевірити забудовника", "податки на нерухомість за кордоном", "документи при купівлі нерухомості",
         "переїзд в іншу країну", "громадянство за інвестиції"],
        ["курси з нерухомості", "професія ріелтор", "робота менеджером з нерухомості",
         "навчання рекрутингу", "як стати рекрутером", "безкоштовне навчання професії"],
    ],
    1000: [  # английский
        ["property abroad", "buy property overseas", "residency by investment",
         "citizenship by investment", "overseas property investment", "house by the sea"],
        ["how to check a developer", "property taxes for non residents", "documents to buy property abroad",
         "moving to another country", "rental yield"],
        ["real estate courses", "how to become a real estate agent", "recruitment courses",
         "how to become a recruiter", "free professional training"],
    ],
}

client = GoogleAdsClient(
    credentials=service_account.Credentials.from_service_account_file(
        ".secrets/gstar-sa.json", scopes=["https://www.googleapis.com/auth/adwords"]),
    developer_token="t8wOf5cvS7HV5V7gjHnH2w", login_customer_id="8522851042",
    version="v22", use_proto_plus=True)
service = client.get_service("KeywordPlanIdeaService")

os.makedirs("data/ads", exist_ok=True)
rows = {}
for lang, batches in SEEDS.items():
    for batch in batches:
        request = client.get_type("GenerateKeywordIdeasRequest")
        request.customer_id = CID
        request.language = f"languageConstants/{lang}"
        request.geo_target_constants = [f"geoTargetConstants/{g}" for g in GEO]
        request.include_adult_keywords = False
        request.keyword_plan_network = client.enums.KeywordPlanNetworkEnum.GOOGLE_SEARCH
        request.keyword_seed.keywords.extend(batch)
        for attempt in range(5):
            try:
                ideas = list(service.generate_keyword_ideas(request=request))
                break
            except GoogleAdsException as err:
                messages = "; ".join(e.message for e in err.failure.errors)
                if "Too many requests" in messages or "Retry" in messages:
                    time.sleep(8 * (attempt + 1))
                    continue
                print("ошибка на пачке", batch[0], ":", messages[:150])
                ideas = []
                break
            except Exception as err:
                if "RESOURCE_EXHAUSTED" in str(err) or "429" in str(err):
                    time.sleep(8 * (attempt + 1))
                    continue
                print("сбой на пачке", batch[0], ":", str(err)[:150])
                ideas = []
                break
        else:
            ideas = []
        if True:
            for idea in ideas:
                m = idea.keyword_idea_metrics
                key = (idea.text, lang)
                if key not in rows or m.avg_monthly_searches > rows[key][0]:
                    rows[key] = (m.avg_monthly_searches or 0, m.competition.name,
                                 m.low_top_of_page_bid_micros / 1_000_000 if m.low_top_of_page_bid_micros else 0,
                                 m.high_top_of_page_bid_micros / 1_000_000 if m.high_top_of_page_bid_micros else 0)
        time.sleep(3)

names = {1031: "ru", 1036: "uk", 1000: "en"}
with open("data/ads/semantics-raw.tsv", "w", encoding="utf-8") as fh:
    fh.write("keyword\tlang\tsearches\tcompetition\tbid_low\tbid_high\n")
    for (text, lang), (searches, comp, low, high) in sorted(rows.items(), key=lambda kv: -kv[1][0]):
        fh.write(f"{text}\t{names[lang]}\t{searches}\t{comp}\t{low:.2f}\t{high:.2f}\n")

print(f"Собрано уникальных запросов: {len(rows)}")
for lang in names:
    n = sum(1 for k in rows if k[1] == lang)
    vol = sum(rows[k][0] for k in rows if k[1] == lang)
    print(f"  {names[lang]}: {n} запросов, суммарный объём {vol}/мес")
print("Файл: data/ads/semantics-raw.tsv")
