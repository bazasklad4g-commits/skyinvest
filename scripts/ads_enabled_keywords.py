# -*- coding: utf-8 -*-
"""For every campaign that is actually running: its keywords and its final URLs."""
import collections
import io
import json

from google.ads.googleads.client import GoogleAdsClient

CUSTOMER_ID = "3432200766"
OUT = "data/ads/ENABLED-CAMPAIGNS.md"
RAW = "data/ads/ads-report.json"

KEYWORDS = """
SELECT
  campaign.name,
  campaign.status,
  ad_group.name,
  ad_group.status,
  ad_group_criterion.keyword.text,
  ad_group_criterion.keyword.match_type,
  ad_group_criterion.status,
  ad_group_criterion.negative
FROM keyword_view
WHERE campaign.status = 'ENABLED'
"""

MATCH = {"EXACT": "точное", "PHRASE": "фразовое", "BROAD": "широкое"}


def main():
    client = GoogleAdsClient.load_from_storage(".secrets/google-ads.yaml", version="v22")
    service = client.get_service("GoogleAdsService")

    kws = collections.defaultdict(list)
    negatives = collections.defaultdict(list)
    for batch in service.search_stream(customer_id=CUSTOMER_ID, query=KEYWORDS):
        for r in batch.results:
            c = r.ad_group_criterion
            if c.status.name == "REMOVED":
                continue
            entry = (r.ad_group.name, c.keyword.text, MATCH.get(c.keyword.match_type.name, c.keyword.match_type.name))
            if c.negative:
                negatives[r.campaign.name].append(entry)
            else:
                kws[r.campaign.name].append(entry)

    ads = [r for r in json.load(io.open(RAW, encoding="utf-8"))
           if r["campaign_status"] == "ENABLED" and r["ad_status"] != "REMOVED"]
    urls = collections.defaultdict(collections.Counter)
    for r in ads:
        for u in r["urls"]:
            urls[r["campaign"]][u] += 1

    names = sorted(set(list(kws) + list(urls)))
    out = ["# Включённые кампании: ключи и адреса\n"]
    out.append("Кампаний со статусом ENABLED: %d. Слово «[PAUSED]» в названии — просто текст.\n" % len(names))

    out.append("## Сводка\n")
    out.append("| Кампания | Ключей | Групп | Полный URL |")
    out.append("|---|---:|---:|---|")
    for name in names:
        groups = {g for g, _, _ in kws.get(name, [])}
        url = " · ".join(u for u, _ in urls.get(name, collections.Counter()).most_common(2)) or "—"
        out.append("| %s | %d | %d | %s |" % (name.replace("|", "/"), len(kws.get(name, [])), len(groups), url))
    out.append("")

    out.append("---\n\n## По каждой кампании\n")
    for name in names:
        out.append("### %s\n" % name)
        for u, n in urls.get(name, collections.Counter()).most_common():
            out.append("**Трафик идёт на:** %s  (объявлений: %d)\n" % (u, n))
        rows = kws.get(name, [])
        if not rows:
            out.append("Ключей нет.\n")
        else:
            by_group = collections.defaultdict(list)
            for g, text, m in rows:
                by_group[g].append((text, m))
            out.append("**Ключи (%d):**\n" % len(rows))
            for g in sorted(by_group):
                items = ", ".join("%s [%s]" % (t, m) for t, m in sorted(by_group[g]))
                out.append("- *%s* — %s" % (g, items))
            out.append("")
        neg = negatives.get(name, [])
        if neg:
            out.append("**Минус-слова (%d):** %s\n" % (len(neg), ", ".join(sorted({t for _, t, _ in neg}))))
    io.open(OUT, "w", encoding="utf-8").write("\n".join(out) + "\n")
    print("wrote", OUT, "| campaigns", len(names), "| keywords", sum(len(v) for v in kws.values()))


if __name__ == "__main__":
    main()
