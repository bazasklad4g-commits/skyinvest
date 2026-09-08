#!/usr/bin/env python
"""История аккаунта: что реально откручивалось. Только чтение."""
import sys
from collections import defaultdict
from google.ads.googleads.client import GoogleAdsClient
from google.oauth2 import service_account

client = GoogleAdsClient(
    credentials=service_account.Credentials.from_service_account_file(
        ".secrets/gstar-sa.json", scopes=["https://www.googleapis.com/auth/adwords"]),
    developer_token="t8wOf5cvS7HV5V7gjHnH2w", login_customer_id="8522851042",
    version="v22", use_proto_plus=True)
ga = client.get_service("GoogleAdsService")
START = sys.argv[1] if len(sys.argv) > 1 else "2024-01-01"
END = "2026-09-08"

def run(q):
    return list(ga.search(customer_id="3432200766", query=q))

print(f"=== По месяцам с {START} ===")
months = defaultdict(lambda: [0, 0, 0.0, 0.0])
for row in run(f"""
    SELECT segments.month, metrics.impressions, metrics.clicks,
           metrics.cost_micros, metrics.conversions
    FROM campaign
    WHERE segments.date BETWEEN '{START}' AND '{END}'
"""):
    m = months[str(row.segments.month)]
    m[0] += row.metrics.impressions
    m[1] += row.metrics.clicks
    m[2] += row.metrics.cost_micros / 1_000_000
    m[3] += row.metrics.conversions
print(f"{'месяц':<12}{'показы':>10}{'клики':>9}{'расход':>11}{'конв.':>8}")
for month in sorted(months):
    i, c, cost, conv = months[month]
    print(f"{month:<12}{i:>10}{c:>9}{cost:>11.2f}{conv:>8.1f}")

print(f"\n=== Топ кампаний по кликам за весь период ===")
camps = defaultdict(lambda: [0, 0, 0.0, 0.0])
for row in run(f"""
    SELECT campaign.name, campaign.status, metrics.impressions, metrics.clicks,
           metrics.cost_micros, metrics.conversions
    FROM campaign
    WHERE segments.date BETWEEN '{START}' AND '{END}'
"""):
    key = f"{row.campaign.name}|{row.campaign.status.name}"
    c = camps[key]
    c[0] += row.metrics.impressions
    c[1] += row.metrics.clicks
    c[2] += row.metrics.cost_micros / 1_000_000
    c[3] += row.metrics.conversions
top = sorted(camps.items(), key=lambda kv: -kv[1][1])[:20]
for key, (i, c, cost, conv) in top:
    name, status = key.rsplit("|", 1)
    print(f"  {c:>6} кликов, {i:>8} показов, ${cost:>9.2f}, конв {conv:>6.1f}  [{status}] {name[:55]}")
