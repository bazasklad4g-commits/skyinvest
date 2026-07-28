#!/usr/bin/env python3
"""Безопасное управление кампаниями Google Ads.

По умолчанию все команды работают в режиме предпросмотра. Любая мутация
выполняется только с явным флагом --apply.

Примеры:
  .venv/bin/python scripts/ads_manage.py list
  .venv/bin/python scripts/ads_manage.py status --campaign-id 123 --set PAUSED
  .venv/bin/python scripts/ads_manage.py status --campaign-id 123 --set PAUSED --apply
  .venv/bin/python scripts/ads_manage.py budget --budget-id 456 --daily 75 --apply
"""
import argparse
import pathlib
import sys

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONFIG = ROOT / ".secrets" / "google-ads.yaml"
MICROS = 1_000_000


def customer_id():
    for line in CONFIG.read_text(encoding="utf-8").splitlines():
        if line.startswith("# Рабочий аккаунт:"):
            return line.split(":", 1)[1].strip()
    raise RuntimeError("В google-ads.yaml нет комментария '# Рабочий аккаунт: <ID>'.")


def require_apply(args, summary):
    if args.apply:
        return
    print(f"Предпросмотр: {summary}")
    print("Изменение не отправлено. Добавьте --apply после проверки ID.")
    sys.exit(0)


def list_campaigns(client, cid):
    query = """
        SELECT campaign.id, campaign.name, campaign.status,
               campaign_budget.id, campaign_budget.amount_micros
        FROM campaign
        WHERE campaign.status != 'REMOVED'
        ORDER BY campaign.name
    """
    service = client.get_service("GoogleAdsService")
    print("campaign_id | budget_id | status | daily_budget | name")
    for row in service.search(customer_id=cid, query=query):
        print(
            f"{row.campaign.id} | {row.campaign_budget.id} | "
            f"{row.campaign.status.name} | "
            f"{row.campaign_budget.amount_micros / MICROS:.2f} | {row.campaign.name}"
        )


def change_status(client, cid, campaign_id, status, args):
    require_apply(args, f"кампания {campaign_id} → {status}")
    service = client.get_service("CampaignService")
    operation = client.get_type("CampaignOperation")
    campaign = operation.update
    campaign.resource_name = service.campaign_path(cid, campaign_id)
    campaign.status = client.enums.CampaignStatusEnum[status]
    operation.update_mask.paths.append("status")
    response = service.mutate_campaigns(customer_id=cid, operations=[operation])
    print(f"Готово: {response.results[0].resource_name} → {status}")


def change_budget(client, cid, budget_id, daily, args):
    if daily <= 0:
        raise ValueError("Дневной бюджет должен быть больше нуля.")
    require_apply(args, f"бюджет {budget_id} → {daily:.2f} в валюте аккаунта в день")
    service = client.get_service("CampaignBudgetService")
    operation = client.get_type("CampaignBudgetOperation")
    budget = operation.update
    budget.resource_name = service.campaign_budget_path(cid, budget_id)
    budget.amount_micros = round(daily * MICROS)
    operation.update_mask.paths.append("amount_micros")
    response = service.mutate_campaign_budgets(customer_id=cid, operations=[operation])
    print(f"Готово: {response.results[0].resource_name} → {daily:.2f} в день")


def parse_args():
    parser = argparse.ArgumentParser(description="Управление Google Ads с обязательным --apply")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("list", help="Показать доступные кампании и бюджеты")

    status = subparsers.add_parser("status", help="Запустить или поставить кампанию на паузу")
    status.add_argument("--campaign-id", required=True, type=int)
    status.add_argument("--set", required=True, choices=("ENABLED", "PAUSED"))
    status.add_argument("--apply", action="store_true", help="Подтвердить изменение")

    budget = subparsers.add_parser("budget", help="Изменить дневной бюджет кампании")
    budget.add_argument("--budget-id", required=True, type=int)
    budget.add_argument("--daily", required=True, type=float, help="Сумма в валюте аккаунта")
    budget.add_argument("--apply", action="store_true", help="Подтвердить изменение")
    return parser.parse_args()


def main():
    args = parse_args()
    if not CONFIG.exists():
        raise RuntimeError(f"Нет конфигурации {CONFIG}.")
    client = GoogleAdsClient.load_from_storage(str(CONFIG))
    cid = customer_id()
    if args.command == "list":
        list_campaigns(client, cid)
    elif args.command == "status":
        change_status(client, cid, args.campaign_id, args.set, args)
    elif args.command == "budget":
        change_budget(client, cid, args.budget_id, args.daily, args)


if __name__ == "__main__":
    try:
        main()
    except (GoogleAdsException, RuntimeError, ValueError) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        sys.exit(1)
