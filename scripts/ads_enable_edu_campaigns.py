#!/usr/bin/env python3
"""Enable the approved EDU Search campaigns and their clean child assets.

Runs in dry-run mode by default. With --apply it changes only campaigns named
"[PAUSED] EDU | …", their one clean ad group, one RSA and that group's paused
positive keywords. It never touches older campaigns or campaign budgets.
"""
from __future__ import annotations

import argparse
import pathlib

from google.ads.googleads.client import GoogleAdsClient


ROOT = pathlib.Path(__file__).resolve().parent.parent
CONFIG = ROOT / ".secrets" / "google-ads.yaml"
PREFIX = "[PAUSED] EDU | "
CLEAN_PREFIX = "[CLEAN] EDU | "


def customer_id() -> str:
    for line in CONFIG.read_text(encoding="utf-8").splitlines():
        if line.startswith("# Рабочий аккаунт:"):
            return line.split(":", 1)[1].strip()
    raise RuntimeError("В google-ads.yaml нет рабочего аккаунта.")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="включить проверенные кампании")
    args = parser.parse_args()
    if not CONFIG.exists():
        raise SystemExit(f"Нет конфигурации {CONFIG}")

    client = GoogleAdsClient.load_from_storage(str(CONFIG))
    cid = customer_id()
    service = client.get_service("GoogleAdsService")
    rows = list(service.search(customer_id=cid, query="""
        SELECT campaign.resource_name, campaign.id, campaign.name, campaign.status
        FROM campaign
        WHERE campaign.status != 'REMOVED' AND campaign.name LIKE '%EDU%'
        ORDER BY campaign.name
    """))
    campaigns = [row.campaign for row in rows if row.campaign.name.startswith(PREFIX)]
    if len(campaigns) != 24:
        raise RuntimeError(f"Ожидалось 24 EDU-кампании, найдено {len(campaigns)}.")

    campaign_operations = []
    group_operations = []
    ad_operations = []
    criterion_operations = []

    for campaign in campaigns:
        group_rows = list(service.search(customer_id=cid, query=f"""
            SELECT ad_group.resource_name, ad_group.name, ad_group.status
            FROM ad_group
            WHERE campaign.id = {campaign.id} AND ad_group.status != 'REMOVED'
        """))
        clean_groups = [row.ad_group for row in group_rows if row.ad_group.name.startswith(CLEAN_PREFIX)]
        if len(clean_groups) != 1:
            raise RuntimeError(f"{campaign.name}: нужна ровно одна clean-группа, найдено {len(clean_groups)}.")
        group = clean_groups[0]

        ad_rows = list(service.search(customer_id=cid, query=f"""
            SELECT ad_group_ad.resource_name, ad_group_ad.status, ad_group_ad.ad.type
            FROM ad_group_ad
            WHERE ad_group.id = {group.resource_name.rsplit('/', 1)[-1]}
              AND ad_group_ad.status != 'REMOVED'
              AND ad_group_ad.ad.type = 'RESPONSIVE_SEARCH_AD'
        """))
        if len(ad_rows) != 1:
            raise RuntimeError(f"{campaign.name}: нужна ровно одна RSA, найдено {len(ad_rows)}.")

        keyword_rows = list(service.search(customer_id=cid, query=f"""
            SELECT ad_group_criterion.resource_name, ad_group_criterion.status
            FROM keyword_view
            WHERE campaign.id = {campaign.id}
              AND ad_group.id = {group.resource_name.rsplit('/', 1)[-1]}
              AND ad_group_criterion.status != 'REMOVED'
        """))
        resources = {row.ad_group_criterion.resource_name for row in keyword_rows}
        if len(resources) < 6:
            raise RuntimeError(f"{campaign.name}: найдено только {len(resources)} активных ключей.")

        print(f"{campaign.name}: group={group.status.name}, rsa={ad_rows[0].ad_group_ad.status.name}, keywords={len(resources)}")
        if not args.apply:
            continue

        if campaign.status.name != "ENABLED":
            operation = client.get_type("CampaignOperation")
            operation.update.resource_name = campaign.resource_name
            operation.update.status = client.enums.CampaignStatusEnum.ENABLED
            operation.update_mask.paths.append("status")
            campaign_operations.append(operation)
        if group.status.name != "ENABLED":
            operation = client.get_type("AdGroupOperation")
            operation.update.resource_name = group.resource_name
            operation.update.status = client.enums.AdGroupStatusEnum.ENABLED
            operation.update_mask.paths.append("status")
            group_operations.append(operation)
        if ad_rows[0].ad_group_ad.status.name != "ENABLED":
            operation = client.get_type("AdGroupAdOperation")
            operation.update.resource_name = ad_rows[0].ad_group_ad.resource_name
            operation.update.status = client.enums.AdGroupAdStatusEnum.ENABLED
            operation.update_mask.paths.append("status")
            ad_operations.append(operation)
        for resource_name in resources:
            operation = client.get_type("AdGroupCriterionOperation")
            operation.update.resource_name = resource_name
            operation.update.status = client.enums.AdGroupCriterionStatusEnum.ENABLED
            operation.update_mask.paths.append("status")
            criterion_operations.append(operation)

    if not args.apply:
        print("Проверка пройдена. Для включения используйте --apply.")
        return

    if criterion_operations:
        client.get_service("AdGroupCriterionService").mutate_ad_group_criteria(customer_id=cid, operations=criterion_operations)
    if ad_operations:
        client.get_service("AdGroupAdService").mutate_ad_group_ads(customer_id=cid, operations=ad_operations)
    if group_operations:
        client.get_service("AdGroupService").mutate_ad_groups(customer_id=cid, operations=group_operations)
    if campaign_operations:
        client.get_service("CampaignService").mutate_campaigns(customer_id=cid, operations=campaign_operations)
    print(f"Включено: кампании={len(campaign_operations)}, группы={len(group_operations)}, RSA={len(ad_operations)}, ключи={len(criterion_operations)}.")


if __name__ == "__main__":
    main()
