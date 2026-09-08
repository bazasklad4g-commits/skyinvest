"""Per-city Turkey clusters, cleaned three ways.

The owner narrowed the project twice: only buying apartments in Turkey (no rent,
no hotels), and the page text must lean on informational queries because the
account is Ad Grants.

Filtering rent and tourism by keyword is not enough: the biggest "clusters" in the
raw export are hotel and complex BRAND names -- "sun apartments marmaris",
"golden moon kusadasi", "sun city apts antalya", "gocek fethiye". They survive a
keyword blocklist because the brand itself carries no banned word. So the final
pass keeps only queries where every token is either a city name or a generic
housing word. A brand token drops the whole query.
"""
import csv
import io
import re
import sys

RENT_TOURISM = (
    "rent", "rental", "hotel", "hostel", "resort", "airbnb", "booking", "tour",
    "holiday", "vacation", "hire", "lease", "aparthotel", "all inclusive",
    "аренд", "снять", "сниму", "снимать", "отел", "хостел", "посуточ", "экскурс",
    "тур ", "туры", "отдых", "путёвк", "путевк", "авиабилет",
)
COMMERCIAL = (
    "for sale", "sale", "buy", "sell", "price", "cheap", "agency", "agent",
    "realtor", "expo", "investment", "invest",
    "купить", "куплю", "продаж", "продам", "цена", "цены", "недорого", "дешев",
    "агент", "риелтор", "риэлтор", "инвест",
)

GENERIC_EN = {
    "turkey", "turkish", "in", "the", "a", "an", "of", "for", "to", "and", "or",
    "is", "are", "it", "you", "your", "with", "on", "at", "by", "vs", "near",
    "real", "estate", "property", "properties", "realty", "housing", "house",
    "houses", "home", "homes", "apartment", "apartments", "apt", "apts", "flat",
    "flats", "villa", "villas", "living", "live", "life", "cost", "costs",
    "expenses", "expense", "family", "luxury", "new", "build", "builds", "sea",
    "view", "views", "city", "district", "districts", "area", "areas", "best",
    "where", "how", "what", "which", "why", "guide", "rules", "documents",
    "document", "tax", "taxes", "owner", "owners", "ownership", "foreigner",
    "foreigners", "residence", "permit", "citizenship", "tapu", "iskan", "dask",
    "deed", "title", "school", "schools", "transport", "metro", "safe", "safety",
    "neighbourhood", "neighborhood", "neighbourhoods", "neighborhoods", "move",
    "moving", "relocate", "relocation", "expat", "expats", "climate", "weather",
    "winter", "summer", "utilities", "aidat", "maintenance", "fee", "fees",
}
GENERIC_RU = {
    "турция", "турции", "турцию", "турецкий", "турецкая", "в", "на", "у", "для",
    "и", "с", "по", "из", "не", "или", "это", "как", "где", "что", "сколько",
    "какой", "какие", "почему", "чем", "ли", "за",
    "недвижимость", "недвижимости", "квартира", "квартиры", "квартиру",
    "квартир", "квартире", "дом", "дома", "дому", "домов", "вилла", "виллы",
    "виллу", "жилье", "жильё", "жилья", "апартаменты", "апартаментов",
    "новостройка", "новостройки", "новостройках", "вторичка", "вторички",
    "жизнь", "жизни", "жить", "проживание", "проживания", "переезд", "переезда",
    "пмж", "внж", "икамет", "гражданство", "гражданства", "тапу", "искан",
    "документы", "документов", "налог", "налоги", "налога", "содержание",
    "содержания", "коммунальные", "аидат", "море", "моря", "морю", "район",
    "районы", "районов", "районе", "семейная", "семейный", "плюсы", "минусы",
    "отзывы", "climate", "климат", "зимой", "летом", "школа", "школы",
    "транспорт", "метро", "безопасно", "безопасность", "иностранцев",
    "иностранца", "владения", "владение", "лучший", "лучшие", "обзор",
}

