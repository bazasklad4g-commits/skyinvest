#!/usr/bin/env python
"""Отчёт GA4 по ресурсу nezaleznist. Аргумент — число дней, по умолчанию 30."""
import os
import sys

from google.analytics.data import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    OrderBy,
    RunReportRequest,
)
from google.oauth2 import service_account

KEY = os.environ.get("GOOGLE_SA_KEY", ".secrets/gstar-sa.json")
PROPERTY = os.environ.get("GA4_PROPERTY", "properties/547441168")
DAYS = sys.argv[1] if len(sys.argv) > 1 else "30"

client = BetaAnalyticsDataClient(
    credentials=service_account.Credentials.from_service_account_file(
        KEY, scopes=["https://www.googleapis.com/auth/analytics.readonly"]
    )
)


def report(title, dimensions, metrics, limit=15, order_metric=None):
    request = RunReportRequest(
        property=PROPERTY,
        date_ranges=[DateRange(start_date=f"{DAYS}daysAgo", end_date="today")],
        dimensions=[Dimension(name=d) for d in dimensions],
        metrics=[Metric(name=m) for m in metrics],
        limit=limit,
    )
    if order_metric:
        request.order_bys = [
            OrderBy(metric=OrderBy.MetricOrderBy(metric_name=order_metric), desc=True)
        ]
    response = client.run_report(request)
    print(f"\n=== {title} ===")
    if not response.rows:
        print("нет данных")
        return
    header = " | ".join(dimensions + metrics)
    print(header)
    print("-" * len(header))
    for row in response.rows:
        cells = [d.value for d in row.dimension_values] + [m.value for m in row.metric_values]
        print(" | ".join(cells))


print(f"Ресурс {PROPERTY}, период: последние {DAYS} дней")
report("Итого", [], ["sessions", "totalUsers", "screenPageViews", "keyEvents"])
report("Источники", ["sessionSource", "sessionMedium"], ["sessions", "keyEvents"], order_metric="sessions")
report("Кампании", ["sessionCampaignName"], ["sessions", "keyEvents"], order_metric="sessions")
report("Посадочные", ["landingPage"], ["sessions", "bounceRate"], order_metric="sessions")
report("События", ["eventName"], ["eventCount"], limit=30, order_metric="eventCount")
report("По дням", ["date"], ["sessions", "totalUsers"], limit=40)
