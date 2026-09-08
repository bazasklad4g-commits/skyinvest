#!/usr/bin/env python
"""Инвентаризация GA4-ресурса и GTM-контейнера SkyInvest."""
import os

from google.analytics.admin import AnalyticsAdminServiceClient
from google.oauth2 import service_account
from googleapiclient.discovery import build

KEY = os.environ.get("GOOGLE_SA_KEY", ".secrets/gstar-sa.json")
PROPERTY = os.environ.get("GA4_PROPERTY", "properties/547441168")


def creds(scopes):
    return service_account.Credentials.from_service_account_file(KEY, scopes=scopes)


def ga4():
    client = AnalyticsAdminServiceClient(
        credentials=creds(["https://www.googleapis.com/auth/analytics.readonly"])
    )
    prop = client.get_property(name=PROPERTY)
    print(f"Ресурс: {prop.display_name} ({prop.name})")
    print(f"  часовой пояс: {prop.time_zone}, валюта: {prop.currency_code}")
    print(f"  создан: {prop.create_time.date()}")

    print("\nПотоки данных:")
    for stream in client.list_data_streams(parent=PROPERTY):
        web = stream.web_stream_data
        print(f"  {stream.display_name}: {web.measurement_id} — {web.default_uri}")

    print("\nСобытия-конверсии:")
    events = list(client.list_key_events(parent=PROPERTY))
    if not events:
        print("  нет ни одного")
    for event in events:
        print(f"  {event.event_name} (создано {event.create_time.date()})")

    print("\nСвязь с Google Ads:")
    links = list(client.list_google_ads_links(parent=PROPERTY))
    if not links:
        print("  связи нет")
    for link in links:
        print(f"  customer {link.customer_id}, персонализация: {link.ads_personalization_enabled}")


def gtm():
    service = build(
        "tagmanager",
        "v2",
        credentials=creds(["https://www.googleapis.com/auth/tagmanager.readonly"]),
        cache_discovery=False,
    )
    path = "accounts/6322262103/containers/234272618"
    workspaces = (
        service.accounts().containers().workspaces().list(parent=path).execute().get("workspace", [])
    )
    print("\nGTM рабочие пространства:")
    for workspace in workspaces:
        print(f"  {workspace['name']} ({workspace['path']})")

    versions = (
        service.accounts()
        .containers()
        .version_headers()
        .list(parent=path)
        .execute()
        .get("containerVersionHeader", [])
    )
    print("\nОпубликованные версии:")
    for version in versions[:5]:
        live = " ← live" if version.get("numTags") and version.get("containerVersionId") == "1" else ""
        print(f"  v{version['containerVersionId']}: {version.get('name', 'без имени')} "
              f"тегов {version.get('numTags', 0)}, триггеров {version.get('numTriggers', 0)}{live}")

    if workspaces:
        tags = (
            service.accounts()
            .containers()
            .workspaces()
            .tags()
            .list(parent=workspaces[0]["path"])
            .execute()
            .get("tag", [])
        )
        print(f"\nТеги в «{workspaces[0]['name']}»:")
        if not tags:
            print("  нет тегов")
        for tag in tags:
            print(f"  {tag['name']} [{tag['type']}] статус: {tag.get('paused') and 'на паузе' or 'активен'}")


if __name__ == "__main__":
    ga4()
    gtm()
