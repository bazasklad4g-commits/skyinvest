"""Write every surviving informational query per city/intent to a TSV for copywriting."""
import io

from city_clusters import CITIES, FILES, INTENTS, bucket, load

OUT = "data/ads/city-informational.tsv"


def main():
    lines = ["lang\tcluster\tvolume\tquery"]
    for lang, src in FILES.items():
        rows = load(src)
        for name, spec in list(CITIES.items()) + list(INTENTS.items()):
            _, _, info = bucket(rows, spec, lang)
            for query, volume in sorted(info.items(), key=lambda t: -t[1]):
                lines.append("%s\t%s\t%d\t%s" % (lang, name, volume, query))
    io.open(OUT, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print("wrote", len(lines) - 1, "rows to", OUT)


if __name__ == "__main__":
    main()
