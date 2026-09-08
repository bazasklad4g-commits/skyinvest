#!/usr/bin/env python
"""Выгрузка всех ключей аккаунта в файл для проверки на пересечения."""
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

rows = ga.search(customer_id=CID, query="""
    SELECT campaign.name, campaign.status, ad_group_criterion.keyword.text,
           ad_group_criterion.keyword.match_type, ad_group_criterion.status
    FROM keyword_view
    WHERE campaign.status != 'REMOVED'
""")
os.makedirs("data/ads", exist_ok=True)
seen = set()
with open("data/ads/all-keywords.tsv", "w", encoding="utf-8") as fh:
    fh.write("keyword\tmatch\tcampaign\tcampaign_status\tkeyword_status\n")
    for row in rows:
        k = row.ad_group_criterion.keyword
        fh.write(f"{k.text}\t{k.match_type.name}\t{row.campaign.name}\t"
                 f"{row.campaign.status.name}\t{row.ad_group_criterion.status.name}\n")
        seen.add(k.text.lower())
print(f"Уникальных текстов ключей: {len(seen)}")
print("Файл: data/ads/all-keywords.tsv")
