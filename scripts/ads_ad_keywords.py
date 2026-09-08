# -*- coding: utf-8 -*-
"""For every ad in every ENABLED campaign: the ad text, the keywords of its ad
group, and the URL the traffic goes to.

Keywords are set on the ad group, not on the ad, so every ad in a group is shown
against that group's keyword list. Grouped by campaign id -- five campaign names
in this account are shared by more than one campaign.
"""
import collections
import io

from google.ads.googleads.client import GoogleAdsClient

CUSTOMER_ID = "3432200766"
OUT = "data/ads/ADS-WITH-KEYWORDS.md"
TSV = "data/ads/ads-with-keywords.tsv"
KW_SHOWN = 60

ADS = """
SELECT campaign.id, campaign.name, ad_group.id, ad_group.name, ad_group.status,
       ad_group_ad.ad.id, ad_group_ad.status, ad_group_ad.ad_strength,
       ad_group_ad.policy_summary.approval_status,
       ad_group_ad.ad.final_urls,
       ad_group_ad.ad.responsive_search_ad.headlines,
       ad_group_ad.ad.responsive_search_ad.descriptions
FROM ad_group_ad
WHERE campaign.status = 'ENABLED' AND ad_group_ad.status != 'REMOVED'
"""
KWS = """
SELECT campaign.id, ad_group.id,
       ad_group_criterion.keyword.text,
       ad_group_criterion.keyword.match_type,
       ad_group_criterion.status,
       ad_group_criterion.negative
FROM keyword_view
WHERE campaign.status = 'ENABLED'
"""
MATCH = {"EXACT": "точн", "PHRASE": "фраз", "BROAD": "широк"}
STRENGTH = {"EXCELLENT": "отличное", "GOOD": "хорошее", "AVERAGE": "среднее",
            "POOR": "низкое", "PENDING": "считается", "UNSPECIFIED": "нет данных"}
APPROVAL = {"APPROVED": "одобрено", "DISAPPROVED": "ОТКЛОНЕНО", "UNKNOWN": "на проверке",
            "APPROVED_LIMITED": "одобрено с ограничениями"}


def main():
    client = GoogleAdsClient.load_from_storage(".secrets/google-ads.yaml", version="v22")
    svc = client.get_service("GoogleAdsService")

    kws = collections.defaultdict(list)
    for batch in svc.search_stream(customer_id=CUSTOMER_ID, query=KWS):
        for r in batch.results:
            c = r.ad_group_criterion
            if c.negative or c.status.name == "REMOVED":
                continue
            kws[str(r.ad_group.id)].append((c.keyword.text, MATCH.get(c.keyword.match_type.name, "?"),
                                            c.status.name))

    ads = collections.defaultdict(list)
    camp_name = {}
    for batch in svc.search_stream(customer_id=CUSTOMER_ID, query=ADS):
        for r in batch.results:
            cid = str(r.campaign.id)
            camp_name[cid] = r.campaign.name
            ads[(cid, str(r.ad_group.id), r.ad_group.name)].append({
                "ad_id": r.ad_group_ad.ad.id,
                "status": r.ad_group_ad.status.name,
                "strength": STRENGTH.get(r.ad_group_ad.ad_strength.name, r.ad_group_ad.ad_strength.name),
                "approval": APPROVAL.get(r.ad_group_ad.policy_summary.approval_status.name,
                                         r.ad_group_ad.policy_summary.approval_status.name),
                "urls": list(r.ad_group_ad.ad.final_urls),
                "heads": [a.text for a in r.ad_group_ad.ad.responsive_search_ad.headlines],
                "descs": [a.text for a in r.ad_group_ad.ad.responsive_search_ad.descriptions],
            })

    by_camp = collections.defaultdict(list)
    for (cid, agid, agname), items in ads.items():
        by_camp[cid].append((agid, agname, items))

    out = ["# Объявления включённых кампаний и ключи, по которым они показываются\n"]
    out.append("Ключи задаются на группе, поэтому все объявления одной группы показываются "
               "по одному и тому же списку. Показано до %d активных ключей на группу, "
               "полный список — в `ads-with-keywords.tsv`.\n" % KW_SHOWN)

    order = sorted(by_camp, key=lambda c: -sum(len(kws.get(a, [])) for a, _, _ in by_camp[c]))
    for cid in order:
        out.append("## %s\n" % camp_name[cid])
        out.append("ID кампании %s\n" % cid)
        for agid, agname, items in sorted(by_camp[cid], key=lambda t: t[1]):
            rows = kws.get(agid, [])
            active = [k for k in rows if k[2] == "ENABLED"]
            out.append("### Группа: %s\n" % agname)
            urls = sorted({u for it in items for u in it["urls"]})
            out.append("**Трафик идёт на:** %s\n" % (", ".join(urls) or "адреса нет"))
            out.append("**Ключей активных: %d** (всего в группе %d)\n" % (len(active), len(rows)))
            if active:
                shown = active[:KW_SHOWN]
                out.append("`" + "` · `".join("%s [%s]" % (t, m) for t, m, _ in shown) + "`")
                if len(active) > KW_SHOWN:
                    out.append("\n*…и ещё %d активных ключей*" % (len(active) - KW_SHOWN))
                out.append("")
            out.append("**Объявления в этой группе (%d):**\n" % len(items))
            for it in items:
                out.append("- `%s` — %s, модерация: %s" % (it["ad_id"], it["strength"], it["approval"]))
                out.append("  - Заголовки: %s" % (" · ".join(it["heads"]) or "—"))
                out.append("  - Описания: %s" % (" · ".join(it["descs"]) or "—"))
            out.append("")
    io.open(OUT, "w", encoding="utf-8").write("\n".join(out) + "\n")

    with io.open(TSV, "w", encoding="utf-8") as fh:
        fh.write("campaign_id\tcampaign\tad_group\tad_id\tkeyword\tmatch\tkw_status\turl\n")
        for (cid, agid, agname), items in ads.items():
            url = items[0]["urls"][0] if items[0]["urls"] else ""
            for it in items:
                for t, m, st in kws.get(agid, []):
                    fh.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (
                        cid, camp_name[cid], agname, it["ad_id"], t, m, st, url))
    print("campaigns", len(by_camp), "| ad groups", len(ads),
          "| ads", sum(len(v) for v in ads.values()))


if __name__ == "__main__":
    main()
