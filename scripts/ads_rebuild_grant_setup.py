#!/usr/bin/env python3
"""Pause irrelevant live campaigns and keep only submitted lead forms primary.

Dry-run by default. Pass --apply to send changes to Google Ads.
"""
import argparse
import pathlib
import sys

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException


ROOT = pathlib.Path(__file__).resolve().parent.parent
CONFIG = ROOT / ".secrets" / "google-ads.yaml"
CAMPAIGNS_TO_PAUSE = {
    23241759103: "Pmax | Nezalezhnist | Warming Up",
    23285792135: "S | Warming Up | work ua",
    23394129087: "Bali | PMax | Max Conversions",
    23412787594: "Dubai | PMax | Max Conversions",
    23403219042: "Spain | PMax | Max Conversions",
    23403234468: "Turkey | PMax | Max Conversions",
    23394096228: "Bali | Search | Max Conversions",
    23399019722: "Bali | Search | Max Conversions Propose",
    23412787597: "Dubai | Search | Max Conversions",
    23403219045: "Spain | Search | Max Conversions",
    23403234471: "Turkey | Search | Max Conversions",
}
CUSTOMER_GOALS = {
    ("DEFAULT", "WEBSITE"): False,
    ("PURCHASE", "WEBSITE"): False,
    ("PAGE_VIEW", "WEBSITE"): False,
    ("PHONE_CALL_LEAD", "WEBSITE"): False,
    ("PHONE_CALL_LEAD", "CALL_FROM_ADS"): False,
    ("SUBMIT_LEAD_FORM", "WEBSITE"): True,
    ("CONTACT", "WEBSITE"): False,
    ("CONTACT", "CALL_FROM_ADS"): False,
}


def customer_id():
    for line in CONFIG.read_text(encoding="utf-8").splitlines():
        if line.startswith("# Рабочий аккаунт:"):
            return line.split(":", 1)[1].strip()
    raise RuntimeError("В конфиге не указан рабочий аккаунт")


def load_targets(client, cid):
    campaign_rows = list(client.get_service("GoogleAdsService").search(
        customer_id=cid,
        query="""
            SELECT campaign.id, campaign.name, campaign.resource_name, campaign.status
            FROM campaign
            WHERE campaign.status != 'REMOVED'
        """,
    ))
    targets = []
    by_id = {row.campaign.id: row.campaign for row in campaign_rows}
    for campaign_id, expected_name in CAMPAIGNS_TO_PAUSE.items():
        campaign = by_id.get(campaign_id)
        if not campaign or campaign.name != expected_name:
            raise RuntimeError(f"Не найдена ожидаемая кампания {campaign_id}: {expected_name}")
        targets.append(campaign)

    goals = []
    goal_rows = client.get_service("GoogleAdsService").search(
        customer_id=cid,
        query="""
            SELECT customer_conversion_goal.resource_name,
                   customer_conversion_goal.category,
                   customer_conversion_goal.origin,
                   customer_conversion_goal.biddable
            FROM customer_conversion_goal
        """,
    )
    for row in goal_rows:
        goal = row.customer_conversion_goal
        desired = CUSTOMER_GOALS.get((goal.category.name, goal.origin.name))
        if desired is not None and goal.biddable != desired:
            goals.append((goal, desired))
    return targets, goals


def apply(client, cid, campaigns, goals):
    campaign_operations = []
    for campaign in campaigns:
        if campaign.status.name == "PAUSED":
            continue
        operation = client.get_type("CampaignOperation")
        operation.update.resource_name = campaign.resource_name
        operation.update.status = client.enums.CampaignStatusEnum.PAUSED
        operation.update_mask.paths.append("status")
        campaign_operations.append(operation)
    if campaign_operations:
        client.get_service("CampaignService").mutate_campaigns(
            customer_id=cid, operations=campaign_operations
        )

    goal_operations = []
    for goal, biddable in goals:
        operation = client.get_type("CustomerConversionGoalOperation")
        operation.update.resource_name = goal.resource_name
        operation.update.biddable = biddable
        operation.update_mask.paths.append("biddable")
        goal_operations.append(operation)
    if goal_operations:
        client.get_service("CustomerConversionGoalService").mutate_customer_conversion_goals(
            customer_id=cid, operations=goal_operations
        )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if not CONFIG.exists():
        raise RuntimeError(f"Нет конфига {CONFIG}")

    client = GoogleAdsClient.load_from_storage(str(CONFIG))
    cid = customer_id()
    campaigns, goals = load_targets(client, cid)
    for campaign in campaigns:
        print(f"Кампания: {campaign.name} — {campaign.status.name} -> PAUSED")
    for goal, biddable in goals:
        role = "PRIMARY" if biddable else "SECONDARY"
        print(f"Цель: {goal.category.name} / {goal.origin.name} -> {role}")
    if not args.apply:
        print("Dry-run: изменения не отправлены. Добавьте --apply.")
        return
    apply(client, cid, campaigns, goals)
    print("Изменения отправлены в Google Ads.")


if __name__ == "__main__":
    try:
        main()
    except (GoogleAdsException, RuntimeError) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        sys.exit(1)
