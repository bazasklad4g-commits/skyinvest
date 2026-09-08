#!/usr/bin/env python
"""Триггеры и переменные рабочего пространства GTM."""
import json
import os

from google.oauth2 import service_account
from googleapiclient.discovery import build

KEY = os.environ.get("GOOGLE_SA_KEY", ".secrets/gstar-sa.json")
WORKSPACE = "accounts/6322262103/containers/234272618/workspaces/9"

service = build(
    "tagmanager",
    "v2",
    credentials=service_account.Credentials.from_service_account_file(
        KEY, scopes=["https://www.googleapis.com/auth/tagmanager.readonly"]
    ),
    cache_discovery=False,
)
ws = service.accounts().containers().workspaces()

print("=== Триггеры ===")
for trigger in ws.triggers().list(parent=WORKSPACE).execute().get("trigger", []):
    detail = ""
    for group in ("customEventFilter", "filter"):
        for condition in trigger.get(group, []):
            params = {p["key"]: p.get("value") for p in condition.get("parameter", [])}
            detail += f"  [{condition['type']}] {params.get('arg0')} = {params.get('arg1')}\n"
    print(f"{trigger['name']} [{trigger['type']}] id={trigger['triggerId']}")
    if detail:
        print(detail, end="")

print("\n=== Привязка тегов к триггерам ===")
for tag in ws.tags().list(parent=WORKSPACE).execute().get("tag", []):
    params = {p["key"]: p.get("value") for p in tag.get("parameter", [])}
    fires = ", ".join(tag.get("firingTriggerId", [])) or "нет"
    label = params.get("eventName") or params.get("conversionLabel") or params.get("tagId") or ""
    print(f"{tag['name']}: триггеры {fires} | {label}")
