#!/usr/bin/env python3
"""Create paused educational Search campaigns for guides, countries, and citizenship.

No campaign is enabled by this script. Review the output first; Google Ads is
mutated only with --apply. Final URLs deliberately point to the m. domain.
"""
import argparse
import pathlib
import time

from google.ads.googleads.client import GoogleAdsClient


ROOT = pathlib.Path(__file__).resolve().parent.parent
CONFIG = ROOT / ".secrets" / "google-ads.yaml"
BASE_URL = "https://m.nezalezhnist.org.ua"
NEGATIVES = [
    "купить", "продажа", "цена", "стоимость", "прайс", "каталог",
    "объекты", "риелтор", "агентство недвижимости", "рассрочка",
    "работа", "вакансии", "зарплата", "резюме", "стажировка",
    "отель", "туры", "погода", "карта", "скачать фильм",
]
CAMPAIGNS = [
    ("Проверка застройщика", "proverka-zastrojshchika", "Получить чек-лист проверки", ["как проверить застройщика за рубежом", "проверка девелопера бали", "документы застройщика за границей"]),
    ("Документы и риски", "dokumenty-i-riski", "Получить карту документов", ["документы для сделки за рубежом", "риски недвижимости за границей", "как проверить документы на недвижимость"]),
    ("Финансовая модель", "kalkulator-dohodnosti-arendy", "Получить финансовую модель", ["как считать доходность аренды", "финансовая модель аренды", "чистая доходность недвижимости"]),
    ("Ошибки инвестора", "7-oshibok-investora", "Получить гид «7 ошибок»", ["ошибки инвестора в недвижимости", "как не потерять деньги за рубежом", "риски инвестиций в недвижимость"]),
    ("Управление объектом", "upravlenie-nedvizhimostyu", "Получить чек-лист управления", ["как работает управляющая компания", "расходы на содержание недвижимости", "договор с управляющей компанией"]),
    ("Выбор страны", "vybor-strany-dlya-pereezda", "Получить сравнительный гид", ["сравнение стран для переезда", "как выбрать страну для жизни", "сравнить страны для переезда"]),
    ("Вебинары", "vebinary-i-konsultacii", "Получить приглашение на вебинар", ["вебинар о проверке недвижимости", "бесплатная консультация по рискам сделки", "вебинар о недвижимости за рубежом"]),
    ("Гражданство | Гренада", "grazhdanstvo-grenady", "Получить карту проверки программы", ["как проверить гражданство гренады", "документы для гражданства гренады", "официальная программа гражданства гренады"]),
    ("Гражданство | Антигуа", "grazhdanstvo-antigua-i-barbudy", "Получить карту проверки программы", ["как проверить гражданство антигуа и барбуды", "документы для гражданства антигуа и барбуды", "официальная программа гражданства антигуа"]),
    ("Гражданство | Доминика", "grazhdanstvo-dominiki", "Получить карту проверки программы", ["как проверить гражданство доминики", "документы для гражданства доминики", "официальная программа гражданства доминики"]),
    ("Гражданство | Сент-Китс", "grazhdanstvo-sent-kits-i-nevis", "Получить карту проверки программы", ["как проверить гражданство сент китс и невис", "документы для гражданства сент китс и невис", "официальная программа гражданства сент китс"]),
    ("Страна | Грузия", "gruziya-ru", "Получить гид по выбору страны", ["как выбрать недвижимость в грузии", "проверка недвижимости в грузии", "документы на недвижимость в грузии"]),
    ("Страна | Камбоджа", "kambodzha-ru", "Получить гид по выбору страны", ["как выбрать недвижимость в камбодже", "проверка недвижимости в камбодже", "документы на недвижимость в камбодже"]),
    ("Страна | Мальдивы", "maldivy-ru", "Получить гид по выбору страны", ["как выбрать недвижимость на мальдивах", "проверка недвижимости на мальдивах", "документы на недвижимость на мальдивах"]),
]


def customer_id():
    for line in CONFIG.read_text(encoding="utf-8").splitlines():
        if line.startswith("# Рабочий аккаунт:"):
            return line.split(":", 1)[1].strip()
    raise RuntimeError("В google-ads.yaml нет комментария '# Рабочий аккаунт: <ID>'.")


def add_text_assets(client, collection, values):
    for value in values:
        asset = client.get_type("AdTextAsset")
        asset.text = value
        collection.append(asset)


