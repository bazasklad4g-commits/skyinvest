#!/usr/bin/env python
"""Проверка, что аккаунту разрешено создавать и править сущности Google Ads.

Каждая операция уходит с validate_only=True: сервер валидирует её полностью,
но ничего не создаёт и не меняет. Ни одна сущность в аккаунте не появится.
"""
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


SERVICES = {
    "MutateCampaignBudgetsRequest": ("CampaignBudgetService", "mutate_campaign_budgets"),
    "MutateCampaignsRequest": ("CampaignService", "mutate_campaigns"),
    "MutateAdGroupsRequest": ("AdGroupService", "mutate_ad_groups"),
    "MutateAdGroupAdsRequest": ("AdGroupAdService", "mutate_ad_group_ads"),
    "MutateAdGroupCriteriaRequest": ("AdGroupCriterionService", "mutate_ad_group_criteria"),
}


def probe(label, service_name, request_type, operation):
    request = client.get_type(request_type)
    request.customer_id = CID
    request.operations = [operation]
    request.validate_only = True
    service_name, method_name = SERVICES[request_type]
    method = getattr(client.get_service(service_name), method_name)
    try:
        method(request=request)
        print(f"  РАЗРЕШЕНО  {label}")
    except GoogleAdsException as err:
        messages = "; ".join(e.message for e in err.failure.errors)
        print(f"  ОТКЛОНЕНО  {label}: {messages[:220]}")
    except Exception as err:  # noqa: BLE001
        print(f"  ОШИБКА     {label}: {str(err)[:220]}")


# Опорные существующие сущности, чтобы ссылаться на них в проверках.
budget_rn = campaign_rn = adgroup_rn = None
for row in ga.search(customer_id=CID, query="""
    SELECT campaign.resource_name, campaign_budget.resource_name
    FROM campaign WHERE campaign.status = 'ENABLED' LIMIT 1
"""):
    campaign_rn = row.campaign.resource_name
    budget_rn = row.campaign_budget.resource_name
for row in ga.search(customer_id=CID, query="""
    SELECT ad_group.resource_name FROM ad_group
    WHERE campaign.status = 'ENABLED' AND ad_group.status = 'ENABLED' LIMIT 1
"""):
    adgroup_rn = row.ad_group.resource_name

print("=== Создание новых сущностей (validate_only) ===")

op = client.get_type("CampaignBudgetOperation")
b = op.create
b.name = "PROBE budget (не создаётся)"
b.amount_micros = 50_000_000
b.delivery_method = enums.BudgetDeliveryMethodEnum.STANDARD
b.explicitly_shared = False
probe("новый бюджет", "CampaignBudgetService", "MutateCampaignBudgetsRequest", op)

op = client.get_type("CampaignOperation")
c = op.create
c.name = "PROBE campaign (не создаётся)"
c.advertising_channel_type = enums.AdvertisingChannelTypeEnum.SEARCH
c.status = enums.CampaignStatusEnum.PAUSED
c.campaign_budget = budget_rn
c.manual_cpc.enhanced_cpc_enabled = False
c.network_settings.target_google_search = True
c.network_settings.target_search_network = False
c.network_settings.target_content_network = False
c.start_date = "2026-09-01"
c.end_date = "2037-12-30"
probe("новая поисковая кампания", "CampaignService", "MutateCampaignsRequest", op)

op = client.get_type("AdGroupOperation")
g = op.create
g.name = "PROBE ad group (не создаётся)"
g.campaign = campaign_rn
g.status = enums.AdGroupStatusEnum.PAUSED
g.type_ = enums.AdGroupTypeEnum.SEARCH_STANDARD
g.cpc_bid_micros = 2_000_000
probe("новая группа объявлений", "AdGroupService", "MutateAdGroupsRequest", op)

op = client.get_type("AdGroupAdOperation")
a = op.create
a.ad_group = adgroup_rn
a.status = enums.AdGroupAdStatusEnum.PAUSED
a.ad.final_urls.append("https://m.nezalezhnist.org.ua/proverka-zastrojshchika")
for text in ("Как проверить застройщика", "Бесплатный чек-лист", "Материал для покупателя"):
    asset = client.get_type("AdTextAsset")
    asset.text = text
    a.ad.responsive_search_ad.headlines.append(asset)
for text in ("Разбор документов и рисков перед покупкой недвижимости за рубежом.",
             "Чек-лист проверки застройщика: что запросить и где сверить."):
    asset = client.get_type("AdTextAsset")
    asset.text = text
    a.ad.responsive_search_ad.descriptions.append(asset)
probe("новое объявление RSA", "AdGroupAdService", "MutateAdGroupAdsRequest", op)

op = client.get_type("AdGroupCriterionOperation")
k = op.create
k.ad_group = adgroup_rn
k.status = enums.AdGroupCriterionStatusEnum.PAUSED
k.keyword.text = "как проверить застройщика за рубежом"
k.keyword.match_type = enums.KeywordMatchTypeEnum.PHRASE
probe("новое ключевое слово", "AdGroupCriterionService", "MutateAdGroupCriteriaRequest", op)

print("\n=== Изменение существующих (validate_only) ===")

op = client.get_type("CampaignOperation")
c = op.update
c.resource_name = campaign_rn
c.status = enums.CampaignStatusEnum.PAUSED
client.copy_from(op.update_mask, protobuf_helpers.field_mask(None, c._pb))
probe("поставить кампанию на паузу", "CampaignService", "MutateCampaignsRequest", op)

op = client.get_type("AdGroupOperation")
g = op.update
g.resource_name = adgroup_rn
g.cpc_bid_micros = 3_000_000
client.copy_from(op.update_mask, protobuf_helpers.field_mask(None, g._pb))
probe("изменить ставку группы", "AdGroupService", "MutateAdGroupsRequest", op)

op = client.get_type("CampaignBudgetOperation")
b = op.update
b.resource_name = budget_rn
b.amount_micros = 75_000_000
client.copy_from(op.update_mask, protobuf_helpers.field_mask(None, b._pb))
probe("изменить бюджет", "CampaignBudgetService", "MutateCampaignBudgetsRequest", op)
