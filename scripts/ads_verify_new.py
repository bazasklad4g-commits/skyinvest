import os
from google.ads.googleads.client import GoogleAdsClient
from google.oauth2 import service_account
client = GoogleAdsClient(
    credentials=service_account.Credentials.from_service_account_file(
        ".secrets/gstar-sa.json", scopes=["https://www.googleapis.com/auth/adwords"]),
    developer_token="t8wOf5cvS7HV5V7gjHnH2w", login_customer_id="8522851042",
    version="v22", use_proto_plus=True)
ga = client.get_service("GoogleAdsService")
IDS = ["24185846360", "24185846588"]
for cid_ in IDS:
    for row in ga.search(customer_id="3432200766", query=f"""
        SELECT campaign.id, campaign.name, campaign.status, campaign.serving_status,
               campaign.primary_status, campaign.bidding_strategy_type,
               campaign.advertising_channel_type, campaign_budget.amount_micros
        FROM campaign WHERE campaign.id = {cid_}"""):
        c = row.campaign
        print(f"\n=== {c.name} (id={c.id}) ===")
        print(f"  статус {c.status.name}, показ {c.serving_status.name}, "
              f"состояние {c.primary_status.name}")
        print(f"  {c.advertising_channel_type.name}, {c.bidding_strategy_type.name}, "
              f"бюджет ${row.campaign_budget.amount_micros/1_000_000:.0f}/день")
    groups = {}
    for row in ga.search(customer_id="3432200766", query=f"""
        SELECT ad_group.name, ad_group.status FROM ad_group
        WHERE campaign.id = {cid_}"""):
        groups[row.ad_group.name] = row.ad_group.status.name
    print(f"  группы: " + ", ".join(f"{n} [{s}]" for n, s in groups.items()))
    ads = kws = 0
    urls = set()
    for row in ga.search(customer_id="3432200766", query=f"""
        SELECT ad_group_ad.ad.id, ad_group_ad.status, ad_group_ad.ad.final_urls,
               ad_group_ad.policy_summary.approval_status,
               ad_group_ad.policy_summary.review_status
        FROM ad_group_ad WHERE campaign.id = {cid_}"""):
        ads += 1
        urls.update(row.ad_group_ad.ad.final_urls)
        approval = row.ad_group_ad.policy_summary.approval_status.name
        review = row.ad_group_ad.policy_summary.review_status.name
    print(f"  объявлений {ads}, модерация: {approval} / {review}")
    print(f"  URL: {', '.join(urls)}")
    for row in ga.search(customer_id="3432200766", query=f"""
        SELECT ad_group_criterion.keyword.text FROM keyword_view
        WHERE campaign.id = {cid_}"""):
        kws += 1
    negs = 0
    for row in ga.search(customer_id="3432200766", query=f"""
        SELECT campaign_criterion.keyword.text, campaign_criterion.negative
        FROM campaign_criterion WHERE campaign.id = {cid_}"""):
        if row.campaign_criterion.negative:
            negs += 1
    print(f"  ключей {kws}, минус-слов на уровне кампании {negs}")
