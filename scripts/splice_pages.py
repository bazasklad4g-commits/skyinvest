"""Splice a batch of hand-written landing page entries into content/landing-pages.ts.

Usage: python scripts/splice_pages.py <batch-file.ts>
The batch file holds entries only, already indented, ending with a comma.
"""
import io
import sys

TARGET = "content/landing-pages.ts"
CLOSER = "];\n\nexport const pagesBySlug"


def main():
    batch = io.open(sys.argv[1], encoding="utf-8").read().rstrip() + "\n"
    source = io.open(TARGET, encoding="utf-8").read()
    if source.count(CLOSER) != 1:
        raise SystemExit("could not find the single array closer in %s" % TARGET)
    source = source.replace(CLOSER, batch + CLOSER)
    io.open(TARGET, "w", encoding="utf-8").write(source)
    print("spliced", batch.count("    slug:"), "entries")


if __name__ == "__main__":
    main()
