# -*- coding: utf-8 -*-
"""Turn the ad dump into a readable report, and check every final URL is alive."""
import collections
import io
import json
import urllib.error
import urllib.request

RAW = "data/ads/ads-report.json"
OUT = "data/ads/ADS-REPORT.md"
GRANT_DOMAIN = "nezalezhnist.org.ua"

STRENGTH_RU = {
    "EXCELLENT": "отличное",
    "GOOD": "хорошее",
    "AVERAGE": "среднее",
    "POOR": "низкое",
    "PENDING": "ещё считается",
    "UNSPECIFIED": "нет данных",
    "UNKNOWN": "нет данных",
}
APPROVAL_RU = {
    "APPROVED": "одобрено",
    "APPROVED_LIMITED": "одобрено с ограничениями",
    "DISAPPROVED": "ОТКЛОНЕНО",
    "AREA_OF_INTEREST_ONLY": "показ ограничен",
    "UNKNOWN": "на проверке",
}
STATUS_RU = {"ENABLED": "ВКЛЮЧЕНА", "PAUSED": "на паузе", "REMOVED": "удалена"}


def cell(text):
    return (text or "").replace("|", "/").replace("\n", " ").strip()


def check(url):
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception:
        return 0


def main():
    rows = json.load(io.open(RAW, encoding="utf-8"))
    urls = sorted({u for r in rows for u in r["urls"]})
    codes = {u: check(u) for u in urls}

    camps = collections.OrderedDict()
    for r in rows:
        camps.setdefault((r["campaign"], r["campaign_status"]), []).append(r)

    def sort_key(item):
        (name, status), ads = item
        return (0 if status == "ENABLED" else 1, name)

    out = []
    out.append("# Кампании и объявления, аккаунт 343-220-0766\n")
    out.append("Снято через Google Ads API. Кампаний %d, объявлений %d.\n" % (len(camps), len(rows)))

    enabled = [(k, v) for k, v in camps.items() if k[1] == "ENABLED"]
    dead = sorted(u for u, c in codes.items() if c != 200)
    foreign = sorted({u for u in urls if GRANT_DOMAIN not in u})
    disapproved = [r for r in rows if r["approval"] == "DISAPPROVED"]

    out.append("## Что важно знать до таблицы\n")
    out.append("**%d кампаний реально ВКЛЮЧЕНЫ, хотя в названии стоит «[PAUSED]».** Название — это просто текст, "
               "статус в нём ничего не значит. Список ниже, в таблице они идут первыми.\n" % len(enabled))
    for (name, _), ads in sorted(enabled, key=lambda kv: kv[0][0]):
        out.append("- `%s` — %d объявлений" % (name, len(ads)))
    out.append("")
    out.append("**Отклонено модерацией: %d объявлений из %d.**\n" % (len(disapproved), len(rows)))
    out.append("**Битые адреса: %d из %d уникальных.** Объявление с таким URL показываться не будет:\n" % (len(dead), len(urls)))
    for u in dead:
        out.append("- `%s` → %s" % (u, codes[u] or "не отвечает"))
    out.append("")
    if foreign:
        out.append("**Адреса вне домена НКО: %d.** Ad Grants разрешает вести только на проверенный домен организации:\n" % len(foreign))
        for u in foreign:
            out.append("- `%s`" % u)
        out.append("")

    counts = collections.Counter(r["strength"] for r in rows)
    out.append("**Качество объявлений по всему аккаунту:** " +
               ", ".join("%s — %d" % (STRENGTH_RU.get(k, k), v) for k, v in counts.most_common()) + "\n")

    out.append("---\n")
    out.append("## Полная таблица\n")
    out.append("| Кампания | Статус | Группа | Объявление | Качество | Модерация | URL | Код |")
    out.append("|---|---|---|---|---|---|---|---|")
    for (name, status), ads in sorted(camps.items(), key=sort_key):
        for r in ads:
            if r["ad_status"] == "REMOVED":
                continue
            heads = " · ".join(r["heads"][:6]) or "—"
            descs = " · ".join(r["descs"][:3]) or "—"
            url = r["urls"][0] if r["urls"] else ""
            code = codes.get(url, "")
            out.append("| %s | %s | %s | **З:** %s<br>**О:** %s | %s | %s | %s | %s |" % (
                cell(name), STATUS_RU.get(status, status), cell(r["ad_group"]),
                cell(heads), cell(descs),
                STRENGTH_RU.get(r["strength"], r["strength"]),
                APPROVAL_RU.get(r["approval"], r["approval"]),
                cell(url) or "—", code or "—",
            ))
    io.open(OUT, "w", encoding="utf-8").write("\n".join(out) + "\n")
    print("wrote", OUT, "| campaigns", len(camps), "| enabled", len(enabled),
          "| dead urls", len(dead), "| disapproved", len(disapproved))


if __name__ == "__main__":
    main()
