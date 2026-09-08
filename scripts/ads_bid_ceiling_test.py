"""Потолок ставки: универсален ли он. Всё через validate_only, ничего не меняется."""
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from google.api_core import protobuf_helpers
from google.oauth2 import service_account

CID = "3432200766"
client = GoogleAdsClient(
    credentials=service_account.Credentials.from_service_account_file(
        ".secrets/gstar-sa.json", scopes=["https://www.googleapis.com/auth/adwords"]),
    developer_token="t8wOf5cvS7HV5V7gjHnH2w", login_customer_id="8522851042",
    version="v22", use_proto_plus=True)
ga = client.get_service("GoogleAdsService")
service = client.get_service("AdGroupService")

groups = []
for row in ga.search(customer_id=CID, query="""
    SELECT ad_group.resource_name, ad_group.name, campaign.name,
           campaign.bidding_strategy_type, campaign.status
    FROM ad_group
    WHERE ad_group.status = 'ENABLED' AND campaign.status != 'REMOVED'
    LIMIT 200
"""):
    groups.append((row.campaign.name, row.campaign.bidding_strategy_type.name,
                   row.ad_group.name, row.ad_group.resource_name))

seen = set()
picked = []
for camp, strat, name, rn in groups:
    if camp not in seen:
        seen.add(camp)
        picked.append((camp, strat, name, rn))
    if len(picked) >= 4:
        break

for camp, strat, name, rn in picked:
    print(f"\n=== {camp[:45]} [{strat}] / группа «{name[:25]}» ===")
    for amount in (2_000_000, 2_010_000, 5_000_000):
        op = client.get_type("AdGroupOperation")
        g = op.update
        g.resource_name = rn
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
            msgs = "; ".join(e.message for e in err.failure.errors)
            print(f"  ${amount/1_000_000:>5.2f}  отклонена: {msgs[:90]}")
