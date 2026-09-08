#!/usr/bin/env python
"""Текущее состояние аккаунта Google Ads: кампании, бюджеты, конверсии. Только чтение."""
import os
import sys

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from google.oauth2 import service_account

DAYS = sys.argv[1] if len(sys.argv) > 1 else "30"
CUSTOMER_ID = os.environ.get("ADS_CUSTOMER_ID", "3432200766")

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
service = client.get_service("GoogleAdsService")


def run(query):
    return list(service.search(customer_id=CUSTOMER_ID, query=query))


print(f"=== Кампании (метрики за {DAYS} дней) ===")
rows = run(f"""
    SELECT campaign.id, campaign.name, campaign.status,
           campaign.advertising_channel_type, campaign.bidding_strategy_type,
           campaign_budget.id, campaign_budget.amount_micros,
           metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions
    FROM campaign
    WHERE segments.date DURING LAST_{DAYS}_DAYS
    ORDER BY campaign.status, campaign.name
""")
enabled = 0
for row in rows:
    c, b, m = row.campaign, row.campaign_budget, row.metrics
    status = c.status.name
    if status == "ENABLED":
        enabled += 1
    print(f"[{status}] {c.name} (id={c.id})")
    print(f"    {c.advertising_channel_type.name}, {c.bidding_strategy_type.name}, "
          f"бюджет {b.amount_micros / 1_000_000:.2f}/день (id={b.id})")
    print(f"    показов {m.impressions}, кликов {m.clicks}, "
          f"расход {m.cost_micros / 1_000_000:.2f}, конверсий {m.conversions:.1f}")
print(f"\nВсего кампаний с данными: {len(rows)}, из них ENABLED: {enabled}")

print("\n=== Все кампании по статусу (без фильтра дат) ===")
counts = {}
for row in run("SELECT campaign.status FROM campaign"):
    counts[row.campaign.status.name] = counts.get(row.campaign.status.name, 0) + 1
for status, count in sorted(counts.items()):
    print(f"  {status}: {count}")

print("\n=== Действия-конверсии ===")
for row in run("""
    SELECT conversion_action.id, conversion_action.name, conversion_action.status,
           conversion_action.type, conversion_action.category,
           conversion_action.primary_for_goal, conversion_action.counting_type
    FROM conversion_action
    ORDER BY conversion_action.name
"""):
    a = row.conversion_action
    print(f"[{a.status.name}] {a.name} (id={a.id})")
    print(f"    тип {a.type_.name}, категория {a.category.name}, "
          f"учёт {a.counting_type.name}, primary_for_goal={a.primary_for_goal}")

print(f"\n=== Итог по аккаунту за {DAYS} дней ===")
for row in run(f"""
    SELECT metrics.impressions, metrics.clicks, metrics.cost_micros,
           metrics.conversions, metrics.ctr, metrics.average_cpc
    FROM customer
    WHERE segments.date DURING LAST_{DAYS}_DAYS
"""):
    m = row.metrics
    print(f"показов {m.impressions}, кликов {m.clicks}, CTR {m.ctr * 100:.2f}%, "
          f"расход {m.cost_micros / 1_000_000:.2f}, конверсий {m.conversions:.1f}")
