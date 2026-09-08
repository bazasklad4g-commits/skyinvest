#!/usr/bin/env python
"""Проверка, принимает ли Google Ads API наш service account."""
import os

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from google.oauth2 import service_account

KEY = os.environ.get("GOOGLE_SA_KEY", ".secrets/gstar-sa.json")
DEVELOPER_TOKEN = "t8wOf5cvS7HV5V7gjHnH2w"
LOGIN_CID = "8522851042"
CUSTOMER_ID = "3432200766"

credentials = service_account.Credentials.from_service_account_file(
    KEY, scopes=["https://www.googleapis.com/auth/adwords"]
)
client = GoogleAdsClient(
    credentials=credentials,
    developer_token=DEVELOPER_TOKEN,
    login_customer_id=LOGIN_CID,
    version="v22",
    use_proto_plus=True,
)

service = client.get_service("GoogleAdsService")
query = """
    SELECT customer.id, customer.descriptive_name, customer.currency_code,
           customer.time_zone, customer.test_account, customer.manager
    FROM customer
    LIMIT 1
"""
try:
    for row in service.search(customer_id=CUSTOMER_ID, query=query):
        c = row.customer
        print(f"Аккаунт: {c.descriptive_name} ({c.id})")
        print(f"  валюта {c.currency_code}, пояс {c.time_zone}, тестовый: {c.test_account}")
except GoogleAdsException as err:
    print(f"GoogleAdsException, request_id={err.request_id}")
    for failure in err.failure.errors:
        print(f"  {failure.error_code}: {failure.message}")
except Exception as err:  # noqa: BLE001
    print("Ошибка:", str(err)[:600].replace("\n", " "))
