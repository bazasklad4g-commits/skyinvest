#!/usr/bin/env python
"""Что реально опубликовано в контейнере GTM (live-версия)."""
import os

from google.oauth2 import service_account
from googleapiclient.discovery import build

CONTAINER = "accounts/6322262103/containers/234272618"
service = build(
    "tagmanager",
    "v2",
    credentials=service_account.Credentials.from_service_account_file(
        os.environ.get("GOOGLE_SA_KEY", ".secrets/gstar-sa.json"),
        scopes=["https://www.googleapis.com/auth/tagmanager.readonly"],
    ),
    cache_discovery=False,
)

live = service.accounts().containers().versions().live(parent=CONTAINER).execute()
print(f"Live-версия: v{live.get('containerVersionId')} «{live.get('name', 'без имени')}»")

triggers = {t["triggerId"]: t for t in live.get("trigger", [])}
print("\n=== Триггеры live ===")
for trigger in triggers.values():
    print(f"id={trigger['triggerId']} {trigger['name']} [{trigger['type']}]")
    for group in ("customEventFilter", "filter", "autoEventFilter"):
        for condition in trigger.get(group, []):
            params = {p["key"]: p.get("value") for p in condition.get("parameter", [])}
            print(f"    [{condition['type']}] {params.get('arg0')} = {params.get('arg1')}")

print("\n=== Теги live ===")
for tag in live.get("tag", []):
    params = {p["key"]: p.get("value") for p in tag.get("parameter", [])}
    fires = [triggers.get(i, {}).get("name", i) for i in tag.get("firingTriggerId", [])]
    label = params.get("eventName") or params.get("tagId") or params.get("conversionLabel") or ""
    print(f"{tag['name']} [{tag['type']}] → {label}")
    print(f"    срабатывает: {', '.join(fires) or 'нет триггера'}")
    if params.get("measurementIdOverride"):
        print(f"    measurementIdOverride: {params['measurementIdOverride']}")
