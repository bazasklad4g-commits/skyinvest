# -*- coding: utf-8 -*-
"""Every ENABLED campaign, keyed by campaign id: keywords and the URL traffic goes to.

Five campaign names in this account are used by more than one campaign, so
everything here is grouped by campaign.id, never by name.
"""
import collections
import io
import json

from google.ads.googleads.client import GoogleAdsClient

CUSTOMER_ID = "3432200766"
OUT = "data/ads/ENABLED-CAMPAIGNS.md"
KW_CAP = 40  # a couple of campaigns carry tens of thousands of keywords

KEYWORDS = """
SELECT campaign.id, ad_group.name, ad_group.status,
       ad_group_criterion.keyword.text,
       ad_group_criterion.keyword.match_type,
       ad_group_criterion.status,
       ad_group_criterion.negative
FROM keyword_view
WHERE campaign.status = 'ENABLED'
"""
MATCH = {"EXACT": "точн", "PHRASE": "фраз", "BROAD": "широк"}


def main():
    client = GoogleAdsClient.load_from_storage(".secrets/google-ads.yaml", version="v22")
    svc = client.get_service("GoogleAdsService")

    camps = {c["id"]: c for c in json.load(io.open("data/ads/campaigns.json", encoding="utf-8"))}
    kws = collections.defaultdict(list)
    negs = collections.defaultdict(set)
    for batch in svc.search_stream(customer_id=CUSTOMER_ID, query=KEYWORDS):
        for r in batch.results:
            c = r.ad_group_criterion
            if c.status.name == "REMOVED" or r.ad_group.status.name == "REMOVED":
                continue
            cid = str(r.campaign.id)
            if c.negative:
                negs[cid].add(c.keyword.text)
            else:
                kws[cid].append((c.keyword.text, MATCH.get(c.keyword.match_type.name, "?"), c.status.name))

    ads = [r for r in json.load(io.open("data/ads/ads-report.json", encoding="utf-8"))
           if r["ad_status"] != "REMOVED"]
    urls = collections.defaultdict(collections.Counter)
    adcount = collections.Counter()
    for r in ads:
        urls[r["campaign_id"]][r["urls"][0] if r["urls"] else ""] += 1
        adcount[r["campaign_id"]] += 1

    enabled = sorted((c for c in camps.values() if c["status"] == "ENABLED"),
                     key=lambda c: -len(kws.get(c["id"], [])))

    out = ["# Включённые кампании: ключи и куда идёт трафик\n"]
    out.append("В аккаунте 139 кампаний: **включено 46**, на паузе 83, удалено 10.\n")
    out.append("Слово «[PAUSED]» в названии — просто текст, к статусу отношения не имеет. "
               "Всё сгруппировано по ID кампании, потому что пять названий в аккаунте повторяются.\n")

    out.append("## Сводка\n")
    out.append("| ID | Кампания | Ключей | Объявл. | Полный URL |")
    out.append("|---|---|---:|---:|---|")
    for c in enabled:
        cid = c["id"]
        u = urls.get(cid, collections.Counter())
        url_cell = "<br>".join(x or "*адреса нет*" for x, _ in u.most_common(3)) or "*объявлений нет*"
        out.append("| %s | %s | %d | %d | %s |" % (
            cid, c["name"].replace("|", "/"), len(kws.get(cid, [])), adcount.get(cid, 0), url_cell))
    out.append("")

    out.append("---\n\n## По каждой кампании\n")
    for c in enabled:
        cid = c["id"]
        out.append("### %s\n" % c["name"])
        out.append("- **ID:** %s · **тип:** %s · **старт:** %s" % (cid, c["channel"], c["start"]))
        u = urls.get(cid, collections.Counter())
        if u:
            for url, n in u.most_common():
                out.append("- **Трафик идёт на:** %s — объявлений %d" % (url or "*адреса нет*", n))
        else:
            out.append("- **Объявлений нет** — показываться нечему")
        rows = kws.get(cid, [])
        if not rows:
            out.append("- **Ключей нет**\n")
            continue
        paused_kw = sum(1 for _, _, st in rows if st == "PAUSED")
        out.append("- **Ключей: %d** (из них на паузе %d)" % (len(rows), paused_kw))
        shown = rows[:KW_CAP]
        out.append("")
        out.append("  " + "; ".join("%s [%s]" % (t, m) for t, m, _ in shown))
        if len(rows) > KW_CAP:
            out.append("")
            out.append("  *…и ещё %d ключей* — полный список в `data/ads/keywords-enabled.tsv`" % (len(rows) - KW_CAP))
        if negs.get(cid):
            out.append("")
            out.append("- **Минус-слов: %d**" % len(negs[cid]))
        out.append("")

    io.open(OUT, "w", encoding="utf-8").write("\n".join(out) + "\n")

    with io.open("data/ads/keywords-enabled.tsv", "w", encoding="utf-8") as fh:
        fh.write("campaign_id\tcampaign\tkeyword\tmatch\tstatus\n")
        for c in enabled:
            for t, m, st in kws.get(c["id"], []):
                fh.write("%s\t%s\t%s\t%s\t%s\n" % (c["id"], c["name"], t, m, st))
    print("enabled campaigns:", len(enabled), "| keywords:", sum(len(v) for v in kws.values()))


if __name__ == "__main__":
    main()
