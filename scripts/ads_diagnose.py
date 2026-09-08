#!/usr/bin/env python
"""Почему включённые кампании не показываются. Только чтение."""
import os

from google.ads.googleads.client import GoogleAdsClient
from google.oauth2 import service_account

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
CID = "3432200766"


def run(query):
    return list(service.search(customer_id=CID, query=query))


print("=== Статус аккаунта ===")
for row in run("""
    SELECT customer.id, customer.status, customer.descriptive_name,
           customer.currency_code, customer.time_zone, customer.pay_per_conversion_eligibility_failure_reasons
    FROM customer
"""):
    c = row.customer
    print(f"{c.descriptive_name}: статус {c.status.name}, {c.currency_code}, {c.time_zone}")

print("\n=== Включённые кампании: статус показа ===")
for row in run("""
    SELECT campaign.id, campaign.name, campaign.serving_status,
           campaign.primary_status, campaign.primary_status_reasons,
           campaign.start_date, campaign.end_date, campaign_budget.amount_micros
    FROM campaign
    WHERE campaign.status = 'ENABLED'
    ORDER BY campaign.name
"""):
    c = row.campaign
    reasons = ", ".join(r.name for r in c.primary_status_reasons) or "нет замечаний"
    print(f"{c.name} (id={c.id})")
    print(f"    показ: {c.serving_status.name}, состояние: {c.primary_status.name}")
    print(f"    причины: {reasons}")
    print(f"    период {c.start_date} — {c.end_date}, бюджет {row.campaign_budget.amount_micros/1_000_000:.0f}")

print("\n=== Объявления: статус модерации ===")
verdicts = {}
for row in run("""
    SELECT ad_group_ad.ad.id, ad_group_ad.status, ad_group_ad.policy_summary.approval_status,
           ad_group_ad.policy_summary.review_status, campaign.status
    FROM ad_group_ad
    WHERE campaign.status = 'ENABLED' AND ad_group_ad.status = 'ENABLED'
"""):
    a = row.ad_group_ad
    key = (a.policy_summary.approval_status.name, a.policy_summary.review_status.name)
    verdicts[key] = verdicts.get(key, 0) + 1
if not verdicts:
    print("  во включённых кампаниях нет ни одного включённого объявления")
for (approval, review), count in sorted(verdicts.items()):
    print(f"  модерация {approval}, проверка {review}: {count}")

print("\n=== Группы объявлений во включённых кампаниях ===")
groups = {}
for row in run("""
    SELECT ad_group.status, campaign.status FROM ad_group WHERE campaign.status = 'ENABLED'
"""):
    key = row.ad_group.status.name
    groups[key] = groups.get(key, 0) + 1
for status, count in sorted(groups.items()):
    print(f"  {status}: {count}")

print("\n=== Ключевые слова: статус ===")
kw = {}
for row in run("""
    SELECT ad_group_criterion.status, ad_group_criterion.approval_status,
           ad_group_criterion.system_serving_status, campaign.status
    FROM keyword_view
    WHERE campaign.status = 'ENABLED'
"""):
    c = row.ad_group_criterion
    key = (c.status.name, c.system_serving_status.name)
    kw[key] = kw.get(key, 0) + 1
for (status, serving), count in sorted(kw.items()):
    print(f"  {status} / {serving}: {count}")
