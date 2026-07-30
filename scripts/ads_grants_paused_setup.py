#!/usr/bin/env python3
"""Build and reconcile paused, Grants-ready educational Search campaigns.

Nothing is enabled by this script.  It uses only phrase/exact multi-word
keywords, two tightly themed ad groups, two RSA per group and two sitelinks
per campaign.  Use --apply only after checking the dry-run output.
"""
from __future__ import annotations

import argparse
import pathlib
import time

from google.ads.googleads.client import GoogleAdsClient

from ads_create_education_campaigns import CAMPAIGNS as EXISTING_CAMPAIGNS
from ads_create_education_campaigns import NEGATIVES


ROOT = pathlib.Path(__file__).resolve().parent.parent
CONFIG = ROOT / ".secrets" / "google-ads.yaml"
BASE_URL = "https://m.nezalezhnist.org.ua"

# Every row is an informational query, a matching article and a form offering
# the article's practical checklist.  They are deliberately not commercial
# property-search campaigns.
NEW_CAMPAIGNS = [
    ("Турция | Документы", "turciya-proverka-dokumentov", "Проверить документы Турции", [
        ["документы на недвижимость в турции", "проверка документов недвижимости турция", "как проверить объект в турции"],
        ["риски сделки с недвижимостью турция", "документы перед сделкой в турции", "как проверить продавца в турции"],
    ], ["turciya-tapu-iskan", "turciya-rashody-na-soderzhanie"]),
    ("Турция | Tapu и Iskan", "turciya-tapu-iskan", "Разобраться в Tapu и Iskan", [
        ["что проверить в tapu турция", "iskan что это в турции", "tapu документы недвижимости"],
        ["как проверить tapu в турции", "документы tapu iskan", "реестр недвижимости турция"],
    ], ["turciya-proverka-dokumentov", "turciya-upravlyayushchaya-kompaniya"]),
    ("Турция | Расходы объекта", "turciya-rashody-na-soderzhanie", "Понять расходы на объект", [
        ["расходы на содержание недвижимости турция", "айдат в турции что это", "коммунальные расходы турция квартира"],
        ["налоги на недвижимость турция", "управляющая компания турция расходы", "проверить расходы перед сделкой турция"],
    ], ["turciya-upravlyayushchaya-kompaniya", "turciya-proverka-dokumentov"]),
    ("Турция | Управление объектом", "turciya-upravlyayushchaya-kompaniya", "Проверить договор управления", [
        ["управляющая компания в турции", "договор с управляющей компанией турция", "управление квартирой в турции"],
        ["как выбрать управляющую компанию турция", "обязанности управляющей компании турция", "проверить договор управления турция"],
    ], ["turciya-rashody-na-soderzhanie", "turciya-tapu-iskan"]),
    ("Грузия | Реестр", "gruziya-proverka-reestra", "Проверить запись в реестре", [
        ["проверить недвижимость в грузии реестр", "реестр недвижимости грузия проверка", "документы на квартиру в грузии"],
        ["как проверить объект в грузии", "публичный реестр грузия недвижимость", "проверка сделки грузия"],
    ], ["gruziya-ru", "sravnenie-stran-dlya-zhizni"]),
    ("Испания | Nota Simple", "ispania-nota-simple", "Разобраться в Nota Simple", [
        ["nota simple что это", "проверка недвижимости испания nota simple", "документы на недвижимость испания"],
        ["как проверить объект в испании", "реестр недвижимости испания", "выписка из реестра испания"],
    ], ["sravnenie-stran-dlya-zhizni", "dokumenty-i-riski"]),
    ("Бали | Права на землю", "bali-prava-na-zemlyu", "Проверить права на землю", [
        ["права на землю бали", "как проверить землю на бали", "документы на недвижимость бали"],
        ["риски недвижимости на бали", "проверка объекта бали", "виды прав на землю индонезия"],
    ], ["proverka-zastrojshchika", "dokumenty-i-riski"]),
    ("ОАЭ | Проверка объекта", "oae-proverka-obekta", "Проверить объект в ОАЭ", [
        ["проверка недвижимости оаэ", "как проверить объект дубай", "документы на недвижимость оаэ"],
        ["реестр недвижимости дубай", "проверка застройщика оаэ", "проверка сделки оаэ"],
    ], ["proverka-zastrojshchika", "dokumenty-i-riski"]),
    ("Камбоджа | Документы", "kambodzha-proverka-dokumentov", "Проверить документы Камбоджи", [
        ["документы на недвижимость камбоджа", "проверка недвижимости камбоджа", "как проверить объект камбоджа"],
        ["риски сделки камбоджа", "проверка застройщика камбоджа", "документы перед сделкой камбоджа"],
    ], ["kambodzha-ru", "dokumenty-i-riski"]),
    ("Сравнение стран", "sravnenie-stran-dlya-zhizni", "Сравнить страны по критериям", [
        ["сравнение стран для жизни", "как выбрать страну для переезда", "сравнить страны для переезда"],
        ["какую страну выбрать для жизни", "сравнение стран документы климат", "страны для переезда сравнение"],
    ], ["vybor-strany-dlya-pereezda", "vebinary-i-konsultacii"]),
]


