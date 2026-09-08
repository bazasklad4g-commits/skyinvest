#!/usr/bin/env python
"""Создание двух образовательных кампаний Google Ads.

Без --apply скрипт только валидирует операции на сервере (validate_only)
и ничего не создаёт. Кампании создаются ОСТАНОВЛЕННЫМИ: включать вручную
после проверки соответствия правилам Ad Grants.

  .venv/Scripts/python.exe scripts/ads_create_edu_campaigns.py
  .venv/Scripts/python.exe scripts/ads_create_edu_campaigns.py --only mission --apply
"""
import argparse
import os

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from google.oauth2 import service_account

CID = "3432200766"
DEVELOPER_TOKEN = "t8wOf5cvS7HV5V7gjHnH2w"
LOGIN_CID = "8522851042"

# Стандартный минус-набор аккаунта: отсекает коммерческий и нерелевантный спрос.
COMMERCIAL_NEGATIVES = [
    "туры", "отель", "работа", "купить", "агентство недвижимости", "цена", "продажа",
    "каталог", "погода", "вакансии", "прайс", "стоимость", "карта", "зарплата",
    "резюме", "паспорт", "стажировка", "риелтор", "рассрочка", "объекты", "скачать фильм",
]

# Для страницы об обучении «работа» и «вакансии» — чужой интент, но не коммерческий.
EDUCATION_NEGATIVES = [
    "вакансії", "вакансии", "зарплата", "зарплатня", "робота", "работа", "резюме",
    "скачати", "скачать", "торрент", "реферат", "диплом", "погода", "купить", "цена",
]

