#!/usr/bin/env python3
"""Rebuild paused EDU Search campaigns without duplicate groups, keywords or RSA.

The script never enables a campaign, ad group, keyword or ad. It is a dry run
unless --apply is passed. On apply it removes the old paused ad groups inside
the named EDU campaigns and creates one clean paused group per campaign.
"""
from __future__ import annotations

import argparse
import pathlib
import time
from collections import OrderedDict

from google.ads.googleads.client import GoogleAdsClient


ROOT = pathlib.Path(__file__).resolve().parent.parent
CONFIG = ROOT / ".secrets" / "google-ads.yaml"
CLEAN_PREFIX = "[CLEAN] EDU | "


def customer_id() -> str:
    for line in CONFIG.read_text(encoding="utf-8").splitlines():
        if line.startswith("# Рабочий аккаунт:"):
            return line.split(":", 1)[1].strip()
    raise RuntimeError("В google-ads.yaml нет комментария '# Рабочий аккаунт: <ID>'.")


def fit(text: str, limit: int) -> str:
    text = " ".join(text.split())
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def material_copy(campaign_name: str) -> tuple[str, str]:
    name = campaign_name.removeprefix("[PAUSED] EDU | ")
    variants = {
        "Бали | Права на землю": ("Права на землю на Бали", "Разберите виды прав, реестры и документы по сделке на Бали."),
        "Вебинары": ("Вебинар о проверке сделки", "Получите программу вебинара и вопросы для безопасной проверки сделки."),
        "Выбор страны": ("Как выбрать страну", "Сравните страны по понятным критериям до принятия решения."),
        "Гражданство | Антигуа": ("Гражданство Антигуа", "Разберите официальные документы и вопросы по программе Антигуа."),
        "Гражданство | Гренада": ("Гражданство Гренады", "Разберите официальные документы и вопросы по программе Гренады."),
        "Гражданство | Доминика": ("Гражданство Доминики", "Разберите официальные документы и вопросы по программе Доминики."),
        "Гражданство | Сент-Китс": ("Гражданство Сент-Китс", "Разберите официальные документы и вопросы по программе Сент-Китс."),
        "Грузия | Реестр": ("Проверка реестра Грузии", "Поймите, какие сведения запросить в реестре и как их сверить."),
        "Документы и риски": ("Документы и риски сделки", "Соберите вопросы к документам и участникам сделки до следующего шага."),
        "Испания | Nota Simple": ("Nota Simple: что проверить", "Разберите выписку Nota Simple и вопросы, которые стоит задать до сделки."),
        "Камбоджа | Документы": ("Документы в Камбодже", "Соберите список документов и вопросов для проверки сделки в Камбодже."),
        "ОАЭ | Проверка объекта": ("Проверка объекта в ОАЭ", "Разберите документы объекта и вопросы для проверки до решения."),
        "Ошибки инвестора": ("7 ошибок инвестора", "Проверьте типичные ошибки до того, как они станут дорогими."),
        "Проверка застройщика": ("Проверка застройщика", "Соберите вопросы к девелоперу, документам и срокам проекта."),
        "Сравнение стран": ("Сравнить страны для жизни", "Сопоставьте страны по критериям, важным именно для вашего сценария."),
        "Страна | Грузия": ("Гид по недвижимости Грузии", "Разберите документы, формат владения и вопросы до принятия решения."),
        "Страна | Камбоджа": ("Гид по недвижимости Камбоджи", "Разберите документы, формат владения и вопросы до принятия решения."),
        "Страна | Мальдивы": ("Гид по недвижимости Мальдив", "Разберите документы, формат владения и вопросы до принятия решения."),
        "Турция | Tapu и Iskan": ("Tapu и Iskan в Турции", "Разберите документы Tapu и Iskan и порядок их проверки."),
        "Турция | Документы": ("Документы в Турции", "Соберите список документов и вопросов для проверки сделки в Турции."),
        "Турция | Расходы объекта": ("Расходы на объект в Турции", "Разберите айдат, налоги и регулярные расходы до выбора объекта."),
        "Турция | Управление объектом": ("Управление объектом в Турции", "Соберите вопросы к управляющей компании и договору управления."),
        "Управление объектом": ("Управление объектом", "Разберите договор управления, обязанности сторон и регулярные расходы."),
        "Финансовая модель": ("Финансовая модель аренды", "Поймите, какие расходы и допущения заложить в расчёт доходности."),
    }
    return variants.get(name, (fit(name, 30), "Получите практический материал и список вопросов для самостоятельной проверки."))


