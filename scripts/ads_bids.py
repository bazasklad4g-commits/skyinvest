#!/usr/bin/env python
"""Ставки и потеря показов. Только чтение."""
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


def run(query, cid="3432200766"):
    return list(service.search(customer_id=cid, query=query))


print("=== Ставки групп во включённых кампаниях ===")
bids = {}
for row in run("""
    SELECT ad_group.cpc_bid_micros, ad_group.name, campaign.name
    FROM ad_group
    WHERE campaign.status = 'ENABLED' AND ad_group.status = 'ENABLED'
"""):
    bid = row.ad_group.cpc_bid_micros / 1_000_000
    bids[bid] = bids.get(bid, 0) + 1
for bid, count in sorted(bids.items()):
    print(f"  ставка {bid:.2f}: групп {count}")

print("\n=== Управляющий аккаунт ===")
for row in run("SELECT customer_client.id, customer_client.descriptive_name, customer_client.manager, customer_client.level FROM customer_client", cid="8522851042")[:10]:
    c = row.customer_client
    print(f"  {c.descriptive_name} ({c.id}) manager={c.manager} level={c.level}")

print("\n=== Потеря показов за 90 дней (включённые кампании) ===")
for row in run("""
    SELECT campaign.name, metrics.impressions,
           metrics.search_impression_share, metrics.search_rank_lost_impression_share,
           metrics.search_budget_lost_impression_share
    FROM campaign
    WHERE campaign.status = 'ENABLED' AND segments.date BETWEEN '2026-05-29' AND '2026-08-27'
    ORDER BY metrics.impressions DESC
    LIMIT 8
"""):
    m = row.metrics
    print(f"{row.campaign.name}: показов {m.impressions}, "
          f"доля показов {m.search_impression_share:.3f}, "
          f"потеряно по рангу {m.search_rank_lost_impression_share:.3f}, "
          f"по бюджету {m.search_budget_lost_impression_share:.3f}")
