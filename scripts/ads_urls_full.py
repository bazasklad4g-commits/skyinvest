# -*- coding: utf-8 -*-
"""Every campaign with its full final URLs, the page title behind each and the HTTP code."""
import collections
import io
import json
import re
import urllib.error
import urllib.request

RAW = "data/ads/ads-report.json"
OUT = "data/ads/CAMPAIGN-URLS.md"
GRANT = "nezalezhnist.org.ua"
STATUS_RU = {"ENABLED": "ВКЛЮЧЕНА", "PAUSED": "на паузе", "REMOVED": "удалена"}


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            body = r.read(120000).decode("utf-8", "replace")
            m = re.search(r"<title[^>]*>(.*?)</title>", body, re.S | re.I)
            title = re.sub(r"\s+", " ", m.group(1)).strip() if m else ""
            return r.status, title
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception:
        return 0, ""


def main():
    rows = [r for r in json.load(io.open(RAW, encoding="utf-8")) if r["ad_status"] != "REMOVED"]
    urls = sorted({u for r in rows for u in r["urls"]})
    info = {u: fetch(u) for u in urls}

    camps = collections.OrderedDict()
    for r in rows:
        camps.setdefault((r["campaign"], r["campaign_status"]), collections.Counter())
        for u in r["urls"]:
            camps[(r["campaign"], r["campaign_status"])][u] += 1
        if not r["urls"]:
            camps[(r["campaign"], r["campaign_status"])][""] += 1

    order = {"ENABLED": 0, "PAUSED": 1, "REMOVED": 2}
    out = []
    out.append("# Все кампании: полный URL и что за страница\n")
    out.append("Кампаний %d, уникальных адресов %d. Код 200 — страница открывается; "
               "404 — её нет; 0 — домен не отвечает.\n" % (len(camps), len(urls)))
    out.append("| Кампания | Статус | Полный URL | Что это за страница | Код | Объявл. |")
    out.append("|---|---|---|---|---:|---:|")
    for (name, status), counter in sorted(camps.items(), key=lambda kv: (order.get(kv[0][1], 9), kv[0][0])):
        for url, n in counter.most_common():
            if not url:
                out.append("| %s | %s | — | у объявления нет адреса | — | %d |" % (
                    name.replace("|", "/"), STATUS_RU.get(status, status), n))
                continue
            code, title = info[url]
            note = title or ("страницы нет" if code == 404 else "домен не отвечает" if code == 0 else "")
            if GRANT not in url:
                note = "ЧУЖОЙ ДОМЕН. " + note
            out.append("| %s | %s | %s | %s | %s | %d |" % (
                name.replace("|", "/"), STATUS_RU.get(status, status), url,
                note.replace("|", "/"), code or "нет ответа", n))
    io.open(OUT, "w", encoding="utf-8").write("\n".join(out) + "\n")
    print("wrote", OUT, "| campaigns", len(camps), "| urls", len(urls))


if __name__ == "__main__":
    main()
