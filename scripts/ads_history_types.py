#!/usr/bin/env python
"""Типы кампаний и периоды открутки. Только чтение."""
from collections import defaultdict
from google.ads.googleads.client import GoogleAdsClient
from google.oauth2 import service_account

client = GoogleAdsClient(
    credentials=service_account.Credentials.from_service_account_file(
        ".secrets/gstar-sa.json", scopes=["https://www.googleapis.com/auth/adwords"]),
    developer_token="t8wOf5cvS7HV5V7gjHnH2w", login_customer_id="8522851042",
    version="v22", use_proto_plus=True)
ga = client.get_service("GoogleAdsService")

def run(q):
    return list(ga.search(customer_id="3432200766", query=q))

print("=== Каналы за всю историю ===")
types = defaultdict(lambda: [0, 0.0])
for row in run("""
    SELECT campaign.advertising_channel_type, metrics.impressions, metrics.cost_micros
    FROM campaign WHERE segments.date BETWEEN '2023-01-01' AND '2026-09-08'
"""):
    t = types[row.campaign.advertising_channel_type.name]
    t[0] += row.metrics.impressions
    t[1] += row.metrics.cost_micros / 1_000_000
for name, (imp, cost) in sorted(types.items(), key=lambda kv: -kv[1][1]):
    print(f"  {name:<20} показов {imp:>8}, расход ${cost:>10.2f}")

print("\n=== Когда крутился Performance Max (в Ad Grants он запрещён) ===")
pmax = defaultdict(float)
for row in run("""
    SELECT segments.month, metrics.cost_micros, campaign.advertising_channel_type
    FROM campaign
    WHERE campaign.advertising_channel_type = 'PERFORMANCE_MAX'
      AND segments.date BETWEEN '2023-01-01' AND '2026-09-08'
"""):
    pmax[str(row.segments.month)] += row.metrics.cost_micros / 1_000_000
for month in sorted(pmax):
    if pmax[month] > 0:
        print(f"  {month}: ${pmax[month]:.2f}")

print("\n=== Последний месяц с реальным расходом по каналам ===")
last = defaultdict(str)
for row in run("""
    SELECT segments.month, campaign.advertising_channel_type, metrics.cost_micros
    FROM campaign WHERE segments.date BETWEEN '2023-01-01' AND '2026-09-08'
"""):
    if row.metrics.cost_micros > 0:
        name = row.campaign.advertising_channel_type.name
        month = str(row.segments.month)
        if month > last[name]:
            last[name] = month
for name, month in sorted(last.items()):
    print(f"  {name}: последний расход {month}")
