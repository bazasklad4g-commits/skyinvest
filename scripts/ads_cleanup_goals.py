#!/usr/bin/env python3
"""Pause the known irrelevant campaign and demote engagement conversions.

Dry-run by default. Pass --apply to mutate Google Ads.
"""
import argparse
import pathlib
import sys

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException


ROOT = pathlib.Path(__file__).resolve().parent.parent
CONFIG = ROOT / ".secrets" / "google-ads.yaml"
CAMPAIGN_ID = "23285820476"
CAMPAIGN_NAME = "S | Warming Up | rabota ua"
SECONDARY_CONVERSIONS = {
    "6727665742": "Nezalezhnist 2  (web) click_tel",
    "6727665745": "Nezalezhnist 2  (web) click_tg",
    "6727665748": "Nezalezhnist 2  (web) click_viber",
    "7370253723": "Scroll_25",
}


def customer_id():
    for line in CONFIG.read_text(encoding="utf-8").splitlines():
        if line.startswith("# Рабочий аккаунт:"):
            return line.split(":", 1)[1].strip()
    raise RuntimeError("В конфиге не указан рабочий аккаунт")


def query_one(client, cid, query):
    rows = list(client.get_service("GoogleAdsService").search(
        customer_id=cid, query=query
    ))
    if len(rows) != 1:
        raise RuntimeError(f"Ожидалась одна строка, получено: {len(rows)}")
    return rows[0]


def verify_targets(client, cid):
    campaign = query_one(client, cid, f"""
        SELECT campaign.id, campaign.resource_name, campaign.name, campaign.status
        FROM campaign
        WHERE campaign.id = {CAMPAIGN_ID}
    """).campaign
    if campaign.name != CAMPAIGN_NAME:
        raise RuntimeError(
            f"Имя кампании не совпало: {campaign.name!r} != {CAMPAIGN_NAME!r}"
        )

    conversions = []
    for action_id, expected_name in SECONDARY_CONVERSIONS.items():
        action = query_one(client, cid, f"""
            SELECT conversion_action.id, conversion_action.resource_name,
                   conversion_action.name, conversion_action.status,
                   conversion_action.primary_for_goal
            FROM conversion_action
            WHERE conversion_action.id = {action_id}
        """).conversion_action
        if action.name != expected_name:
            raise RuntimeError(
                f"Имя конверсии не совпало: {action.name!r} != {expected_name!r}"
            )
        conversions.append(action)
    return campaign, conversions


def apply_changes(client, cid, campaign, conversions):
    campaign_operation = client.get_type("CampaignOperation")
    campaign_operation.update.resource_name = campaign.resource_name
    campaign_operation.update.status = client.enums.CampaignStatusEnum.PAUSED
    campaign_operation.update_mask.paths.append("status")
    client.get_service("CampaignService").mutate_campaigns(
        customer_id=cid, operations=[campaign_operation]
    )

    operations = []
    for action in conversions:
        if not action.primary_for_goal:
            continue
        operation = client.get_type("ConversionActionOperation")
        operation.update.resource_name = action.resource_name
        operation.update.primary_for_goal = False
        operation.update_mask.paths.append("primary_for_goal")
        operations.append(operation)
    if operations:
        client.get_service("ConversionActionService").mutate_conversion_actions(
            customer_id=cid, operations=operations
        )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    if not CONFIG.exists():
        sys.exit(f"Нет конфига {CONFIG}")
    client = GoogleAdsClient.load_from_storage(str(CONFIG))
    cid = customer_id()
    campaign, conversions = verify_targets(client, cid)

    print(f"Кампания: {campaign.name} — {campaign.status.name} -> PAUSED")
    for action in conversions:
        role = "PRIMARY" if action.primary_for_goal else "SECONDARY"
        print(f"Конверсия: {action.name} — {role} -> SECONDARY")

    if not args.apply:
        print("\nDry-run: изменения не внесены. Для записи добавьте --apply.")
        return

    apply_changes(client, cid, campaign, conversions)
    print("\nИзменения отправлены в Google Ads.")


if __name__ == "__main__":
    try:
        main()
    except GoogleAdsException as exc:
        print(f"Ошибка Google Ads API, request_id={exc.request_id}")
        for error in exc.failure.errors:
            print(f"  {error.message}")
        raise SystemExit(1)
