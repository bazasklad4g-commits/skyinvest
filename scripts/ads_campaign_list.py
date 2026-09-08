# -*- coding: utf-8 -*-
"""Authoritative campaign list: id, name, status, channel."""
import io
import json

from google.ads.googleads.client import GoogleAdsClient

Q = """
SELECT campaign.id, campaign.name, campaign.status,
       campaign.advertising_channel_type, campaign.start_date, campaign.end_date
FROM campaign
"""


def main():
    client = GoogleAdsClient.load_from_storage(".secrets/google-ads.yaml", version="v22")
    svc = client.get_service("GoogleAdsService")
    rows = []
    for batch in svc.search_stream(customer_id="3432200766", query=Q):
        for r in batch.results:
            rows.append({
                "id": str(r.campaign.id),
                "name": r.campaign.name,
                "status": r.campaign.status.name,
                "channel": r.campaign.advertising_channel_type.name,
                "start": r.campaign.start_date,
                "end": r.campaign.end_date,
            })
    io.open("data/ads/campaigns.json", "w", encoding="utf-8").write(
        json.dumps(rows, ensure_ascii=False, indent=1))
    from collections import Counter
    print("campaigns:", len(rows), Counter(r["status"] for r in rows))
    dupes = Counter(r["name"] for r in rows)
    print("names used more than once:", sum(1 for n, c in dupes.items() if c > 1))


if __name__ == "__main__":
    main()