def customer_id() -> str:
    for line in CONFIG.read_text(encoding="utf-8").splitlines():
        if line.startswith("# Рабочий аккаунт:"):
            return line.split(":", 1)[1].strip()
    raise RuntimeError("В конфигурации не указан рабочий рекламный аккаунт.")


def text_assets(client, collection, values):
    for value in values:
        if len(value) > 30:
            raise ValueError(f"Слишком длинный заголовок: {value}")
        asset = client.get_type("AdTextAsset")
        asset.text = value
        collection.append(asset)


def descriptions(client, collection, values):
    for value in values:
        if len(value) > 90:
            raise ValueError(f"Слишком длинное описание: {value}")
        asset = client.get_type("AdTextAsset")
        asset.text = value
        collection.append(asset)


def campaign_name(title: str) -> str:
    return f"[PAUSED] EDU | {title}"


def existing_campaigns(client, cid):
    rows = client.get_service("GoogleAdsService").search(customer_id=cid, query="""
        SELECT campaign.id, campaign.name, campaign.resource_name, campaign.status,
               campaign.bidding_strategy_type
        FROM campaign
        WHERE campaign.status != 'REMOVED'
    """)
    return {row.campaign.name: row.campaign for row in rows}


def set_maximize_conversions(client, cid, campaign):
    if campaign.bidding_strategy_type.name == "MAXIMIZE_CONVERSIONS":
        return False
    op = client.get_type("CampaignOperation")
    op.update.resource_name = campaign.resource_name
    # MaximizeConversions has subfields.  The Ads API requires the mutable
    # subfield in the mask even when we intentionally leave it unset (no tCPA).
    op.update_mask.paths.append("maximize_conversions.target_cpa_micros")
    client.get_service("CampaignService").mutate_campaigns(customer_id=cid, operations=[op])
    return True


def create_campaign(client, cid, title, slug, groups, sitelinks, daily_budget):
    budget_op = client.get_type("CampaignBudgetOperation")
    budget_op.create.name = f"{campaign_name(title)} | budget"
    budget_op.create.amount_micros = round(daily_budget * 1_000_000)
    budget_op.create.delivery_method = client.enums.BudgetDeliveryMethodEnum.STANDARD
    budget_op.create.explicitly_shared = False
    budget = client.get_service("CampaignBudgetService").mutate_campaign_budgets(
        customer_id=cid, operations=[budget_op]
    ).results[0].resource_name
    op = client.get_type("CampaignOperation")
    campaign = op.create
    campaign.name = campaign_name(title)
    campaign.status = client.enums.CampaignStatusEnum.PAUSED
    campaign.advertising_channel_type = client.enums.AdvertisingChannelTypeEnum.SEARCH
    campaign.contains_eu_political_advertising = client.enums.EuPoliticalAdvertisingStatusEnum.DOES_NOT_CONTAIN_EU_POLITICAL_ADVERTISING
    campaign.campaign_budget = budget
    campaign.network_settings.target_google_search = True
    campaign.network_settings.target_search_network = False
    campaign.network_settings.target_partner_search_network = False
    campaign.maximize_conversions._pb.CopyFrom(client.get_type("MaximizeConversions")._pb)
    return client.get_service("CampaignService").mutate_campaigns(customer_id=cid, operations=[op]).results[0].resource_name