CAMPAIGNS = {
    "realestate": {
        "name": "EDU | Основы покупки за рубежом",
        "final_url": "https://m.nezalezhnist.org.ua/real-estate",
        "budget": 50,
        "negatives": COMMERCIAL_NEGATIVES,
        "groups": [
            {
                "name": "Выбор страны",
                "keywords": [
                    "как выбрать страну для покупки недвижимости",
                    "как сравнить страны для покупки недвижимости",
                    "чем отличается покупка недвижимости в разных странах",
                    "как выбрать страну под аренду недвижимости",
                    "с чего начать покупку недвижимости за рубежом",
                ],
                "ads": [
                    {
                        "headlines": ["Как выбрать страну", "Сравнение направлений",
                                      "Разбор без продаж", "Что учесть до покупки",
                                      "Жизнь, отдых или аренда"],
                        "descriptions": [
                            "Сравниваем страны по цели покупки: для жизни, отдыха или аренды.",
                            "Разбор направлений: Испания, Турция, Дубай, Бали, Грузия, Кипр.",
                            "Бесплатный материал о том, с чего начать выбор страны.",
                        ],
                    },
                    {
                        "headlines": ["Сначала цель, потом страна", "Материал для покупателя",
                                      "Разбор направлений", "Без рекламы объектов",
                                      "Что важно решить"],
                        "descriptions": [
                            "Материал о том, как цель покупки сужает круг подходящих стран.",
                            "Сравнение стран по климату, правилам владения и порядку сделки.",
                            "Никаких предложений о покупке: только разбор и критерии.",
                        ],
                    },
                ],
            },
            {
                "name": "Документы и проверка",
                "keywords": [
                    "какие документы нужны для покупки недвижимости за рубежом",
                    "как проверить недвижимость за рубежом перед покупкой",
                    "что нужно знать перед покупкой недвижимости за рубежом",
                ],
                "ads": [
                    {
                        "headlines": ["Документы для покупки", "Что проверить заранее",
                                      "Проверка объекта", "Разбор документов",
                                      "Список для проверки"],
                        "descriptions": [
                            "Какие документы запросить и где их сверить перед покупкой.",
                            "Чек-лист проверки: реестры, право собственности, обременения.",
                            "Материал о типичных ошибках и способах их избежать.",
                        ],
                    },
                    {
                        "headlines": ["Проверка до сделки", "Разбор рисков",
                                      "Какие бумаги нужны", "Где сверить данные",
                                      "Материал о проверке"],
                        "descriptions": [
                            "Разбираем, какие документы подтверждают право собственности.",
                            "Где находятся публичные реестры и как ими пользоваться.",
                            "Бесплатный материал без предложений о покупке.",
                        ],
                    },
                ],
            },
            {
                "name": "Расходы и налоги",
                "keywords": [
                    "налоги на недвижимость за рубежом для нерезидентов",
                    "расходы на содержание недвижимости за рубежом",
                ],
                "ads": [
                    {
                        "headlines": ["Налоги для нерезидентов", "Расходы на содержание",
                                      "Что платить каждый год", "Разбор расходов",
                                      "Считаем заранее"],
                        "descriptions": [
                            "Какие налоги и сборы платит нерезидент, владея жильём за рубежом.",
                            "Ежегодные расходы: коммунальные платежи, налоги, управление.",
                            "Разбор без рекламы объектов и без предложений о покупке.",
                        ],
                    },
                    {
                        "headlines": ["Сколько стоит владеть", "Ежегодные платежи",
                                      "Налоги за рубежом", "Материал о расходах",
                                      "Разбор для покупателя"],
                        "descriptions": [
                            "Что входит в содержание жилья за рубежом кроме самой покупки.",
                            "Как различаются налоговые правила для нерезидентов по странам.",
                            "Бесплатный материал о расходах после сделки.",
                        ],
                    },
                ],
            },
            {
                "name": "Українською",
                "keywords": [
                    "як обрати країну для купівлі нерухомості",
                    "що потрібно знати перед купівлею нерухомості за кордоном",
                    "документи для купівлі нерухомості за кордоном",
                    "податки на нерухомість за кордоном для нерезидентів",
                ],
                "ads": [
                    {
                        "headlines": ["Як обрати країну", "Що варто знати",
                                      "Документи для купівлі", "Розбір без продажу",
                                      "Матеріал для покупця"],
                        "descriptions": [
                            "Порівнюємо країни за метою купівлі: життя, відпочинок, оренда.",
                            "Які документи потрібні та де їх перевірити перед купівлею.",
                            "Безкоштовний матеріал про те, з чого почати вибір країни.",
                        ],
                    },
                    {
                        "headlines": ["Спершу мета, потім країна", "Податки за кордоном",
                                      "Перевірка до угоди", "Розбір напрямків",
                                      "Без реклами обʼєктів"],
                        "descriptions": [
                            "Розбір правил володіння та порядку угоди в різних країнах.",
                            "Які податки сплачує нерезидент, володіючи житлом за кордоном.",
                            "Тільки розбір і критерії, без пропозицій про купівлю.",
                        ],
                    },
                ],
            },
        ],
    },
    "mission": {
        "name": "EDU | Безкоштовне навчання професій",
        "final_url": "https://www.nezalezhnist.org.ua/",
        "budget": 50,
        "negatives": EDUCATION_NEGATIVES,
        "groups": [
            {
                "name": "Нерухомість | Навчання",
                "keywords": [
                    "безкоштовні курси менеджера закордонної нерухомості",
                    "як стати менеджером з продажу закордонної нерухомості",
                    "навчання міжнародної нерухомості",
                ],
                "ads": [
                    {
                        "headlines": ["Безкоштовне навчання", "Курс із нерухомості",
                                      "Тиждень теорії", "44 дні практики", "Старт карʼєри"],
                        "descriptions": [
                            "Безкоштовний курс менеджера з продажу закордонної нерухомості.",
                            "Тиждень теорії та 44 дні практики з підтримкою наставників.",
                            "Громадська організація «Незалежність»: освіта та підтримка.",
                        ],
                    },
                    {
                        "headlines": ["Освіта без оплати", "Професія з нуля",
                                      "Теорія і практика", "Навчання онлайн",
                                      "Заповніть анкету"],
                        "descriptions": [
                            "Отримайте професію менеджера міжнародної нерухомості безкоштовно.",
                            "Практичні навички, а не лише теорія: база для відпрацювання.",
                            "Проєкт неприбуткової організації для тих, хто починає карʼєру.",
                        ],
                    },
                ],
            },
            {
                "name": "Рекрутинг | Навчання",
                "keywords": [
                    "як стати рекрутером з нуля",
                    "безкоштовні курси рекрутера онлайн",
                ],
                "ads": [
                    {
                        "headlines": ["Курс рекрутера", "Навчання безкоштовне",
                                      "Три блоки навчання", "Професія рекрутер",
                                      "Почніть з нуля"],
                        "descriptions": [
                            "Безкоштовний курс рекрутера: три блоки теорії та практики.",
                            "Навчимо шукати й оцінювати кандидатів на реальних задачах.",
                            "Освітній проєкт громадської організації «Незалежність».",
                        ],
                    },
                    {
                        "headlines": ["Стати рекрутером", "Навчання рекрутингу",
                                      "Без досвіду", "Практика на задачах",
                                      "Записатися на курс"],
                        "descriptions": [
                            "Три блоки навчання: теорія, інструменти та практичні завдання.",
                            "Для тих, хто змінює професію та починає карʼєру в рекрутингу.",
                            "Навчання безкоштовне, організоване неприбутковою організацією.",
                        ],
                    },
                ],
            },
            {
                "name": "Зміна професії",
                "keywords": [
                    "безкоштовне навчання професії",
                    "як змінити професію без досвіду",
                    "громадська організація навчання професій",
                ],
                "ads": [
                    {
                        "headlines": ["Змінити професію", "Навчання безкоштовне",
                                      "Почати з нуля", "Освітній проєкт", "Без досвіду"],
                        "descriptions": [
                            "Безкоштовна освіта для тих, хто змінює професію та починає з нуля.",
                            "Курси менеджера міжнародної нерухомості та рекрутера.",
                            "Громадська організація «Незалежність»: навчання та підтримка.",
                        ],
                    },
                    {
                        "headlines": ["Нова професія", "Курси від організації",
                                      "Теорія та практика", "Заповніть анкету",
                                      "Старт карʼєри"],
                        "descriptions": [
                            "Оберіть напрям: міжнародна нерухомість або рекрутинг.",
                            "Навчання складається з теорії та тривалої практичної частини.",
                            "Проєкт неприбуткової організації, оплата не потрібна.",
                        ],
                    },
                ],
            },
            {
                "name": "Русский",
                "keywords": [
                    "бесплатное обучение профессии с нуля",
                    "как стать менеджером по зарубежной недвижимости",
                    "обучение международной недвижимости",
                ],
                "ads": [
                    {
                        "headlines": ["Бесплатное обучение", "Профессия с нуля",
                                      "Теория и практика", "Курс от организации",
                                      "Начните карьеру"],
                        "descriptions": [
                            "Бесплатный курс менеджера по зарубежной недвижимости и рекрутера.",
                            "Неделя теории и 44 дня практики с поддержкой наставников.",
                            "Образовательный проект общественной организации.",
                        ],
                    },
                    {
                        "headlines": ["Обучение без оплаты", "Смена профессии",
                                      "Практические навыки", "Заполните анкету",
                                      "Учиться онлайн"],
                        "descriptions": [
                            "Получите профессию в сфере международной недвижимости бесплатно.",
                            "Не только теория: база для отработки практических навыков.",
                            "Проект некоммерческой организации для тех, кто начинает карьеру.",
                        ],
                    },
                ],
            },
        ],
    },
}


