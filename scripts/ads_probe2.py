#!/usr/bin/env python
"""Уточнение: кампания через временный ресурс бюджета и потолок ставки. validate_only."""
import os

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from google.api_core import protobuf_helpers
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
enums = client.enums

print("=== Кампания + бюджет одной пачкой (GoogleAdsService.mutate, validate_only) ===")
budget_op = client.get_type("MutateOperation")
b = budget_op.campaign_budget_operation.create
b.resource_name = "customers/%s/campaignBudgets/-1" % CID
b.name = "PROBE budget"
b.amount_micros = 50_000_000
b.delivery_method = enums.BudgetDeliveryMethodEnum.STANDARD
b.explicitly_shared = False

camp_op = client.get_type("MutateOperation")
c = camp_op.campaign_operation.create
c.name = "PROBE campaign"
c.advertising_channel_type = enums.AdvertisingChannelTypeEnum.SEARCH
c.status = enums.CampaignStatusEnum.PAUSED
c.campaign_budget = b.resource_name
c.manual_cpc.enhanced_cpc_enabled = False
c.network_settings.target_google_search = True
c.network_settings.target_search_network = False
c.network_settings.target_content_network = False
c.contains_eu_political_advertising = (
    enums.EuPoliticalAdvertisingStatusEnum.DOES_NOT_CONTAIN_EU_POLITICAL_ADVERTISING
)
c.start_date = "2026-09-01"
c.end_date = "2037-12-30"

request = client.get_type("MutateGoogleAdsRequest")
request.customer_id = CID
request.mutate_operations = [budget_op, camp_op]
request.validate_only = True
try:
    ga.mutate(request=request)
    print("  РАЗРЕШЕНО  создание кампании вместе с её бюджетом")
except GoogleAdsException as err:
    for e in err.failure.errors:
        path = ".".join(x.field_name for x in e.location.field_path_elements)
        print(f"  ОТКЛОНЕНО: {e.message} | поле: {path} | код: {e.error_code}")

print("\n=== Потолок ставки в группе ===")
adgroup_rn = None
for row in ga.search(customer_id=CID, query="""
    SELECT ad_group.resource_name FROM ad_group
    WHERE campaign.status = 'ENABLED' AND ad_group.status = 'ENABLED' LIMIT 1
"""):
    adgroup_rn = row.ad_group.resource_name

service = client.get_service("AdGroupService")
for amount in (2_000_000, 2_010_000, 3_000_000, 10_000_000):
    op = client.get_type("AdGroupOperation")
    g = op.update
    g.resource_name = adgroup_rn
    g.cpc_bid_micros = amount
    client.copy_from(op.update_mask, protobuf_helpers.field_mask(None, g._pb))
    request = client.get_type("MutateAdGroupsRequest")
    request.customer_id = CID
    request.operations = [op]
    request.validate_only = True
    try:
        service.mutate_ad_groups(request=request)
        print(f"  ${amount/1_000_000:>5.2f}  принята")
    except GoogleAdsException as err:
        print(f"  ${amount/1_000_000:>5.2f}  отклонена: "
              + "; ".join(e.message for e in err.failure.errors)[:120])
