#!/usr/bin/env python
"""Какие права у нашего доступа в аккаунте Google Ads."""
import os

from google.api_core import protobuf_helpers
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

print("=== Пользователи аккаунта 3432200766 ===")
try:
    for row in service.search(customer_id="3432200766", query="""
        SELECT customer_user_access.email_address, customer_user_access.access_role,
               customer_user_access.user_id
        FROM customer_user_access
    """):
        a = row.customer_user_access
        mark = "  <-- наш ключ" if "skyinvest-specialist-api" in a.email_address else ""
        print(f"  {a.email_address}: {a.access_role.name}{mark}")
except Exception as err:  # noqa: BLE001
    print("Список пользователей недоступен:", str(err)[:300].replace("\n", " "))

print("\n=== Проверка права на изменение (validate_only, ничего не меняет) ===")
campaign_service = client.get_service("CampaignService")
operation = client.get_type("CampaignOperation")
campaign = operation.update
campaign.resource_name = campaign_service.campaign_path("3432200766", "24072272106")
campaign.name = "[PAUSED] EDU | Проверка застройщика"
client.copy_from(operation.update_mask, protobuf_helpers.field_mask(None, campaign._pb))
try:
    request = client.get_type("MutateCampaignsRequest")
    request.customer_id = "3432200766"
    request.operations = [operation]
    request.validate_only = True
    campaign_service.mutate_campaigns(request=request)
    print("  Запись разрешена: сервер принял пробную мутацию (validate_only, изменений нет).")
except Exception as err:  # noqa: BLE001
    print("  Запись отклонена:", str(err)[:400].replace("\n", " "))