def check_texts():
    """Длины заголовков и описаний по требованиям RSA."""
    problems = []
    for key, spec in CAMPAIGNS.items():
        for group in spec["groups"]:
            for ad in group["ads"]:
                if len(ad["headlines"]) < 3:
                    problems.append(f"{key}/{group['name']}: меньше трёх заголовков")
                if len(ad["descriptions"]) < 2:
                    problems.append(f"{key}/{group['name']}: меньше двух описаний")
                for text in ad["headlines"]:
                    if len(text) > 30:
                        problems.append(f"{key}: заголовок {len(text)} симв. — {text}")
                for text in ad["descriptions"]:
                    if len(text) > 90:
                        problems.append(f"{key}: описание {len(text)} симв. — {text}")
    return problems


def build(client, key, spec, temp_base):
    """Пачка операций на одну кампанию. temp_base разводит временные id кампаний."""
    enums = client.enums
    operations = []

    def new_op():
        op = client.get_type("MutateOperation")
        operations.append(op)
        return op

    temp = temp_base
    budget_rn = f"customers/{CID}/campaignBudgets/{temp}"
    temp -= 1
    campaign_rn = f"customers/{CID}/campaigns/{temp}"
    temp -= 1

    budget = new_op().campaign_budget_operation.create
    budget.resource_name = budget_rn
    budget.name = spec["name"]
    budget.amount_micros = spec["budget"] * 1_000_000
    budget.delivery_method = enums.BudgetDeliveryMethodEnum.STANDARD
    budget.explicitly_shared = False

    campaign = new_op().campaign_operation.create
    campaign.resource_name = campaign_rn
    campaign.name = spec["name"]
    campaign.status = enums.CampaignStatusEnum.PAUSED
    campaign.advertising_channel_type = enums.AdvertisingChannelTypeEnum.SEARCH
    campaign.campaign_budget = budget_rn
    campaign.maximize_conversions.target_cpa_micros = 0
    campaign.network_settings.target_google_search = True
    campaign.network_settings.target_search_network = False
    campaign.network_settings.target_content_network = False
    campaign.network_settings.target_partner_search_network = False
    campaign.geo_target_type_setting.positive_geo_target_type = (
        enums.PositiveGeoTargetTypeEnum.PRESENCE_OR_INTEREST
    )
    campaign.contains_eu_political_advertising = (
        enums.EuPoliticalAdvertisingStatusEnum.DOES_NOT_CONTAIN_EU_POLITICAL_ADVERTISING
    )
    campaign.start_date = "2026-08-28"
    campaign.end_date = "2037-12-30"

    for text in spec["negatives"]:
        criterion = new_op().campaign_criterion_operation.create
        criterion.campaign = campaign_rn
        criterion.negative = True
        criterion.keyword.text = text
        criterion.keyword.match_type = enums.KeywordMatchTypeEnum.PHRASE

    for group in spec["groups"]:
        group_rn = f"customers/{CID}/adGroups/{temp}"
        temp -= 1

        ad_group = new_op().ad_group_operation.create
        ad_group.resource_name = group_rn
        ad_group.name = group["name"]
        ad_group.campaign = campaign_rn
        ad_group.status = enums.AdGroupStatusEnum.ENABLED
        ad_group.type_ = enums.AdGroupTypeEnum.SEARCH_STANDARD

        for ad_spec in group["ads"]:
            ad_group_ad = new_op().ad_group_ad_operation.create
            ad_group_ad.ad_group = group_rn
            ad_group_ad.status = enums.AdGroupAdStatusEnum.ENABLED
            ad_group_ad.ad.final_urls.append(spec["final_url"])
            for text in ad_spec["headlines"]:
                asset = client.get_type("AdTextAsset")
                asset.text = text
                ad_group_ad.ad.responsive_search_ad.headlines.append(asset)
            for text in ad_spec["descriptions"]:
                asset = client.get_type("AdTextAsset")
                asset.text = text
                ad_group_ad.ad.responsive_search_ad.descriptions.append(asset)

        for text in group["keywords"]:
            for match in (enums.KeywordMatchTypeEnum.PHRASE, enums.KeywordMatchTypeEnum.EXACT):
                criterion = new_op().ad_group_criterion_operation.create
                criterion.ad_group = group_rn
                criterion.status = enums.AdGroupCriterionStatusEnum.ENABLED
                criterion.keyword.text = text
                criterion.keyword.match_type = match

    return operations


