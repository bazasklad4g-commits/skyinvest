"""Every ad in the account: campaign, ad text, ad strength, approval and final URL.

Campaign names in this account carry a "[PAUSED]" prefix that does not match the
real status, so the actual campaign.status is reported alongside the name.
"""
import io
import json

from google.ads.googleads.client import GoogleAdsClient

CUSTOMER_ID = "3432200766"
OUT = "data/ads/ADS-REPORT.md"
RAW = "data/ads/ads-report.json"

QUERY = """
SELECT
  campaign.id,
  campaign.name,
  campaign.status,
  campaign.advertising_channel_type,
  ad_group.id,
  ad_group.name,
  ad_group.status,
  ad_group_ad.ad.id,
  ad_group_ad.status,
  ad_group_ad.ad_strength,
  ad_group_ad.ad.type,
  ad_group_ad.ad.final_urls,
  ad_group_ad.ad.responsive_search_ad.headlines,
  ad_group_ad.ad.responsive_search_ad.descriptions,
  ad_group_ad.ad.expanded_text_ad.headline_part1,
  ad_group_ad.ad.expanded_text_ad.headline_part2,
  ad_group_ad.ad.expanded_text_ad.description,
  ad_group_ad.policy_summary.approval_status,
  ad_group_ad.policy_summary.review_status
FROM ad_group_ad
ORDER BY campaign.name, ad_group.name
"""


def texts(assets):
    return [a.text for a in assets]


def main():
    client = GoogleAdsClient.load_from_storage(".secrets/google-ads.yaml", version="v22")
    service = client.get_service("GoogleAdsService")

    rows = []
    for batch in service.search_stream(customer_id=CUSTOMER_ID, query=QUERY):
        for r in batch.results:
            ad = r.ad_group_ad.ad
            if ad.type_.name == "RESPONSIVE_SEARCH_AD":
                heads = texts(ad.responsive_search_ad.headlines)
                descs = texts(ad.responsive_search_ad.descriptions)
            elif ad.type_.name == "EXPANDED_TEXT_AD":
                heads = [ad.expanded_text_ad.headline_part1, ad.expanded_text_ad.headline_part2]
                descs = [ad.expanded_text_ad.description]
            else:
                heads, descs = [], []
            rows.append({
                "campaign_id": str(r.campaign.id),
                "campaign": r.campaign.name,
                "campaign_status": r.campaign.status.name,
                "channel": r.campaign.advertising_channel_type.name,
                "ad_group": r.ad_group.name,
                "ad_group_status": r.ad_group.status.name,
                "ad_id": ad.id,
                "ad_status": r.ad_group_ad.status.name,
                "strength": r.ad_group_ad.ad_strength.name,
                "approval": r.ad_group_ad.policy_summary.approval_status.name,
                "review": r.ad_group_ad.policy_summary.review_status.name,
                "type": ad.type_.name,
                "urls": list(ad.final_urls),
                "heads": heads,
                "descs": descs,
            })

    io.open(RAW, "w", encoding="utf-8").write(json.dumps(rows, ensure_ascii=False, indent=1))
    print("wrote %d ads to %s" % (len(rows), RAW))


if __name__ == "__main__":
    main()
