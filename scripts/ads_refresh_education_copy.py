#!/usr/bin/env python3
"""Replace placeholder RSA copy in the paused EDU campaigns. Never enables anything."""
import argparse
import pathlib

from google.ads.googleads.client import GoogleAdsClient

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONFIG = ROOT / ".secrets" / "google-ads.yaml"

COPY = {
    "Проверка застройщика": (
        ["Проверить застройщика", "Чек-лист до бронирования", "Что спросить у девелопера", "Документы без лишних слов", "Получить чек-лист", "Файл в Telegram"],
        ["Чек-лист: что запросить до бронирования и как проверить девелопера.", "Получите файл в Telegram. Без звонка, прайса и навязчивого менеджера."],
    ),
    "Документы и риски": (
        ["Документы до сделки", "Карта проверки документов", "Вопросы для юриста", "Не пропустите важное", "Получить карту документов", "Файл в Telegram"],
        ["Список документов и вопросов, которые стоит задать до сделки за рубежом.", "Гид придёт в Telegram. На странице нет каталога, цен и скрытых условий."],
    ),
    "Финансовая модель": (
        ["Посчитать доход от аренды", "Финансовая модель аренды", "Доход, простои, расходы", "Не верьте цифре из рекламы", "Получить шаблон расчёта", "Файл в Telegram"],
        ["Шаблон расчёта: доход, простои, расходы и вопросы к управляющей компании.", "Получите файл в Telegram и посчитайте свой сценарий до выбора объекта."],
    ),
    "Ошибки инвестора": (
        ["Семь ошибок инвестора", "До первого платежа", "Проверьте свой сценарий", "Не потерять деньги", "Получить гид", "Файл в Telegram"],
        ["Гид о семи ошибках, которые часто замечают уже после перевода денег.", "Получите файл в Telegram и отметьте риски, которые относятся к вашей ситуации."],
    ),
    "Управление объектом": (
        ["Как управляют объектом", "Чек-лист для собственника", "Расходы после покупки", "Вопросы к управляющей", "Получить чек-лист", "Файл в Telegram"],
        ["Разберите расходы, договор и обязанности управляющей компании до подписания.", "Чек-лист придёт в Telegram. Он поможет сравнить ответы без спешки."],
    ),
    "Выбор страны": (
        ["Сравнить страны для жизни", "Гид по выбору страны", "Не выбирать по открытке", "Вопросы до переезда", "Получить сравнительный гид", "Файл в Telegram"],
        ["Сравните страны по вашему плану: жизнь, документы, климат и повседневность.", "Гид придёт в Telegram. Сначала разберитесь в маршруте, потом в объектах."],
    ),
    "Вебинары": (
        ["Открытый разбор рисков", "Вебинар без продаж", "Вопросы до сделки", "Проверка без спешки", "Получить приглашение", "В Telegram"],
        ["Открытый разбор того, что проверить до сделки и разговора с посредником.", "Получите приглашение в Telegram. В эфире можно задать свой вопрос."],
    ),
    "Гражданство | Гренада": (
        ["Гражданство Гренады", "Карта проверки программы", "Источники и документы", "Вопросы к посреднику", "Проверить до обращения", "Файл в Telegram"],
        ["Карта проверки: источники, документы, посредник и вопросы для юриста.", "Получите материал в Telegram. Без обещаний результата, сроков и сумм."],
    ),
    "Гражданство | Антигуа": (
        ["Гражданство Антигуа", "Карта проверки программы", "Источники и документы", "Вопросы к посреднику", "Проверить до обращения", "Файл в Telegram"],
        ["Разберите официальные источники, документы и вопросы к посреднику.", "Материал придёт в Telegram. Без обещаний результата, сроков и сумм."],
    ),
    "Гражданство | Доминика": (
        ["Гражданство Доминики", "Карта проверки программы", "Источники и документы", "Вопросы к посреднику", "Проверить до обращения", "Файл в Telegram"],
        ["Разберите официальные источники, документы и вопросы к посреднику.", "Материал придёт в Telegram. Без обещаний результата, сроков и сумм."],
    ),
    "Гражданство | Сент-Китс": (
        ["Гражданство Сент-Китс", "Карта проверки программы", "Источники и документы", "Вопросы к посреднику", "Проверить до обращения", "Файл в Telegram"],
        ["Разберите официальные источники, документы и вопросы к посреднику.", "Материал придёт в Telegram. Без обещаний результата, сроков и сумм."],
    ),
    "Страна | Грузия": (
        ["Недвижимость в Грузии", "Гид по выбору страны", "Документы до разговора", "Проверить объект в Грузии", "Получить гид", "Файл в Telegram"],
        ["Гид по Грузии: какие документы запросить и что проверить до разговора об объекте.", "Получите файл в Telegram. Без каталога, цен и попытки продать вам квартиру."],
    ),
    "Страна | Камбоджа": (
        ["Недвижимость в Камбодже", "Гид по выбору страны", "Документы до разговора", "Проверить объект в Камбодже", "Получить гид", "Файл в Telegram"],
        ["Гид по Камбодже: какие документы запросить и что проверить до разговора об объекте.", "Получите файл в Telegram. Без каталога, цен и попытки продать вам квартиру."],
    ),
    "Страна | Мальдивы": (
        ["Недвижимость на Мальдивах", "Гид по выбору страны", "Документы до разговора", "Проверить объект на Мальдивах", "Получить гид", "Файл в Telegram"],
        ["Гид по Мальдивам: какие документы запросить и что проверить до разговора об объекте.", "Получите файл в Telegram. Без каталога, цен и попытки продать вам квартиру."],
    ),
}