def add_text_assets(client, collection, values: list[str]) -> None:
    for value in values:
        asset = client.get_type("AdTextAsset")
        asset.text = value
        collection.append(asset)


def query_campaigns(service, cid: str):
    rows = service.search(customer_id=cid, query="""
        SELECT campaign.id, campaign.name, campaign.resource_name, campaign.status
        FROM campaign
        WHERE campaign.name LIKE '%EDU%' AND campaign.status != 'REMOVED'
        ORDER BY campaign.name
    """)
    return [row.campaign for row in rows if row.campaign.name.startswith("[PAUSED] EDU | ")]


def keywords_and_url(service, cid: str, campaign_id: int) -> tuple[list[str], str]:
    terms: OrderedDict[str, None] = OrderedDict()
    keyword_rows = service.search(customer_id=cid, query=f"""
        SELECT ad_group_criterion.keyword.text
        FROM keyword_view
        WHERE campaign.id = {campaign_id}
        ORDER BY ad_group_criterion.keyword.text
    """)
    for row in keyword_rows:
        term = row.ad_group_criterion.keyword.text.strip()
        if term:
            terms.setdefault(term.lower(), term)

    url_rows = service.search(customer_id=cid, query=f"""
        SELECT ad_group_ad.ad.final_urls
        FROM ad_group_ad
        WHERE campaign.id = {campaign_id}
          AND ad_group_ad.ad.type = 'RESPONSIVE_SEARCH_AD'
        LIMIT 1
    """)
    url = next((row.ad_group_ad.ad.final_urls[0] for row in url_rows if row.ad_group_ad.ad.final_urls), "")
    return list(terms.values())[:6], url


def group_state(service, cid: str, campaign_id: int) -> tuple[bool, int]:
    rows = service.search(customer_id=cid, query=f"""
        SELECT ad_group.name
        FROM ad_group
        WHERE campaign.id = {campaign_id} AND ad_group.status != 'REMOVED'
    """)
    groups = list(rows)
    return (
        any(row.ad_group.name.startswith(CLEAN_PREFIX) for row in groups),
        sum(not row.ad_group.name.startswith(CLEAN_PREFIX) for row in groups),
    )


def remove_old_groups(client, service, cid: str, campaign_id: int) -> int:
    rows = service.search(customer_id=cid, query=f"""
        SELECT ad_group.resource_name, ad_group.name
        FROM ad_group
        WHERE campaign.id = {campaign_id} AND ad_group.status != 'REMOVED'
    """)
    operations = []
    for row in rows:
        if row.ad_group.name.startswith(CLEAN_PREFIX):
            continue
        operation = client.get_type("AdGroupOperation")
        operation.remove = row.ad_group.resource_name
        operations.append(operation)
    if operations:
        client.get_service("AdGroupService").mutate_ad_groups(customer_id=cid, operations=operations)
    return len(operations)


def add_passport_negative(client, service, cid: str, campaign) -> None:
    rows = service.search(customer_id=cid, query=f"""
        SELECT campaign_criterion.keyword.text
        FROM campaign_criterion
        WHERE campaign.id = {campaign.id}
          AND campaign_criterion.negative = TRUE
          AND campaign_criterion.type = 'KEYWORD'
    """)
    existing = {row.campaign_criterion.keyword.text.lower() for row in rows}
    if "паспорт" in existing:
        return
    operation = client.get_type("CampaignCriterionOperation")
    criterion = operation.create
    criterion.campaign = campaign.resource_name
    criterion.negative = True
    criterion.keyword.text = "паспорт"
    criterion.keyword.match_type = client.enums.KeywordMatchTypeEnum.PHRASE
    client.get_service("CampaignCriterionService").mutate_campaign_criteria(customer_id=cid, operations=[operation])


