#!/usr/bin/env python
"""Реестр страниц сайта: что есть в коде, что в sitemap, что закрыто кампанией."""
import io, json, re, urllib.request
from collections import defaultdict

from google.ads.googleads.client import GoogleAdsClient
from google.oauth2 import service_account

BASE = "https://m.nezalezhnist.org.ua"

# --- страницы из кода ---
pages = []
for path, kind in (("content/landing-pages.ts", "Коммерческая"),
                   ("content/grant-landing-pages.ts", "Просветительская")):
    s = io.open(path, encoding="utf-8").read()
    for m in re.finditer(r'slug:\s*"([^"]+)"', s):
        tail = s[m.end():m.end() + 3000]
        def grab(field):
            g = re.search(field + ':\s*"([^"]*)"', tail)
            return g.group(1) if g else ""
        locale = grab("locale") or "ru"
        pages.append({"slug": m.group(1), "kind": kind, "locale": locale,
                      "title": grab("title"), "h1": grab("h1"), "offer": grab("offer")})

# --- живой sitemap ---
xml = urllib.request.urlopen(f"{BASE}/sitemap.xml", timeout=60).read().decode("utf-8")
live = {u.rsplit("/", 1)[-1] for u in re.findall(r"<loc>([^<]+)</loc>", xml)}

# --- кампании по посадочным ---
client = GoogleAdsClient(
    credentials=service_account.Credentials.from_service_account_file(
        ".secrets/gstar-sa.json", scopes=["https://www.googleapis.com/auth/adwords"]),
    developer_token="t8wOf5cvS7HV5V7gjHnH2w", login_customer_id="8522851042",
    version="v22", use_proto_plus=True)
ga = client.get_service("GoogleAdsService")
by_url = defaultdict(set)
for row in ga.search(customer_id="3432200766", query="""
    SELECT campaign.name, campaign.status, ad_group_ad.ad.final_urls
    FROM ad_group_ad WHERE campaign.status != 'REMOVED'
"""):
    for url in row.ad_group_ad.ad.final_urls:
        slug = url.rstrip("/").rsplit("/", 1)[-1]
        status = row.campaign.status.name
        mark = "ВКЛ" if status == "ENABLED" else "пауза"
        by_url[slug].add(f"{row.campaign.name} ({mark})")

lang_name = {"ru": "RU", "uk": "UK", "en": "EN"}
lines = [f"# Страницы {BASE}", "",
         f"Всего страниц: **{len(pages)}**. В sitemap: **{len(live)}**.", ""]

for kind in ("Коммерческая", "Просветительская"):
    group = [p for p in pages if p["kind"] == kind]
    lines += [f"## {kind}: {len(group)}", "",
              "| URL | Яз. | Заголовок страницы | Оффер формы | Кампания |",
              "|---|---|---|---|---|"]
    for p in sorted(group, key=lambda x: x["slug"]):
        camps = by_url.get(p["slug"], set())
        shown = sorted(c for c in camps if "(ВКЛ)" in c) or sorted(camps)
        mark = "<br>".join(shown[:3]) if shown else "—"
        title = (p["h1"] or p["title"])[:70]
        lines.append(f"| `/{p['slug']}` | {lang_name.get(p['locale'], p['locale'])} | "
                     f"{title} | {p['offer'][:38]} | {mark} |")
    lines.append("")

orphan = [p["slug"] for p in pages
          if not any("(ВКЛ)" in c for c in by_url.get(p["slug"], []))]
lines += ["## Без включённой кампании", "",
          f"Таких страниц **{len(orphan)}**:", ""] + [f"- `/{s}`" for s in sorted(orphan)]

missing = live - {p["slug"] for p in pages}
extra = {p["slug"] for p in pages} - live
if missing or extra:
    lines += ["", "## Расхождения кода и sitemap", ""]
    for s in sorted(missing):
        lines.append(f"- в sitemap есть, в коде нет: `/{s}`")
    for s in sorted(extra):
        lines.append(f"- в коде есть, в sitemap нет: `/{s}`")

io.open("data/ads/PAGES.md", "w", encoding="utf-8").write("\n".join(lines) + "\n")
print(f"страниц {len(pages)}, без кампании {len(orphan)}")
print("Файл: data/ads/PAGES.md")
