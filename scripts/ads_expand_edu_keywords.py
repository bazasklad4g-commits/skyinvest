#!/usr/bin/env python3
"""Add approved, higher-demand informational keywords to EDU campaigns.

This script never creates broad-match keywords and never changes budgets,
campaign status, ads or targeting. Run without --apply to preview changes.
"""
from __future__ import annotations

import argparse
import pathlib

from google.ads.googleads.client import GoogleAdsClient


ROOT = pathlib.Path(__file__).resolve().parent.parent
CONFIG = ROOT / ".secrets" / "google-ads.yaml"
CAMPAIGN_PREFIX = "[PAUSED] EDU | "
CLEAN_GROUP_PREFIX = "[CLEAN] EDU | "

# Ideas were screened through Keyword Planner on 2026-08-03. Each phrase is
# relevant to the free material on its landing page and avoids commercial terms.
EXPANSIONS = {
    "Проверка застройщика": ["проверка застройщика", "как проверить застройщика"],
    "Документы и риски": ["документы на квартиру"],
    "Финансовая модель": ["как считать доходность", "доходность недвижимости"],
    "Управление объектом": ["управление недвижимостью", "договор управления недвижимостью"],
    "Выбор страны": ["как переехать в другую страну"],
    "Грузия | Реестр": ["публичный реестр грузии", "выписка из реестра грузии"],
    "Испания | Nota Simple": ["nota simple"],
    "Гражданство | Гренада": ["гражданство гренады"],
    "Гражданство | Доминика": ["гражданство доминики"],
    "Гражданство | Антигуа": ["гражданство антигуа"],
    "Гражданство | Сент-Китс": ["гражданство сент китс"],
}
BLOCKED = ("купить", "продаж", "цен", "стоим", "прайс", "каталог", "паспорт")


def customer_id() -> str:
    for line in CONFIG.read_text(encoding="utf-8").splitlines():
        if line.startswith("# Рабочий аккаунт:"):
            return line.split(":", 1)[1].strip()
    raise RuntimeError("В google-ads.yaml нет рабочего аккаунта.")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="добавить ключи в Google Ads")
    args = parser.parse_args()
    if not CONFIG.exists():
        raise SystemExit(f"Нет конфигурации {CONFIG}")
    for terms in EXPANSIONS.values():
        for term in terms:
            if any(word in term.lower() for word in BLOCKED):
                raise RuntimeError(f"Запрещённая формулировка в списке: {term}")

    client = GoogleAdsClient.load_from_storage(str(CONFIG))
    cid = customer_id()
    service = client.get_service("GoogleAdsService")
    campaign_rows = service.search(customer_id=cid, query="""
        SELECT campaign.id, campaign.name
        FROM campaign
        WHERE campaign.name LIKE '%EDU%' AND campaign.status != 'REMOVED'
    """)
    campaigns = {
        row.campaign.name.removeprefix(CAMPAIGN_PREFIX): row.campaign
        for row in campaign_rows
        if row.campaign.name.startswith(CAMPAIGN_PREFIX)
    }
    if set(EXPANSIONS) - set(campaigns):
        raise RuntimeError(f"Не найдены кампании: {sorted(set(EXPANSIONS) - set(campaigns))}")

    operations = []
    summary = []
    for short_name, proposed in EXPANSIONS.items():
        campaign = campaigns[short_name]
        groups = list(service.search(customer_id=cid, query=f"""
            SELECT ad_group.resource_name, ad_group.name
            FROM ad_group
            WHERE campaign.id = {campaign.id} AND ad_group.status != 'REMOVED'
        """))
        clean_groups = [row.ad_group for row in groups if row.ad_group.name.startswith(CLEAN_GROUP_PREFIX)]
        if len(clean_groups) != 1:
            raise RuntimeError(f"{short_name}: найдена не одна clean-группа.")
        group = clean_groups[0]
        group_id = group.resource_name.rsplit("/", 1)[-1]
        current_rows = service.search(customer_id=cid, query=f"""
            SELECT ad_group_criterion.keyword.text
            FROM keyword_view
            WHERE ad_group.id = {group_id} AND ad_group_criterion.status != 'REMOVED'
        """)
        existing = {row.ad_group_criterion.keyword.text.lower() for row in current_rows}
        additions = [term for term in proposed if term.lower() not in existing]
        summary.append((short_name, additions))
        if args.apply:
            for term in additions:
                for match_name in ("PHRASE", "EXACT"):
                    operation = client.get_type("AdGroupCriterionOperation")
                    criterion = operation.create
                    criterion.ad_group = group.resource_name
                    criterion.status = client.enums.AdGroupCriterionStatusEnum.ENABLED
                    criterion.keyword.text = term
                    criterion.keyword.match_type = client.enums.KeywordMatchTypeEnum[match_name]
                    operations.append(operation)

    for name, additions in summary:
        print(f"{name}: " + (", ".join(additions) if additions else "без новых ключей"))
    if not args.apply:
        print("Проверка завершена. Используйте --apply для внесения изменений.")
        return
    if operations:
        client.get_service("AdGroupCriterionService").mutate_ad_group_criteria(
            customer_id=cid, operations=operations
        )
    print(f"Добавлено ключей: {len(operations)} (phrase/exact).")


if __name__ == "__main__":
    main()
