"""Чем кампании 2024 года отличались от нынешних. Только чтение."""
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

print("=== Типы соответствия ключей, дававших клики в 2024 ===")
match = defaultdict(lambda: [0, 0])
for row in run("""
    SELECT ad_group_criterion.keyword.match_type, metrics.impressions, metrics.clicks
    FROM keyword_view
    WHERE segments.date BETWEEN '2024-01-01' AND '2024-12-31'
"""):
    m = match[row.ad_group_criterion.keyword.match_type.name]
    m[0] += row.metrics.impressions
    m[1] += row.metrics.clicks
for name, (i, c) in sorted(match.items(), key=lambda kv: -kv[1][1]):
    print(f"  {name:<10} показов {i:>8}, кликов {c:>6}")

print("\n=== Топ-15 ключей 2024 по кликам ===")
kws = defaultdict(lambda: [0, 0, 0.0])
for row in run("""
    SELECT ad_group_criterion.keyword.text, ad_group_criterion.keyword.match_type,
           metrics.impressions, metrics.clicks, metrics.conversions
    FROM keyword_view
    WHERE segments.date BETWEEN '2024-01-01' AND '2024-12-31'
      AND metrics.clicks > 0
"""):
    k = row.ad_group_criterion.keyword
    key = f"{k.text}|{k.match_type.name}"
    v = kws[key]
    v[0] += row.metrics.impressions
    v[1] += row.metrics.clicks
    v[2] += row.metrics.conversions
for key, (i, c, conv) in sorted(kws.items(), key=lambda kv: -kv[1][1])[:15]:
    text, mt = key.rsplit("|", 1)
    print(f"  {c:>5} кликов, {i:>7} показов, конв {conv:>5.1f}  [{mt:<6}] {text[:50]}")

print("\n=== Стратегии ставок кампаний, дававших клики в 2024 ===")
strat = defaultdict(int)
for row in run("""
    SELECT campaign.bidding_strategy_type, metrics.clicks
    FROM campaign
    WHERE segments.date BETWEEN '2024-01-01' AND '2024-12-31' AND metrics.clicks > 0
"""):
    strat[row.campaign.bidding_strategy_type.name] += row.metrics.clicks
for name, c in sorted(strat.items(), key=lambda kv: -kv[1]):
    print(f"  {name:<28} кликов {c}")
