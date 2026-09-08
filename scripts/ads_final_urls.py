import os
from google.ads.googleads.client import GoogleAdsClient
from google.oauth2 import service_account
client = GoogleAdsClient(
    credentials=service_account.Credentials.from_service_account_file(
        ".secrets/gstar-sa.json", scopes=["https://www.googleapis.com/auth/adwords"]),
    developer_token="t8wOf5cvS7HV5V7gjHnH2w", login_customer_id="8522851042",
    version="v22", use_proto_plus=True)
ga = client.get_service("GoogleAdsService")
seen = {}
for row in ga.search(customer_id="3432200766", query="""
    SELECT campaign.name, ad_group_ad.ad.final_urls
    FROM ad_group_ad WHERE campaign.status = 'ENABLED'
"""):
    for u in row.ad_group_ad.ad.final_urls:
        seen.setdefault(u, set()).add(row.campaign.name)
for url, camps in sorted(seen.items()):
    print(f"{url}\n    {', '.join(sorted(camps))[:150]}")
