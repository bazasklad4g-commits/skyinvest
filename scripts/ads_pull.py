#!/usr/bin/env python3
"""Выгрузка Google Ads. ТОЛЬКО ЧТЕНИЕ — ни одного мутирующего вызова.

Забирает за период:
  1. кампании: расход, клики, показы, конверсии, стратегия ставок, tCPA
  2. разбивку конверсий по действиям в разрезе кампаний
  3. поисковые запросы

Пишет CSV в data/ads/.

Запуск:  .venv/bin/python scripts/ads_pull.py [дней, по умолчанию 30]
"""
import csv
import datetime
import pathlib
import sys

import yaml
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONFIG = ROOT / ".secrets" / "google-ads.yaml"
OUT = ROOT / "data" / "ads"
OUT.mkdir(parents=True, exist_ok=True)

MICROS = 1_000_000


def customer_id():
    """Рабочий аккаунт берём из комментария в конфиге, иначе спрашиваем."""
    for line in CONFIG.read_text(encoding="utf-8").splitlines():
        if line.startswith("# Рабочий аккаунт:"):
            return line.split(":", 1)[1].strip()
    return input("ID рекламного аккаунта (только цифры): ").strip()


def run(client, cid, query):
    service = client.get_service("GoogleAdsService")
    return service.search(customer_id=cid, query=query)


def write(name, header, rows):
    path = OUT / name
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    print(f"  {path.relative_to(ROOT)}  —  {len(rows)} строк")
    return path


def main():
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    if not CONFIG.exists():
        sys.exit(f"Нет {CONFIG}. Сначала: .venv/bin/python scripts/ads_auth.py")

    end = datetime.date.today() - datetime.timedelta(days=1)
    start = end - datetime.timedelta(days=days - 1)
    period = f"segments.date BETWEEN '{start}' AND '{end}'"
    stamp = f"{start}_{end}"

    client = GoogleAdsClient.load_from_storage(str(CONFIG))
    cid = customer_id()
    print(f"Аккаунт {cid}, период {start} → {end}\n")

    # --- 1. Кампании ---
    q = f"""
        SELECT campaign.name, campaign.status, campaign.advertising_channel_type,
               campaign.bidding_strategy_type,
               campaign.target_cpa.target_cpa_micros,
               campaign.maximize_conversions.target_cpa_micros,
               campaign_budget.amount_micros,
               metrics.impressions, metrics.clicks, metrics.cost_micros,
               metrics.conversions, metrics.conversions_value
        FROM campaign
        WHERE {period} AND campaign.status != 'REMOVED'
    """
    rows = []
    for r in run(client, cid, q):
        tcpa = (r.campaign.target_cpa.target_cpa_micros
                or r.campaign.maximize_conversions.target_cpa_micros or 0)
        rows.append([
            r.campaign.name,
            r.campaign.status.name,
            r.campaign.advertising_channel_type.name,
            r.campaign.bidding_strategy_type.name,
            round(tcpa / MICROS, 2),
            round(r.campaign_budget.amount_micros / MICROS, 2),
            r.metrics.impressions,
            r.metrics.clicks,
            round(r.metrics.cost_micros / MICROS, 2),
            round(r.metrics.conversions, 2),
            round(r.metrics.conversions_value, 2),
        ])
    rows.sort(key=lambda x: -x[8])
    write(f"campaigns_{stamp}.csv",
          ["кампания", "статус", "тип", "стратегия", "tCPA", "бюджет_день",
           "показы", "клики", "расход", "конверсии", "ценность"], rows)

    # --- 2. Конверсии по действиям в разрезе кампаний ---
    q = f"""
        SELECT campaign.name, segments.conversion_action_name,
               segments.conversion_action_category,
               metrics.all_conversions, metrics.conversions
        FROM campaign
        WHERE {period} AND campaign.status != 'REMOVED'
    """
    rows = []
    for r in run(client, cid, q):
        rows.append([
            r.campaign.name,
            r.segments.conversion_action_name,
            r.segments.conversion_action_category.name,
            round(r.metrics.all_conversions, 2),
            round(r.metrics.conversions, 2),
        ])
    rows.sort(key=lambda x: -x[3])
    write(f"conversions_by_campaign_{stamp}.csv",
          ["кампания", "действие", "категория", "все_конверсии", "в_ставках"], rows)

    # --- 3. Справочник действий-конверсий ---
    q = """
        SELECT conversion_action.name, conversion_action.category,
               conversion_action.status, conversion_action.type,
               conversion_action.primary_for_goal,
               conversion_action.counting_type
        FROM conversion_action
    """
    rows = [[
        r.conversion_action.name,
        r.conversion_action.category.name,
        r.conversion_action.status.name,
        r.conversion_action.type_.name,
        "PRIMARY" if r.conversion_action.primary_for_goal else "SECONDARY",
        r.conversion_action.counting_type.name,
    ] for r in run(client, cid, q)]
    write("conversion_actions.csv",
          ["действие", "категория", "статус", "тип", "роль", "счёт"], rows)

    # --- 4. Поисковые запросы ---
    q = f"""
        SELECT campaign.name, search_term_view.search_term,
               metrics.impressions, metrics.clicks, metrics.cost_micros,
               metrics.conversions
        FROM search_term_view
        WHERE {period}
    """
    rows = []
    for r in run(client, cid, q):
        rows.append([
            r.campaign.name,
            r.search_term_view.search_term,
            r.metrics.impressions,
            r.metrics.clicks,
            round(r.metrics.cost_micros / MICROS, 2),
            round(r.metrics.conversions, 2),
        ])
    rows.sort(key=lambda x: -x[4])
    write(f"search_terms_{stamp}.csv",
          ["кампания", "запрос", "показы", "клики", "расход", "конверсии"], rows)

    print("\nГотово.")


if __name__ == "__main__":
    try:
        main()
    except GoogleAdsException as e:
        print(f"Ошибка API (запрос {e.request_id}):")
        for err in e.failure.errors:
            print(f"  {err.message}")
        sys.exit(1)
