#!/usr/bin/env python
"""Все потоки данных во всех доступных ресурсах — ищем, кому принадлежит measurement ID."""
import os

from google.analytics.admin import AnalyticsAdminServiceClient
from google.oauth2 import service_account

client = AnalyticsAdminServiceClient(
    credentials=service_account.Credentials.from_service_account_file(
        os.environ.get("GOOGLE_SA_KEY", ".secrets/gstar-sa.json"),
        scopes=["https://www.googleapis.com/auth/analytics.readonly"],
    )
)

for account in client.list_account_summaries():
    for prop in account.property_summaries:
        for stream in client.list_data_streams(parent=prop.property):
            web = stream.web_stream_data
            if not web.measurement_id:
                continue
            print(f"{web.measurement_id}  {prop.display_name} ({prop.property})  {web.default_uri}")