def create_campaign(client, cid, title, slug, offer, keywords, daily_budget):
    budget_operation = client.get_type("CampaignBudgetOperation")
    budget = budget_operation.create
    budget.name = f"[PAUSED] EDU | {title} | budget"
    budget.amount_micros = round(daily_budget * 1_000_000)
    budget.delivery_method = client.enums.BudgetDeliveryMethodEnum.STANDARD
    budget.explicitly_shared = False
    budget_name = client.get_service("CampaignBudgetService").mutate_campaign_budgets(
        customer_id=cid, operations=[budget_operation]
    ).results[0].resource_name

    campaign_operation = client.get_type("CampaignOperation")
    campaign = campaign_operation.create
    campaign.name = f"[PAUSED] EDU | {title}"
    campaign.status = client.enums.CampaignStatusEnum.PAUSED
    campaign.advertising_channel_type = client.enums.AdvertisingChannelTypeEnum.SEARCH
    campaign.contains_eu_political_advertising = (
        client.enums.EuPoliticalAdvertisingStatusEnum.DOES_NOT_CONTAIN_EU_POLITICAL_ADVERTISING
    )
    campaign.campaign_budget = budget_name
    campaign.network_settings.target_google_search = True
    campaign.network_settings.target_search_network = False
    campaign.network_settings.target_partner_search_network = False
    campaign.manual_cpc.enhanced_cpc_enabled = False
    campaign_name = client.get_service("CampaignService").mutate_campaigns(
        customer_id=cid, operations=[campaign_operation]
    ).results[0].resource_name
    time.sleep(2)

    group_operation = client.get_type("AdGroupOperation")
    group = group_operation.create
    group.name = f"{title} | информационный запрос"
    group.campaign = campaign_name
    group.status = client.enums.AdGroupStatusEnum.PAUSED
    group.type_ = client.enums.AdGroupTypeEnum.SEARCH_STANDARD
    group.cpc_bid_micros = 2_000_000
    group_name = client.get_service("AdGroupService").mutate_ad_groups(
        customer_id=cid, operations=[group_operation]
    ).results[0].resource_name
    time.sleep(2)

    criterion_operations = []
    for term in keywords:
        for match_type in ("PHRASE", "EXACT"):
            operation = client.get_type("AdGroupCriterionOperation")
            criterion = operation.create
            criterion.ad_group = group_name
            criterion.status = client.enums.AdGroupCriterionStatusEnum.PAUSED
            criterion.keyword.text = term
            criterion.keyword.match_type = client.enums.KeywordMatchTypeEnum[match_type]
            criterion_operations.append(operation)
    negative_operations = []
    for term in NEGATIVES:
        operation = client.get_type("CampaignCriterionOperation")
        criterion = operation.create
        criterion.campaign = campaign_name
        criterion.negative = True
        criterion.keyword.text = term
        criterion.keyword.match_type = client.enums.KeywordMatchTypeEnum.PHRASE
        negative_operations.append(operation)
    client.get_service("CampaignCriterionService").mutate_campaign_criteria(
        customer_id=cid, operations=negative_operations
    )
    client.get_service("AdGroupCriterionService").mutate_ad_group_criteria(
        customer_id=cid, operations=criterion_operations
    )

    ad_operation = client.get_type("AdGroupAdOperation")
    ad = ad_operation.create
    ad.ad_group = group_name
    ad.status = client.enums.AdGroupAdStatusEnum.PAUSED
    ad.ad.final_urls.append(f"{BASE_URL}/{slug}")
    add_text_assets(client, ad.ad.responsive_search_ad.headlines, [
        title, "Бесплатный материал", "Проверка без рекламы", "Получить карту проверки",
        "Вопросы до решения", "Материал в мессенджер",
    ])
    add_text_assets(client, ad.ad.responsive_search_ad.descriptions, [
        "Понятный материал с вопросами для самостоятельной проверки. Без прайса на странице.",
        "Получите материал в выбранный мессенджер и разберите вопрос до следующего шага.",
    ])
    client.get_service("AdGroupAdService").mutate_ad_group_ads(
        customer_id=cid, operations=[ad_operation]
    )
    return campaign_name


def campaign_exists(client, cid, title):
    name = f"[PAUSED] EDU | {title}".replace("'", "\\'")
    query = f"SELECT campaign.id FROM campaign WHERE campaign.name = '{name}' AND campaign.status != 'REMOVED'"
    return any(client.get_service("GoogleAdsService").search(customer_id=cid, query=query))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--daily-budget", type=float, default=50.0)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if args.daily_budget <= 0:
        raise SystemExit("Дневной бюджет должен быть больше нуля.")
    if not CONFIG.exists():
        raise SystemExit(f"Нет конфигурации {CONFIG}")
    if not args.apply:
        for title, slug, _, keywords in CAMPAIGNS:
            print(f"[PAUSED] EDU | {title} | {BASE_URL}/{slug} | {len(keywords) * 2} ключей")
        print("Dry-run: ничего не создано. Для записи добавьте --apply.")
        return
    client = GoogleAdsClient.load_from_storage(str(CONFIG))
    cid = customer_id()
    for item in CAMPAIGNS:
        if campaign_exists(client, cid, item[0]):
            print(f"Уже существует, пропущена: [PAUSED] EDU | {item[0]}")
            continue
        resource = create_campaign(client, cid, *item, args.daily_budget)
        print(f"Создана и оставлена на паузе: {resource}")


if __name__ == "__main__":
    main()