def create_clean_group(client, cid: str, campaign, terms: list[str], url: str) -> None:
    if not terms or not url:
        raise RuntimeError(f"{campaign.name}: нет ключей или final URL для пересборки")
    topic, detail = material_copy(campaign.name)
    group_operation = client.get_type("AdGroupOperation")
    group = group_operation.create
    group.name = f"{CLEAN_PREFIX}{topic}"
    group.campaign = campaign.resource_name
    group.status = client.enums.AdGroupStatusEnum.PAUSED
    group.type_ = client.enums.AdGroupTypeEnum.SEARCH_STANDARD
    group.cpc_bid_micros = 2_000_000
    group_name = client.get_service("AdGroupService").mutate_ad_groups(
        customer_id=cid, operations=[group_operation]
    ).results[0].resource_name

    keyword_operations = []
    for term in terms:
        for match_type in ("PHRASE", "EXACT"):
            operation = client.get_type("AdGroupCriterionOperation")
            criterion = operation.create
            criterion.ad_group = group_name
            criterion.status = client.enums.AdGroupCriterionStatusEnum.PAUSED
            criterion.keyword.text = term
            criterion.keyword.match_type = client.enums.KeywordMatchTypeEnum[match_type]
            keyword_operations.append(operation)
    client.get_service("AdGroupCriterionService").mutate_ad_group_criteria(
        customer_id=cid, operations=keyword_operations
    )

    ad_operation = client.get_type("AdGroupAdOperation")
    ad = ad_operation.create
    ad.ad_group = group_name
    ad.status = client.enums.AdGroupAdStatusEnum.PAUSED
    ad.ad.final_urls.append(url)
    add_text_assets(client, ad.ad.responsive_search_ad.headlines, [
        fit(topic, 30),
        "Бесплатный материал",
        "Что проверить заранее",
        "Практический чек-лист",
        "Вопросы до решения",
        "Материал в Telegram",
        "Официальные источники",
        "Проверка без спешки",
    ])
    add_text_assets(client, ad.ad.responsive_search_ad.descriptions, [
        fit(f"{detail} Получите практический материал в Telegram.", 90),
        "Список вопросов и документов, которые стоит проверить до решения.",
        "Без цен, витрины объектов и навязчивых звонков.",
    ])
    client.get_service("AdGroupAdService").mutate_ad_group_ads(
        customer_id=cid, operations=[ad_operation]
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="внести изменения в Ads")
    parser.add_argument("--start", type=int, default=0, help="начать с кампании N (нумерация с нуля)")
    parser.add_argument("--limit", type=int, default=24, help="сколько кампаний обработать за один запуск")
    args = parser.parse_args()
    if not CONFIG.exists():
        raise SystemExit(f"Нет конфигурации {CONFIG}")

    client = GoogleAdsClient.load_from_storage(str(CONFIG))
    cid = customer_id()
    service = client.get_service("GoogleAdsService")
    campaigns = query_campaigns(service, cid)[args.start:args.start + args.limit]
    for campaign in campaigns:
        terms, url = keywords_and_url(service, cid, int(campaign.id))
        clean_exists, old_group_count = group_state(service, cid, int(campaign.id))
        marker = "ГОТОВО" if clean_exists and old_group_count == 0 else "ПЕРЕСОБРАТЬ"
        print(f"{marker} | {campaign.name} | {url} | {len(terms)} уникальных ключей")
        if not args.apply or marker == "ГОТОВО":
            continue
        removed = remove_old_groups(client, service, cid, int(campaign.id))
        if not clean_exists:
            # Let the removal propagate before creating the replacement group.
            time.sleep(0.5)
            create_clean_group(client, cid, campaign, terms, url)
        add_passport_negative(client, service, cid, campaign)
        print(f"  удалено legacy-групп: {removed}; clean-группа сохранена/создана и остаётся PAUSED")


if __name__ == "__main__":
    main()