CITIES = {
    "Istanbul": {
        "en": ("istanbul",), "ru": ("стамбул", "стамбуле", "стамбула"),
        "tokens": {"istanbul", "стамбул", "стамбуле", "стамбула", "стамбулу"},
    },
    "Antalya": {
        "en": ("antalya",), "ru": ("анталия", "анталии", "анталью", "анталье", "анталья"),
        "tokens": {"antalya", "анталия", "анталии", "анталью", "анталье", "анталья"},
    },
    "Alanya": {
        "en": ("alanya",), "ru": ("алания", "алании", "аланию", "аланья", "аланье"),
        "tokens": {"alanya", "алания", "алании", "аланию", "аланья", "аланье"},
    },
    "Marmaris": {
        "en": ("marmaris",), "ru": ("мармарис", "мармарисе"),
        "tokens": {"marmaris", "мармарис", "мармарисе", "мармариса"},
    },
    "Fethiye": {
        "en": ("fethiye",), "ru": ("фетхие",),
        "tokens": {"fethiye", "фетхие"},
    },
    "Bodrum": {
        "en": ("bodrum",), "ru": ("бодрум", "бодруме"),
        "tokens": {"bodrum", "бодрум", "бодруме", "бодрума"},
    },
    "Kusadasi": {
        "en": ("kusadasi",), "ru": ("кушадасы", "кушадас"),
        "tokens": {"kusadasi", "кушадасы", "кушадасах"},
    },
    "Izmir": {
        "en": ("izmir",), "ru": ("измир", "измире"),
        "tokens": {"izmir", "измир", "измире", "измира"},
    },
    "Kemer": {
        "en": ("kemer",), "ru": ("кемер", "кемере"),
        "tokens": {"kemer", "кемер", "кемере", "кемера"},
    },
    "Ankara": {
        "en": ("ankara",), "ru": ("анкара", "анкаре"),
        "tokens": {"ankara", "анкара", "анкаре", "анкары"},
    },
    "Mersin": {
        "en": ("mersin",), "ru": ("мерсин", "мерсине"),
        "tokens": {"mersin", "мерсин", "мерсине", "мерсина"},
    },
    "Bursa": {
        "en": ("bursa",), "ru": ("бурса", "бурсе"),
        "tokens": {"bursa", "бурса", "бурсе", "бурсы"},
    },
    "Trabzon": {
        "en": ("trabzon",), "ru": ("трабзон", "трабзоне"),
        "tokens": {"trabzon", "трабзон", "трабзоне"},
    },
    "Belek": {
        "en": ("belek",), "ru": ("белек", "белеке"),
        "tokens": {"belek", "белек", "белеке"},
    },
    "Mahmutlar": {
        "en": ("mahmutlar",), "ru": ("махмутлар", "махмутларе"),
        "tokens": {"mahmutlar", "махмутлар", "махмутларе"},
    },
    "Didim": {
        "en": ("didim",), "ru": ("дидим",),
        "tokens": {"didim", "дидим"},
    },
}
INTENTS = {
    "Residence permit": {
        "en": ("residence permit", "ikamet"), "ru": ("внж", "вид на жительство", "икамет"),
        "tokens": set(),
    },
    "Citizenship": {
        "en": ("citizenship",), "ru": ("гражданств",),
        "tokens": set(),
    },
    "Documents": {
        "en": ("tapu", "title deed", "iskan", "dask"), "ru": ("тапу", "искан", "документ"),
        "tokens": set(),
    },
}

FILES = {"en": "data/ads/semantics-turkey-en.tsv", "ru": "data/ads/semantics-turkey.tsv"}
SPLIT = re.compile(r"[^a-zа-яёіїєґ0-9+]+")


def load(path):
    rows = {}
    try:
        handle = io.open(path, encoding="utf-8", errors="replace")
    except OSError as exc:
        print("CANNOT OPEN", path, exc, file=sys.stderr)
        return rows
    reader = csv.reader(handle, delimiter="\t")
    next(reader, None)
    for row in reader:
        if len(row) < 2:
            continue
        key = row[0].strip().lower()
        # The RU export carries a lang column before the volume; the EN one does not.
        volume = None
        for cell in row[1:]:
            try:
                volume = int(cell)
                break
            except ValueError:
                continue
        if volume is None:
            continue
        rows[key] = max(volume, rows.get(key, 0))
    return rows


def generic_only(query, lang, city_tokens):
    vocab = GENERIC_EN if lang == "en" else GENERIC_RU
    tokens = [t for t in SPLIT.split(query) if t]
    if not tokens:
        return False
    return all(t in vocab or t in city_tokens for t in tokens)


def bucket(rows, spec, lang):
    needles = spec[lang]
    hit = {k: v for k, v in rows.items() if any(n in k for n in needles)}
    clean = {k: v for k, v in hit.items() if not any(b in k for b in RENT_TOURISM)}
    info = {k: v for k, v in clean.items() if not any(c in k for c in COMMERCIAL)}
    if spec["tokens"]:
        info = {k: v for k, v in info.items() if generic_only(k, lang, spec["tokens"])}
    return hit, clean, info


def main():
    for lang, path in FILES.items():
        rows = load(path)
        if not rows:
            continue
        print("\n=== %s (%d phrases in file) ===" % (lang.upper(), len(rows)))
        print("cluster".ljust(18), "raw".rjust(7), "no-rent".rjust(8), "generic-info".rjust(13), "phrases".rjust(8), "  top")
        report = []
        for name, spec in list(CITIES.items()) + list(INTENTS.items()):
            hit, clean, info = bucket(rows, spec, lang)
            if not info:
                continue
            top = sorted(info.items(), key=lambda t: -t[1])[:4]
            report.append((sum(info.values()), name, sum(hit.values()), sum(clean.values()), len(info), top))
        for total, name, raw, clean, count, top in sorted(report, reverse=True):
            print(
                name.ljust(18), str(raw).rjust(7), str(clean).rjust(8),
                str(total).rjust(13), str(count).rjust(8),
                "  " + " | ".join("%s (%d)" % (k, v) for k, v in top),
            )


if __name__ == "__main__":
    main()
