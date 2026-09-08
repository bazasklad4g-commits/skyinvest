#!/usr/bin/env python
"""Проверка доступа service account к GA4 и GTM.

Печатает, что аккаунту уже видно, и объясняет отказы.
"""
import os
import sys

from google.oauth2 import service_account

KEY = os.environ.get("GOOGLE_SA_KEY", ".secrets/gstar-sa.json")


def creds(scopes):
    return service_account.Credentials.from_service_account_file(KEY, scopes=scopes)


def short(err):
    text = str(err)
    return text[:400].replace("\n", " ")


def check_ga4():
    print("=== GA4 Admin API ===")
    try:
        from google.analytics.admin import AnalyticsAdminServiceClient

        client = AnalyticsAdminServiceClient(
            credentials=creds(["https://www.googleapis.com/auth/analytics.readonly"])
        )
        found = list(client.list_account_summaries())
        if not found:
            print("Доступ есть, но аккаунтов не видно: service account не добавлен ни в один GA4-аккаунт.")
        for account in found:
            print(f"Аккаунт: {account.display_name} ({account.account})")
            for prop in account.property_summaries:
                print(f"  Ресурс: {prop.display_name} ({prop.property})")
    except Exception as err:  # noqa: BLE001
        print("Ошибка:", short(err))


def check_gtm():
    print("\n=== Tag Manager API ===")
    try:
        from googleapiclient.discovery import build

        service = build(
            "tagmanager",
            "v2",
            credentials=creds(["https://www.googleapis.com/auth/tagmanager.readonly"]),
            cache_discovery=False,
        )
        accounts = service.accounts().list().execute().get("account", [])
        if not accounts:
            print("Доступ есть, но аккаунтов не видно: service account не добавлен ни в один GTM-аккаунт.")
        for account in accounts:
            print(f"Аккаунт: {account['name']} ({account['path']})")
            containers = (
                service.accounts()
                .containers()
                .list(parent=account["path"])
                .execute()
                .get("container", [])
            )
            for container in containers:
                print(f"  Контейнер: {container['name']} {container.get('publicId')} ({container['path']})")
    except Exception as err:  # noqa: BLE001
        print("Ошибка:", short(err))


if __name__ == "__main__":
    if not os.path.exists(KEY):
        sys.exit(f"Нет ключа: {KEY}")
    info = service_account.Credentials.from_service_account_file(KEY).service_account_email
    print(f"Service account: {info}\n")
    check_ga4()
    check_gtm()