def create_group(client, cid, campaign_resource, title, number, terms):
    op = client.get_type("AdGroupOperation")
    group = op.create
    group.name = f"{title} | запросы {number}"
    group.campaign = campaign_resource
    group.status = client.enums.AdGroupStatusEnum.PAUSED
    group.type_ = client.enums.AdGroupTypeEnum.SEARCH_STANDARD
    group.cpc_bid_micros = 2_000_000
    group_resource = client.get_service("AdGroupService").mutate_ad_groups(customer_id=cid, operations=[op]).results[0].resource_name
    terms_ops = []
    for term in terms:
        if len(term.split()) < 2:
            raise ValueError(f"Одиночный ключ запрещён: {term}")
        for match in ("PHRASE", "EXACT"):
            operation = client.get_type("AdGroupCriterionOperation")
            criterion = operation.create
            criterion.ad_group = group_resource
            criterion.status = client.enums.AdGroupCriterionStatusEnum.PAUSED
            criterion.keyword.text = term
            criterion.keyword.match_type = client.enums.KeywordMatchTypeEnum[match]
            terms_ops.append(operation)
    client.get_service("AdGroupCriterionService").mutate_ad_group_criteria(customer_id=cid, operations=terms_ops)
    return group_resource


def rsa_values(title, offer, variant):
    common = [title[:30], "Проверка без спешки", "Практический гид", "Вопросы до решения", "Файл в Telegram"]
    if variant == 1:
        return common + [offer[:30]], [
            "Разберите документы, реестры и вопросы к участникам сделки до следующего шага.",
            "Получите бесплатный материал в Telegram — без звонка и без каталога объектов.",
        ]
    return common + ["Открыть чек-лист"], [
        "Сохраните список проверок и сверяйте ответы с официальными источниками.",
        "Материал придёт в Telegram. Спокойно разберите свою ситуацию в удобное время.",
    ]


def add_rsa(client, cid, group_resource, slug, title, offer):
    operations = []
    for variant in (1, 2):
        headlines, desc = rsa_values(title, offer, variant)
        op = client.get_type("AdGroupAdOperation")
        ad = op.create
        ad.ad_group = group_resource
        ad.status = client.enums.AdGroupAdStatusEnum.PAUSED
        ad.ad.final_urls.append(f"{BASE_URL}/{slug}")
        text_assets(client, ad.ad.responsive_search_ad.headlines, headlines)
        descriptions(client, ad.ad.responsive_search_ad.descriptions, desc)
        operations.append(op)
    client.get_service("AdGroupAdService").mutate_ad_group_ads(customer_id=cid, operations=operations)


def add_negatives(client, cid, campaign_resource):
    operations = []
    for term in NEGATIVES:
        op = client.get_type("CampaignCriterionOperation")
        criterion = op.create
        criterion.campaign = campaign_resource
        criterion.negative = True
        criterion.keyword.text = term
        criterion.keyword.match_type = client.enums.KeywordMatchTypeEnum.PHRASE
        operations.append(op)
    client.get_service("CampaignCriterionService").mutate_campaign_criteria(customer_id=cid, operations=operations)


def add_sitelinks(client, cid, campaign_resource, slugs):
    asset_ops = []
    for index, slug in enumerate(slugs, start=1):
        op = client.get_type("AssetOperation")
        op.create.name = f"EDU information link {slug}"
        op.create.final_urls.append(f"{BASE_URL}/{slug}")
        op.create.sitelink_asset.link_text = ("Открыть материал" if index == 1 else "Ещё один полезный гид")
        op.create.sitelink_asset.description1 = "Проверка документов и рисков"
        op.create.sitelink_asset.description2 = "Практические вопросы до решения"
        asset_ops.append(op)
    assets = client.get_service("AssetService").mutate_assets(customer_id=cid, operations=asset_ops).results
    links = []
    for asset in assets:
        op = client.get_type("CampaignAssetOperation")
        op.create.campaign = campaign_resource
        op.create.asset = asset.resource_name
        op.create.field_type = client.enums.AssetFieldTypeEnum.SITELINK
        links.append(op)
    client.get_service("CampaignAssetService").mutate_campaign_assets(customer_id=cid, operations=links)


