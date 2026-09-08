# -*- coding: utf-8 -*-
"""Which paused campaigns could actually be switched on today.

A campaign is ready only if it is paused (not removed, not already running),
every live ad points at a URL that answers 200, and no ad is disapproved.
"""
import collections
import io
import json
import urllib.error
import urllib.request

RAW = "data/ads/ads-report.json"
OUT = "data/ads/READY-TO-ENABLE.md"
GRANT = "nezalezhnist.org.ua"


def check(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception:
        return 0


def main():
    rows = [r for r in json.load(io.open(RAW, encoding="utf-8")) if r["ad_status"] != "REMOVED"]
    urls = sorted({u for r in rows for u in r["urls"]})
    code = {u: check(u) for u in urls}

    camps = collections.OrderedDict()
    for r in rows:
        camps.setdefault((r["campaign"], r["campaign_status"]), []).append(r)

    ready, url_broken, rejected, foreign_domain = [], [], [], []
    for (name, status), ads in camps.items():
        if status != "PAUSED":
            continue
        ad_urls = sorted({u for a in ads for u in a["urls"]})
        dead = [u for u in ad_urls if code.get(u) != 200]
        outside = [u for u in ad_urls if GRANT not in u]
        bad_ads = [a for a in ads if a["approval"] == "DISAPPROVED"]
        item = {
            "name": name, "ads": len(ads), "urls": ad_urls, "dead": dead,
            "outside": outside, "rejected": len(bad_ads),
            "ok_ads": len(ads) - len(bad_ads),
        }
        if outside:
            foreign_domain.append(item)
        elif dead:
            url_broken.append(item)
        elif bad_ads and len(bad_ads) == len(ads):
            rejected.append(item)
        else:
            ready.append(item)

    ready.sort(key=lambda i: -i["ads"])
    out = []
    out.append("# Какие кампании можно включить\n")
    out.append("Кампания попадает в «можно включить», только если она сейчас на паузе, "
               "все её адреса отвечают 200 и ни одно объявление не отклонено модерацией.\n")
    out.append("## Готовы к включению: %d\n" % len(ready))
    out.append("| # | Кампания | Объявл. | Отклонено | URL |")
    out.append("|---:|---|---:|---:|---|")
    for n, i in enumerate(ready, 1):
        u = "<br>".join(i["urls"][:4]) + ("<br>… ещё %d" % (len(i["urls"]) - 4) if len(i["urls"]) > 4 else "")
        out.append("| %d | %s | %d | %d | %s |" % (n, i["name"].replace("|", "/"), i["ads"], i["rejected"], u))
    out.append("")
    out.append("## Нельзя: ведут на чужой домен — %d\n" % len(foreign_domain))
    for i in foreign_domain:
        out.append("- **%s** — %d объявлений, адреса вне домена НКО: %s" % (
            i["name"].replace("|", "/"), i["ads"], ", ".join(i["outside"][:3]) + (" …" if len(i["outside"]) > 3 else "")))
    out.append("")
    out.append("## Нельзя: битые адреса — %d\n" % len(url_broken))
    for i in url_broken:
        out.append("- **%s** — %d объявлений, не отвечает: %s" % (
            i["name"].replace("|", "/"), i["ads"], ", ".join("%s (%s)" % (u, code[u] or "нет ответа") for u in i["dead"][:3])))
    out.append("")
    out.append("## Нельзя: все объявления отклонены — %d\n" % len(rejected))
    for i in rejected:
        out.append("- **%s** — %d объявлений, все отклонены, URL %s" % (
            i["name"].replace("|", "/"), i["ads"], ", ".join(i["urls"][:2])))
    io.open(OUT, "w", encoding="utf-8").write("\n".join(out) + "\n")
    print("ready=%d foreign=%d broken=%d rejected=%d" % (
        len(ready), len(foreign_domain), len(url_broken), len(rejected)))


if __name__ == "__main__":
    main()
