#!/usr/bin/env python
"""Проверка доступа к Keyword Planner."""
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from google.oauth2 import service_account

client = GoogleAdsClient(
    credentials=service_account.Credentials.from_service_account_file(
        ".secrets/gstar-sa.json", scopes=["https://www.googleapis.com/auth/adwords"]),
    developer_token="t8wOf5cvS7HV5V7gjHnH2w", login_customer_id="8522851042",
    version="v22", use_proto_plus=True)

service = client.get_service("KeywordPlanIdeaService")
request = client.get_type("GenerateKeywordIdeasRequest")
request.customer_id = "3432200766"
request.language = "languageConstants/1031"
request.geo_target_constants = ["geoTargetConstants/2804"]
request.include_adult_keywords = False
request.keyword_plan_network = (
    client.enums.KeywordPlanNetworkEnum.GOOGLE_SEARCH
)
request.keyword_seed.keywords.extend([
    "как проверить застройщика", "документы на недвижимость за рубежом"
])

try:
    response = service.generate_keyword_ideas(request=request)
    rows = list(response)
    print(f"Идей получено: {len(rows)}\n")
    for idea in rows[:15]:
        m = idea.keyword_idea_metrics
        print(f"  {m.avg_monthly_searches or 0:>7}/мес  конкуренция {m.competition.name:<12} {idea.text}")
except GoogleAdsException as err:
    print("Отклонено:")
    for e in err.failure.errors:
        print(f"  {e.error_code}: {e.message}")