def group_count(client, cid, campaign_id):
    query = f"SELECT ad_group.resource_name FROM ad_group WHERE campaign.id = {campaign_id} AND ad_group.status != 'REMOVED'"
    return [row.ad_group.resource_name for row in client.get_service("GoogleAdsService").search(customer_id=cid, query=query)]


def rsa_count(client, cid, group_resource):
    query = f"""
        SELECT ad_group_ad.resource_name
        FROM ad_group_ad
        WHERE ad_group.resource_name = '{group_resource}'
          AND ad_group_ad.status != 'REMOVED'
    """
    return sum(1 for _ in client.get_service("GoogleAdsService").search(customer_id=cid, query=query))


def sitelink_count(client, cid, campaign_id):
    query = f"""
        SELECT campaign.id, campaign_asset.resource_name
        FROM campaign_asset
        WHERE campaign.id = {campaign_id}
          AND campaign_asset.field_type = 'SITELINK'
          AND campaign_asset.status != 'REMOVED'
    """
    return sum(1 for _ in client.get_service("GoogleAdsService").search(customer_id=cid, query=query))


def make_existing_specs():
    specs = []
    for title, slug, offer, terms in EXISTING_CAMPAIGNS:
        midpoint = max(2, len(terms) // 2)
        specs.append((title, slug, offer, [terms[:midpoint], terms[midpoint:]], ["dokumenty-i-riski", "vebinary-i-konsultacii"]))
    return specs


def validate_specs(specs):
    prohibited = "паспорт"
    for title, slug, offer, groups, links in specs:
        text = " ".join([title, slug, offer, *links, *(term for group in groups for term in group)]).lower()
        if prohibited in text:
            raise ValueError("Запрещённое слово обнаружено в настройке кампании.")
        if len(groups) != 2 or any(not group for group in groups):
            raise ValueError(f"У кампании {title} должны быть две непустые группы.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--daily-budget", type=float, default=50.0)
    args = parser.parse_args()
    if not CONFIG.exists():
        raise SystemExit("Нет конфигурации Google Ads.")
    specs = make_existing_specs() + NEW_CAMPAIGNS
    validate_specs(specs)
    client = GoogleAdsClient.load_from_storage(str(CONFIG))
    cid = customer_id()
    known = existing_campaigns(client, cid)
    for title, slug, offer, groups, links in specs:
        label = campaign_name(title)
        current = known.get(label)
        state = "проверить и дополнить" if current else "создать"
        print(f"{state}: {label} → /{slug}; 2 группы, 2 RSA/группу, 2 sitelink; PAUSED")
    if not args.apply:
        print("Dry-run: Google Ads не изменялся. Все будущие сущности имеют статус PAUSED.")
        return
    for title, slug, offer, groups, links in specs:
        label = campaign_name(title)
        current = known.get(label)
        if current:
            campaign_resource = current.resource_name
            changed = set_maximize_conversions(client, cid, current)
            group_resources = group_count(client, cid, current.id)
            # Existing campaigns already contain their first group. Add the missing one.
            while len(group_resources) < 2:
                group_resources.append(create_group(client, cid, campaign_resource, title, len(group_resources) + 1, groups[len(group_resources)]))
            if sitelink_count(client, cid, current.id) < 2:
                add_sitelinks(client, cid, campaign_resource, links)
            print(f"Дополнена: {label}; Smart Bidding {'включён' if changed else 'уже был'}")
        else:
            campaign_resource = create_campaign(client, cid, title, slug, groups, links, args.daily_budget)
            time.sleep(1)
            group_resources = [create_group(client, cid, campaign_resource, title, index, terms) for index, terms in enumerate(groups, start=1)]
            add_negatives(client, cid, campaign_resource)
            add_sitelinks(client, cid, campaign_resource, links)
            print(f"Создана: {label}")
        # Fresh RSAs are created alongside historic ads: RSA fields are immutable in
        # the API, so the former ad is never edited in place.
        for resource in group_resources:
            if rsa_count(client, cid, resource) < 2:
                add_rsa(client, cid, resource, slug, title, offer)
    print("Готово: ни одна кампания, группа, ключ или RSA не включались.")


if __name__ == "__main__":
    main()
