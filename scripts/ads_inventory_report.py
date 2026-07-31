#!/usr/bin/env python3
"""Read-only Google Ads inventory export to a Markdown audit report."""
from __future__ import annotations

import datetime as dt
import pathlib
from collections import defaultdict

from google.ads.googleads.client import GoogleAdsClient

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONFIG = ROOT / ".secrets" / "google-ads.yaml"
REPORT = ROOT / "docs" / "ADS-INVENTORY-2026-07-29.md"
MICROS = 1_000_000


def customer_id() -> str:
    for line in CONFIG.read_text(encoding="utf-8").splitlines():
        if line.startswith("# Рабочий аккаунт:"):
            return line.split(":", 1)[1].strip()
    raise RuntimeError("Не найден рабочий аккаунт в конфигурации.")


def esc(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", "<br>")


def name(value) -> str:
    return value.name if hasattr(value, "name") else str(value)


def category(campaign_name: str, channel: str) -> str:
    lower = campaign_name.lower()
    if "[paused] edu" in lower:
        return "Новые просветительские Search"
    if "pmax" in lower or channel == "PERFORMANCE_MAX":
        return "PMax / нецелевые коммерческие"
    if any(term in lower for term in ("work", "rabota", "работ", "вакан", "риелтор")):
        return "Поиск работы / нерелевантное"
    if channel == "SEARCH":
        return "Старые Search-кампании"
    return "Архив и прочее"


def score(campaign_name: str, channel: str, status: str, ad_count: int, keyword_count: int) -> str:
    lower = campaign_name.lower()
    if "[paused] edu" in lower:
        return "4/5 — структура и оффер соответствуют просветительской посадочной; трафика ещё нет, поэтому QS/CTR не оценить."
    if any(term in lower for term in ("work", "rabota", "работ", "вакан")):
        return "0/5 — вакансии и работа не соответствуют миссии и посадочным."
    if "pmax" in lower or channel == "PERFORMANCE_MAX":
        return "1/5 — не соответствует новой Search-структуре; оставлена на паузе."
    if status == "PAUSED" and not ad_count:
        return "1/5 — архив без доступных объявлений для оценки."
    if not keyword_count:
        return "2/5 — нет видимой поисковой структуры для проверки релевантности."
    return "2/5 — историческая структура; нужна отдельная пересборка под страницу и намерение запроса."


def main() -> None:
    if not CONFIG.exists():
        raise SystemExit("Нет Google Ads конфигурации.")
    client = GoogleAdsClient.load_from_storage(str(CONFIG))
    cid = customer_id()
    service = client.get_service("GoogleAdsService")

    campaign_rows = list(service.search(customer_id=cid, query="""
        SELECT campaign.id, campaign.name, campaign.status,
               campaign.advertising_channel_type, campaign.bidding_strategy_type,
               campaign_budget.amount_micros,
               campaign.target_cpa.target_cpa_micros,
               campaign.maximize_conversions.target_cpa_micros
        FROM campaign
        WHERE campaign.status != 'REMOVED'
        ORDER BY campaign.name
    """))
    campaigns = {}
    for row in campaign_rows:
        campaign = row.campaign
        cid_num = int(campaign.id)
        tcpa = campaign.target_cpa.target_cpa_micros or campaign.maximize_conversions.target_cpa_micros
        campaigns[cid_num] = {
            "name": campaign.name,
            "status": name(campaign.status),
            "channel": name(campaign.advertising_channel_type),
            "strategy": name(campaign.bidding_strategy_type),
            "budget": row.campaign_budget.amount_micros / MICROS,
            "tcpa": tcpa / MICROS if tcpa else None,
        }

    ads = defaultdict(list)
    try:
        ad_rows = service.search(customer_id=cid, query="""
            SELECT campaign.id, ad_group.id, ad_group.name, ad_group.status,
                   ad_group.cpc_bid_micros, ad_group.target_cpa_micros,
                   ad_group_ad.status, ad_group_ad.ad.type,
                   ad_group_ad.ad.final_urls,
                   ad_group_ad.ad.responsive_search_ad.headlines,
                   ad_group_ad.ad.responsive_search_ad.descriptions
            FROM ad_group_ad
            WHERE campaign.status != 'REMOVED'
              AND ad_group.status != 'REMOVED'
              AND ad_group_ad.ad.type = 'RESPONSIVE_SEARCH_AD'
        """)
        for row in ad_rows:
            rsa = row.ad_group_ad.ad.responsive_search_ad
            ads[int(row.campaign.id)].append({
                "group": row.ad_group.name,
                "group_status": name(row.ad_group.status),
                "ad_status": name(row.ad_group_ad.status),
                "cpc": row.ad_group.cpc_bid_micros / MICROS if row.ad_group.cpc_bid_micros else None,
                "tcpa": row.ad_group.target_cpa_micros / MICROS if row.ad_group.target_cpa_micros else None,
                "urls": list(row.ad_group_ad.ad.final_urls),
                "headlines": [asset.text for asset in rsa.headlines],
                "descriptions": [asset.text for asset in rsa.descriptions],
            })
    except Exception as error:
        print(f"Не удалось получить RSA: {error}")

    keywords = defaultdict(list)
    try:
        keyword_rows = service.search(customer_id=cid, query="""
            SELECT campaign.id, ad_group.id, ad_group_criterion.keyword.text,
                   ad_group_criterion.keyword.match_type, ad_group_criterion.status,
                   ad_group_criterion.quality_info.quality_score
            FROM keyword_view
            WHERE campaign.status != 'REMOVED'
              AND ad_group.status != 'REMOVED'
            LIMIT 2000
        """)
        for row in keyword_rows:
            criterion = row.ad_group_criterion
            keywords[int(row.campaign.id)].append({
                "text": criterion.keyword.text,
                "match": name(criterion.keyword.match_type),
                "status": name(criterion.status),
                "quality": criterion.quality_info.quality_score or "—",
            })
        education_rows = service.search(customer_id=cid, query="""
            SELECT campaign.id, ad_group.id, ad_group_criterion.keyword.text,
                   ad_group_criterion.keyword.match_type, ad_group_criterion.status,
                   ad_group_criterion.quality_info.quality_score
            FROM keyword_view
            WHERE campaign.name LIKE '%EDU%'
              AND ad_group.status != 'REMOVED'
        """)
        known = {(campaign_id, item["text"], item["match"]) for campaign_id, items in keywords.items() for item in items}
        for row in education_rows:
            criterion = row.ad_group_criterion
            item = {
                "text": criterion.keyword.text,
                "match": name(criterion.keyword.match_type),
                "status": name(criterion.status),
                "quality": criterion.quality_info.quality_score or "—",
            }
            key = (int(row.campaign.id), item["text"], item["match"])
            if key not in known:
                keywords[int(row.campaign.id)].append(item)
                known.add(key)
    except Exception as error:
        print(f"Не удалось получить ключи: {error}")

    assets = defaultdict(list)
    for resource, label in (("campaign_asset", "Кампания"), ("ad_group_asset", "Группа")):
        try:
            asset_rows = service.search(customer_id=cid, query=f"""
                SELECT campaign.id, asset.type, asset.name,
                       asset.final_urls, asset.sitelink_asset.link_text,
                       asset.callout_asset.callout_text, asset.call_asset.phone_number,
                       asset.structured_snippet_asset.header, asset.structured_snippet_asset.values
                FROM {resource}
                WHERE asset.type IN ('SITELINK', 'CALLOUT', 'CALL', 'STRUCTURED_SNIPPET')
            """)
            for row in asset_rows:
                asset = row.asset
                asset_type = name(asset.type)
                details = ""
                if asset_type == "SITELINK":
                    details = f"{asset.sitelink_asset.link_text} → {', '.join(asset.final_urls)}"
                elif asset_type == "CALLOUT":
                    details = asset.callout_asset.callout_text
                elif asset_type == "CALL":
                    details = asset.call_asset.phone_number
                elif asset_type == "STRUCTURED_SNIPPET":
                    details = f"{asset.structured_snippet_asset.header}: {', '.join(asset.structured_snippet_asset.values)}"
                assets[int(row.campaign.id)].append(f"{label}: {asset_type} — {details}")
        except Exception as error:
            print(f"Не удалось получить расширения {resource}: {error}")

    groups = defaultdict(list)
    for campaign_id, campaign in campaigns.items():
        campaign["id"] = campaign_id
        groups[category(campaign["name"], campaign["channel"])].append(campaign)

    lines = [
        "# Инвентаризация Google Ads",
        "",
        f"Срез подготовлен **{dt.date.today().isoformat()}** через Google Ads API. Отчёт только читает аккаунт; изменения в Ads не вносились.",
        "",
        "## Как читать оценку",
        "",
        "Оценка относится к соответствию новой просветительской Search-структуре и качеству видимой связки «запрос → объявление → посадочная». Она не является Google Ads Quality Score: без трафика и показов QS/CTR нельзя честно рассчитать.",
        "",
        "## Сводка",
        "",
        f"- Кампаний в инвентаре: **{len(campaigns)}**.",
        f"- RSA-объявлений: **{sum(len(value) for value in ads.values())}**.",
        f"- Ключевых слов в отчёте: **{sum(len(value) for value in keywords.values())}** (исторические кампании ограничены первыми 2 000; все ключи новых EDU включены полностью).",
        f"- Новых просветительских кампаний: **{len(groups['Новые просветительские Search'])}**, все должны быть PAUSED до отдельного запуска.",
        "",
    ]

    for group_name, items in groups.items():
        lines += [f"## {group_name}", "", "| Кампания | Статус | Канал | Стратегия / ставка | Дневной бюджет | Объявления | Ключи | Оценка |", "|---|---|---|---|---:|---:|---:|---|"]
        for item in items:
            strategy = item["strategy"]
            if item["tcpa"]:
                strategy += f" · tCPA {item['tcpa']:.2f}"
            lines.append(
                f"| {esc(item['name'])} | {item['status']} | {item['channel']} | {esc(strategy)} | {item['budget']:.2f} | {len(ads[item['id']])} | {len(keywords[item['id']])} | {esc(score(item['name'], item['channel'], item['status'], len(ads[item['id']]), len(keywords[item['id']]))) } |"
            )
        lines.append("")

        for item in items:
            campaign_ads = ads[item["id"]]
            campaign_keywords = keywords[item["id"]]
            campaign_assets = assets[item["id"]]
            lines += [f"### {item['name']}", "", f"- **ID:** `{item['id']}`", f"- **Куда ведёт:** {', '.join(sorted({url for ad in campaign_ads for url in ad['urls']})) or 'URL не задан в Search RSA / проверить тип кампании.'}", f"- **Что предлагает:** {'Бесплатный просветительский материал и форма в мессенджер.' if '[PAUSED] EDU' in item['name'] else 'Смотреть тексты ниже: это историческая связка, не запускать без отдельной проверки.'}", f"- **Оценка:** {score(item['name'], item['channel'], item['status'], len(campaign_ads), len(campaign_keywords))}", ""]
            if campaign_ads:
                lines += ["#### Объявления", "", "| Группа | Статус группы / RSA | Ставка группы | Заголовки | Descriptions | Final URL |", "|---|---|---:|---|---|---|"]
                for ad in campaign_ads:
                    bid = f"CPC {ad['cpc']:.2f}" if ad["cpc"] else (f"tCPA {ad['tcpa']:.2f}" if ad["tcpa"] else "на уровне кампании")
                    lines.append(f"| {esc(ad['group'])} | {ad['group_status']} / {ad['ad_status']} | {bid} | {esc('<br>'.join(ad['headlines']))} | {esc('<br>'.join(ad['descriptions']))} | {esc('<br>'.join(ad['urls']))} |")
                lines.append("")
            else:
                lines += ["#### Объявления", "", "Нет RSA в выдаче API: для PMax или архивной кампании тексты могут быть в других типах ассетов.", ""]
            if campaign_keywords:
                lines += ["#### Ключевые слова", "", "| Ключ | Соответствие | Статус | QS |", "|---|---|---|---|"]
                for keyword in campaign_keywords:
                    lines.append(f"| {esc(keyword['text'])} | {keyword['match']} | {keyword['status']} | {keyword['quality']} |")
                lines.append("")
            if campaign_assets:
                lines += ["#### Расширения", ""]
                lines.extend([f"- {esc(asset)}" for asset in campaign_assets])
                lines.append("")
            else:
                lines += ["#### Расширения", "", "Расширения уровня кампании/группы в API не найдены.", ""]

    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(REPORT)


if __name__ == "__main__":
    main()