def summarize(key, spec):
    groups = len(spec["groups"])
    ads = sum(len(g["ads"]) for g in spec["groups"])
    keywords = sum(len(g["keywords"]) for g in spec["groups"]) * 2
    print(f"\n[{key}] «{spec['name']}»")
    print(f"  посадочная: {spec['final_url']}")
    print(f"  статус PAUSED, бюджет ${spec['budget']}/день, стратегия Maximize Conversions")
    print(f"  групп {groups}, объявлений {ads}, ключей {keywords} "
          f"(phrase+exact), минус-слов {len(spec['negatives'])}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", choices=sorted(CAMPAIGNS), help="создать одну кампанию")
    parser.add_argument("--apply", action="store_true",
                        help="создать на самом деле; без флага только проверка")
    args = parser.parse_args()

    problems = check_texts()
    if problems:
        print("Тексты не проходят проверку:")
        for problem in problems:
            print("  " + problem)
        raise SystemExit(1)

    client = GoogleAdsClient(
        credentials=service_account.Credentials.from_service_account_file(
            os.environ.get("GOOGLE_SA_KEY", ".secrets/gstar-sa.json"),
            scopes=["https://www.googleapis.com/auth/adwords"],
        ),
        developer_token=DEVELOPER_TOKEN,
        login_customer_id=LOGIN_CID,
        version="v22",
        use_proto_plus=True,
    )
    service = client.get_service("GoogleAdsService")

    keys = [args.only] if args.only else list(CAMPAIGNS)
    print("Режим: " + ("СОЗДАНИЕ" if args.apply else "проверка, ничего не создаётся"))

    for index, key in enumerate(keys):
        spec = CAMPAIGNS[key]
        summarize(key, spec)
        operations = build(client, key, spec, temp_base=-1 - index * 100)

        request = client.get_type("MutateGoogleAdsRequest")
        request.customer_id = CID
        request.mutate_operations = operations
        request.validate_only = not args.apply

        try:
            response = service.mutate(request=request)
        except GoogleAdsException as err:
            print("  ОТКЛОНЕНО:")
            for error in err.failure.errors:
                path = ".".join(x.field_name for x in error.location.field_path_elements)
                print(f"    {error.message} | поле: {path}")
            raise SystemExit(1)

        if args.apply:
            for result in response.mutate_operation_responses:
                kind = result._pb.WhichOneof("response")
                if kind in ("campaign_result", "campaign_budget_result"):
                    print(f"  создано {kind}: {getattr(result, kind).resource_name}")
            print("  кампания создана и остановлена")
        else:
            print(f"  проверка пройдена, операций в пачке: {len(operations)}")

    if not args.apply:
        print("\nНичего не создано. Для создания добавьте --apply")


if __name__ == "__main__":
    main()