def customer_id():
    for line in CONFIG.read_text(encoding="utf-8").splitlines():
        if line.startswith("# Рабочий аккаунт:"):
            return line.split(":", 1)[1].strip()
    raise RuntimeError("Не найден рабочий аккаунт.")


def add_assets(client, collection, values):
    for value in values:
        asset = client.get_type("AdTextAsset")
        asset.text = value
        collection.append(asset)


def validate_copy():
    for campaign, (headlines, descriptions) in COPY.items():
        for headline in headlines:
            if len(headline) > 30:
                raise ValueError(f"Заголовок длиннее 30 символов: {campaign}: {headline}")
        for description in descriptions:
            if len(description) > 90:
                raise ValueError(f"Description длиннее 90 символов: {campaign}: {description}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    validate_copy()
    client = GoogleAdsClient.load_from_storage(str(CONFIG))
    cid = customer_id()
    rows = client.get_service("GoogleAdsService").search(customer_id=cid, query="""
        SELECT campaign.name, ad_group_ad.resource_name, ad_group_ad.ad_group,
               ad_group_ad.ad.final_urls, ad_group_ad.status
        FROM ad_group_ad
        WHERE campaign.name LIKE '%EDU%'
          AND ad_group_ad.ad.type = 'RESPONSIVE_SEARCH_AD'
          AND campaign.status != 'REMOVED'
    """)
    operations = []
    for row in rows:
        title = row.campaign.name.replace("[PAUSED] EDU | ", "", 1)
        if title not in COPY:
            raise RuntimeError(f"Нет копирайта для кампании: {row.campaign.name}")
        headlines, descriptions = COPY[title]
        print(f"{row.campaign.name}: {descriptions[0]} / {descriptions[1]}")
        operation = client.get_type("AdGroupAdOperation")
        replacement = operation.create
        replacement.ad_group = row.ad_group_ad.ad_group
        replacement.status = client.enums.AdGroupAdStatusEnum.PAUSED
        replacement.ad.final_urls.extend(row.ad_group_ad.ad.final_urls)
        add_assets(client, replacement.ad.responsive_search_ad.headlines, headlines)
        add_assets(client, replacement.ad.responsive_search_ad.descriptions, descriptions)
        operations.append(operation)
    if len(operations) != len(COPY):
        raise RuntimeError(f"Ожидалось {len(COPY)} RSA, найдено {len(operations)}.")
    if not args.apply:
        print("Предпросмотр: изменения не отправлены. Все кампании останутся PAUSED.")
        return
    client.get_service("AdGroupAdService").mutate_ad_group_ads(customer_id=cid, operations=operations)
    print("Созданы новые RSA с обновлённым копирайтом. Все новые и исходные RSA остаются PAUSED.")


if __name__ == "__main__":
    main()
