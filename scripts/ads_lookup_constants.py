#!/usr/bin/env python
"""ID языков и регионов для Keyword Planner. Только чтение."""
import os
from google.ads.googleads.client import GoogleAdsClient
from google.oauth2 import service_account

client = GoogleAdsClient(
    credentials=service_account.Credentials.from_service_account_file(
        ".secrets/gstar-sa.json", scopes=["https://www.googleapis.com/auth/adwords"]),
    developer_token="t8wOf5cvS7HV5V7gjHnH2w", login_customer_id="8522851042",
    version="v22", use_proto_plus=True)
ga = client.get_service("GoogleAdsService")

print("=== Языки ===")
for row in ga.search(customer_id="3432200766", query="""
    SELECT language_constant.id, language_constant.code, language_constant.name
    FROM language_constant
    WHERE language_constant.code IN ('ru', 'uk', 'en')
"""):
    lc = row.language_constant
    print(f"  {lc.code}: id={lc.id} ({lc.name})")

print("\n=== Регионы ===")
for row in ga.search(customer_id="3432200766", query="""
    SELECT geo_target_constant.id, geo_target_constant.name,
           geo_target_constant.country_code, geo_target_constant.target_type
    FROM geo_target_constant
    WHERE geo_target_constant.country_code IN ('UA','PL','DE','ES','TR','AE','GE')
      AND geo_target_constant.target_type = 'Country'
"""):
    gc = row.geo_target_constant
    print(f"  {gc.country_code}: id={gc.id} ({gc.name})")
