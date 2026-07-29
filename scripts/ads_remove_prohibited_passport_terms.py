#!/usr/bin/env python3
"""Remove legacy Ads content containing the prohibited word 'паспорт'."""
import argparse
import pathlib

from google.ads.googleads.client import GoogleAdsClient

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONFIG = ROOT / ".secrets" / "google-ads.yaml"
TERM = "паспорт"


def customer_id():
    for line in CONFIG.read_text(encoding="utf-8").splitlines():
        if line.startswith("# Рабочий аккаунт:"):
            return line.split(":", 1)[1].strip()
    raise RuntimeError("Не найден рабочий аккаунт.")


def has_term(values):
    return any(TERM in value.lower() for value in values)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    client = GoogleAdsClient.load_from_storage(str(CONFIG))
    cid = customer_id()
    service = client.get_service("GoogleAdsService")

    ads = []
    ad_rows = service.search(customer_id=cid, query="""
        SELECT campaign.name, campaign.status, ad_group_ad.resource_name,
               ad_group_ad.ad.responsive_search_ad.headlines,
               ad_group_ad.ad.responsive_search_ad.descriptions
        FROM ad_group_ad
        WHERE campaign.status != 'REMOVED'
          AND ad_group_ad.ad.type = 'RESPONSIVE_SEARCH_AD'
    """)
    for row in ad_rows:
        text = [asset.text for asset in row.ad_group_ad.ad.responsive_search_ad.headlines]
        text += [asset.text for asset in row.ad_group_ad.ad.responsive_search_ad.descriptions]
        if has_term(text):
            ads.append((row.campaign.name, row.ad_group_ad.resource_name))

    keywords = []
    keyword_rows = service.search(customer_id=cid, query="""
        SELECT campaign.name, campaign.status, ad_group_criterion.resource_name,
               ad_group_criterion.keyword.text
        FROM keyword_view
        WHERE ad_group_criterion.keyword.text LIKE '%паспорт%'
    """)
    for row in keyword_rows:
        keywords.append((row.campaign.name, row.ad_group_criterion.resource_name, row.ad_group_criterion.keyword.text))

    print(f"RSA к удалению: {len(ads)}")
    for campaign, resource_name in ads:
        print(f"  {campaign} | {resource_name}")
    print(f"Ключи к удалению: {len(keywords)}")
    for campaign, resource_name, keyword in keywords:
        print(f"  {campaign} | {keyword} | {resource_name}")
    if not args.apply:
        print("Предпросмотр: ничего не удалено.")
        return

    ad_operations = []
    for _, resource_name in ads:
        operation = client.get_type("AdGroupAdOperation")
        operation.remove = resource_name
        ad_operations.append(operation)
    keyword_operations = []
    for _, resource_name, _ in keywords:
        operation = client.get_type("AdGroupCriterionOperation")
        operation.remove = resource_name
        keyword_operations.append(operation)
    if ad_operations:
        client.get_service("AdGroupAdService").mutate_ad_group_ads(customer_id=cid, operations=ad_operations)
    if keyword_operations:
        client.get_service("AdGroupCriterionService").mutate_ad_group_criteria(customer_id=cid, operations=keyword_operations)
    print("Все найденные RSA и ключи с запрещённым словом удалены.")


if __name__ == "__main__":
    main()
