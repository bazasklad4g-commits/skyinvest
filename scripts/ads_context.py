#!/usr/bin/env python
"""Существующие ключи и настройки таргетинга. Только чтение."""
import os

from google.ads.googleads.client import GoogleAdsClient
from google.oauth2 import service_account

CID = "3432200766"
client = GoogleAdsClient(
    credentials=service_account.Credentials.from_service_account_file(
        os.environ.get("GOOGLE_SA_KEY", ".secrets/gstar-sa.json"),
        scopes=["https://www.googleapis.com/auth/adwords"],
    ),
    developer_token="t8wOf5cvS7HV5V7gjHnH2w",
    login_customer_id="8522851042",
    version="v22",
    use_proto_plus=True,
)
ga = client.get_service("GoogleAdsService")


def run(q):
    return list(ga.search(customer_id=CID, query=q))


print("=== Ключи во включённых кампаниях ===")
for row in run("""
    SELECT campaign.name, ad_group_criterion.keyword.text,
           ad_group_criterion.keyword.match_type, ad_group_criterion.status
    FROM keyword_view
    WHERE campaign.status = 'ENABLED' AND ad_group_criterion.status = 'ENABLED'
    ORDER BY campaign.name
"""):
    k = row.ad_group_criterion.keyword
    print(f"  [{row.campaign.name[:38]:38}] {k.match_type.name[:6]:6} {k.text}")

print("\n=== Гео и язык эталонной кампании EDU | Выбор страны (24072276861) ===")
for row in run("""
    SELECT campaign_criterion.type, campaign_criterion.negative,
           campaign_criterion.location.geo_target_constant,
           campaign_criterion.language.language_constant,
           campaign_criterion.keyword.text, campaign_criterion.keyword.match_type
    FROM campaign_criterion
    WHERE campaign.id = 24072276861
"""):
    c = row.campaign_criterion
    kind = c.type_.name
    if kind == "LOCATION":
        print(f"  гео: {c.location.geo_target_constant}")
    elif kind == "LANGUAGE":
        print(f"  язык: {c.language.language_constant}")
    elif kind == "KEYWORD" and c.negative:
        print(f"  минус: [{c.keyword.match_type.name}] {c.keyword.text}")
    else:
        print(f"  {kind} negative={c.negative}")

print("\n=== Настройки этой же кампании ===")
for row in run("""
    SELECT campaign.name, campaign.bidding_strategy_type, campaign.start_date,
           campaign.network_settings.target_google_search,
           campaign.network_settings.target_search_network,
           campaign.network_settings.target_content_network,
           campaign.geo_target_type_setting.positive_geo_target_type,
           campaign_budget.amount_micros, campaign_budget.explicitly_shared
    FROM campaign WHERE campaign.id = 24072276861
"""):
    c = row.campaign
    print(f"  стратегия {c.bidding_strategy_type.name}, старт {c.start_date}")
    print(f"  сети: search={c.network_settings.target_google_search}, "
          f"partners={c.network_settings.target_search_network}, "
          f"display={c.network_settings.target_content_network}")
    print(f"  тип гео: {c.geo_target_type_setting.positive_geo_target_type.name}")
    print(f"  бюджет {row.campaign_budget.amount_micros/1_000_000:.0f}, "
          f"общий={row.campaign_budget.explicitly_shared}")
