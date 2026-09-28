"""Web-scraping entry-point for the pre-approved, openly-licensed sources
(see DECISIONS.md D026/D027 and docs/COLLECTION_PROTOCOL.md's scraping
note). This script is NOT stdlib-only like the rest of the pipeline
(scrape_source.py needs `requests` and `beautifulsoup4`) because it is a
data-*acquisition* step, run once by an author on a machine with normal
internet access — not part of the core, always-run pipeline
(preprocess/validate/review/build_release), which stays stdlib-only per
the original NETWORK RULES.

IMPORTANT — read `LOG.md`'s "Stage 9" entry before running this:
this script could NOT be executed or validated inside the assistant's
sandboxed session, because that sandbox's own egress policy blocks
every approved source's live site (africanstorybook.org, and
yo.wikipedia.org are not on the sandbox's network allowlist, which
covers only GitHub and language package registries). Only the
GitHub-mirrored `global-asp/storybooks-uganda` static site could be
reached (via `git clone`, not live HTTP), and it currently has ZERO
Rukiga and ZERO Yoruba stories (see LOG.md for how this was verified).
So: the code below is written carefully and follows each source's
documented structure (confirmed via the site's own robots.txt, its
static HTML structure inspected via a git checkout, and — for
africanstorybook.org's main catalogue — the request pattern used by
the (open source) `sushi-chef-african-storybook` project, a working
third-party scraper for the same site), but it has not been run
end-to-end against live data by the assistant. An author running this
on their own machine (normal internet access) should treat the first
run as a dry run: inspect `data/raw/raw_<lang>_scraped.csv` closely
before trusting it, and expect to need small fixes — this is exactly
why the pipeline still requires the small-batch self-check gate
(validate_auto.py) before scaling up, per Stage 9 of the brief.

Sources implemented (the pre-approved list — do not add others):

1. `global-asp/storybooks-uganda` (africanstorybook.org content
   re-published as a static site, CC BY 4.0 per story, human English
   translations already present) — read from a local git checkout,
   never live HTTP, since the checkout is what the assistant actually
   verified. As of 2026-09-29 this source has 0 Rukiga and 0 Yoruba
   stories (Rukiga is listed on the site's own "languages we hope to
   cover" page with no story link; the site is Uganda-only, so Yoruba,
   a Nigerian language, was never in scope for it). Kept here, not
   deleted, so a future run automatically picks up stories if the
   volunteer-translator project adds either language later — see
   `site_has_language()`.

2. `www.africanstorybook.org` (the main library, CC BY 4.0 per story,
   ~260 languages, "260 languages, ~5470 storybooks" per the site's own
   homepage). Its book catalogue (`bookItemsAppr`, `languages`) is
   populated by client-side JavaScript after page load — confirmed via
   the sushi-chef-african-storybook project's own scraper, which uses a
   headless browser (`pyppeteer`) specifically to read those two
   JS globals; there is no plain JSON/API endpoint for the catalogue.
   Individual books ARE downloadable without a browser once you have a
   book id, as a static EPUB: `GET /makeapp/data/landscape.php?id=<id>`
   — EPUB is just a zip of XHTML, parsed here with `zipfile` + BS4, no
   browser needed for that part. Because catalogue discovery needs a
   headless browser, `discover_book_ids()` below requires `selenium` or
   `pyppeteer` (optional import) OR a `--book-ids-file` of ids the
   author found by hand (e.g. by browsing the site's language filter
   for Rukiga and Yoruba and copying story URLs' `id=` values) — the
   sandboxed session used the latter approach is NOT possible here
   either (no way to browse the site at all from the sandbox), so no
   book ids were ever obtained.

3. `yo.wikipedia.org`'s MediaWiki REST API (`/api/rest_v1/page/summary/
   <title>` and `/api/rest_v1/page/related/<title>`, CC BY-SA 4.0,
   Yoruba backup only, per D026/D027 — no Wikipedia backup exists for
   Rukiga). Uses the REST API only, never HTML crawling (the brief's
   own note that robots.txt blocks HTML crawling matches Wikimedia's
   documented bot policy). `translation_source` is always "machine"
   for this source since the site provides no English translation —
   this script does NOT ship a machine-translation backend (none of
   the sandbox's allowed package registries were reachable together
   with a translation model/API in the time available); `translate()`
   below is a clearly-marked stub the author must fill in with their
   own MT of choice (e.g. an API key for a translation service, or a
   local model) before running against Yoruba Wikipedia content.

Every function respects robots.txt (`urllib.robotparser`) and rate-limits
requests (`RATE_LIMIT_SECONDS` between requests to the same host). Every
unit is checked for PII-shaped content and for naming a private
individual before being kept (`looks_like_pii` / `mentions_named_person`)
— matching docs/COLLECTION_PROTOCOL.md's "never collect" list, applied to
scraped text as required by DECISIONS.md D026's carried-forward DATA
SAFETY RULES.
"""
from __future__ import annotations

import argparse
import re
import sys
import time
import urllib.robotparser
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from urllib.parse import urljoin, urlparse

import common

# Reuse the pipeline's own PII patterns rather than redefining them, so
# scrape-time filtering and validate_auto.py's PII check never drift
# apart. validate_auto.py is a sibling script in scripts/, imported the
# same way common.py is (see docs/SCHEMA.md's "Raw vs. processed" note:
# scraped rows still go through the same validate_auto.py afterwards —
# this is a *pre*-filter, not a replacement for it).
import validate_auto as va

RATE_LIMIT_SECONDS = 2.0
USER_AGENT = (
    "african-lang-data-practicals-coursework-bot/1.0 "
    "(course dataset project; contact amosnabasa4@gmail.com; "
    "see practical2/docs/COLLECTION_PROTOCOL.md)"
)

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"

# ---------------------------------------------------------------------------
# Shared helpers: robots.txt, rate limiting, PII/person-name pre-filter
# ---------------------------------------------------------------------------

_robots_cache: dict[str, urllib.robotparser.RobotFileParser] = {}
_last_request_time: dict[str, float] = {}


def _robots_for(url: str) -> urllib.robotparser.RobotFileParser:
    parsed = urlparse(url)
    origin = f"{parsed.scheme}://{parsed.netloc}"
    if origin not in _robots_cache:
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(urljoin(origin, "/robots.txt"))
        try:
            rp.read()
        except OSError:
            # If robots.txt itself can't be fetched, fail closed: treat
            # everything as disallowed rather than assuming it's fine.
            rp.disallow_all = True  # type: ignore[attr-defined]
        _robots_cache[origin] = rp
    return _robots_cache[origin]


def allowed_by_robots(url: str) -> bool:
    rp = _robots_for(url)
    return rp.can_fetch(USER_AGENT, url)


def rate_limit(url: str) -> None:
    host = urlparse(url).netloc
    last = _last_request_time.get(host)
    now = time.monotonic()
    if last is not None:
        elapsed = now - last
        if elapsed < RATE_LIMIT_SECONDS:
            time.sleep(RATE_LIMIT_SECONDS - elapsed)
    _last_request_time[host] = time.monotonic()


# A private-individual name mention is inherently heuristic (this pipeline
# is not fluent in either target language — see VIVA_NOTES.md's "How was
# validation designed?"), so this is a conservative pattern-based filter,
# not a claim of certainty: it flags likely personal-name patterns for a
# human to double check, same spirit as validate_auto.py's other checks.
_CAPITALIZED_NAME_RUN_RE = re.compile(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})\b")


def looks_like_pii(text: str) -> bool:
    """Reuses the pipeline's own PII regexes (email/phone/handle), minus
    URL_RE — scraped *story* text legitimately containing no URLs is the
    expectation, and we don't want to reuse URL_RE here since it would
    need separate handling from how validate_auto.py applies it to the
    source_url field specifically."""
    return bool(
        va.EMAIL_RE.search(text)
        or va.HANDLE_RE.search(text)
        or va.UG_PHONE_RE.search(text)
        or va.NG_PHONE_RE.search(text)
        or va.INTL_PHONE_RE.search(text)
    )


def mentions_named_person(text: str, known_author_names: tuple[str, ...] = ()) -> bool:
    """Heuristic only (see docstring above): flags runs of 2-4
    capitalized words, which commonly indicate a full personal name, so
    the unit can be skipped per docs/COLLECTION_PROTOCOL.md's "names of
    private individuals" rule. `known_author_names` (e.g. story
    author/illustrator/translator credits, which ARE meant to be public
    and are recorded separately, not in `text`) are excluded so this
    doesn't over-flag ordinary story-credit lines that never make it
    into the entry `text` field anyway."""
    for match in _CAPITALIZED_NAME_RUN_RE.finditer(text):
        name = match.group(1)
        if name not in known_author_names:
            return True
    return False


def is_self_contained_unit(text: str) -> bool:
    """Short, sentence-like, non-empty. Deliberately conservative — this
    is a pre-filter before validate_auto.py's own empty/short check, not
    a replacement for it."""
    text = text.strip()
    if not text:
        return False
    word_count = len(text.split())
    return 2 <= word_count <= 60


@dataclass
class ScrapedUnit:
    language: str
    text: str
    translation_en: str
    source_url: str
    site_name: str
    source_license: str
    translation_source: str  # "site" or "machine"
    retrieved_date: str = field(default_factory=lambda: date.today().isoformat())
    region: str = ""
    dialect: str = ""
    domain: str = ""

    def to_row(self) -> dict:
        return {
            "id": "",  # assigned later by preprocess.py's assign_ids
            "language": self.language,
            "text": self.text,
            "translation_en": self.translation_en,
            "contributor_id": common.CONTRIBUTOR_ID_NA,
            "region": self.region,
            "dialect": self.dialect,
            "date_collected": "",
            "source_type": "web-scraped",
            "domain": self.domain,
            "reviewed": "false",
            "reviewer_id": "",
            "reviewed_by_independent": "false",
            "source_url": self.source_url,
            "site_name": self.site_name,
            "retrieved_date": self.retrieved_date,
            "source_license": self.source_license,
            "translation_source": self.translation_source,
        }


# ---------------------------------------------------------------------------
# Source 1: global-asp/storybooks-uganda (local git checkout only)
# ---------------------------------------------------------------------------

STORYBOOKS_UGANDA_SITE_NAME = "Storybooks Uganda (africanstorybook.org content, GitHub Pages mirror)"
STORYBOOKS_UGANDA_LICENSE = "CC BY 4.0 (per-story attribution required; see each story's credits)"

# Language-name -> directory-code mapping as published in
# stories/index.html and about/languages/index.html of the
# global-asp/storybooks-uganda repo (verified 2026-09-29 via a git
# checkout — see LOG.md). Rukiga is NOT present (listed under "languages
# we hope to cover" with no story link); kept as None here rather than
# omitted, so `site_has_language()` gives an explicit, logged "no" rather
# than a silent KeyError if this script is ever pointed at "cgg".
STORYBOOKS_UGANDA_LANG_DIRS = {
    "cgg": None,  # Rukiga: listed, not yet translated/linked (checked 2026-09-29)
    "yor": None,  # Yoruba: not in scope for this Uganda-only site
}


def site_has_language(repo_root: Path, lang: str) -> bool:
    lang_dir = STORYBOOKS_UGANDA_LANG_DIRS.get(lang)
    if lang_dir is None:
        return False
    return (repo_root / "stories" / lang_dir).is_dir()


def scrape_storybooks_uganda(repo_root: Path, lang: str) -> list[ScrapedUnit]:
    """Reads from a local `git clone` of global-asp/storybooks-uganda
    (public repo, no auth needed) rather than live HTTP — see the module
    docstring for why. Run:
        git clone --depth 1 https://github.com/global-asp/storybooks-uganda
    first, then pass that path as `repo_root`.
    """
    if not site_has_language(repo_root, lang):
        print(
            f"[storybooks-uganda] no stories for language={lang!r} as of "
            "this checkout (see LOG.md Stage 9) -- skipping.",
            file=sys.stderr,
        )
        return []

    lang_dir = repo_root / "stories" / STORYBOOKS_UGANDA_LANG_DIRS[lang]
    units: list[ScrapedUnit] = []
    for story_dir in sorted(lang_dir.glob("[0-9][0-9][0-9][0-9]")):
        index_html = story_dir / "index.html"
        if not index_html.exists():
            continue
        units.extend(_parse_storybooks_uganda_story(index_html, lang))
    return units


def _parse_storybooks_uganda_story(index_html: Path, lang: str) -> list[ScrapedUnit]:
    """Each story page has repeating blocks:
        <div class="... level1-txt def"><h3>LOCAL LANGUAGE TEXT</h3></div>
        <div class="... level1-txt l1"><h3>ENGLISH TEXT</h3></div>
    (verified directly against a real checked-out page,
    stories/nyn/0327/index.html -- see LOG.md). This uses a small,
    tolerant regex rather than pulling in an HTML parser dependency
    beyond what's already required for the EPUB source below; if the
    markup changes this will simply find nothing (fails safe, not
    silently wrong) -- the small-batch gate would show empty output.
    """
    from bs4 import BeautifulSoup  # optional dep, only needed for scraping

    html = index_html.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")

    canonical_link = soup.find("link", rel="canonical")
    story_url = canonical_link["href"] if canonical_link else str(index_html)

    units: list[ScrapedUnit] = []
    local_blocks = soup.select("div.level1-txt.def h3")
    en_blocks = soup.select("div.level1-txt.l1 h3")
    for local_el, en_el in zip(local_blocks, en_blocks):
        local_text = local_el.get_text(strip=True)
        en_text = en_el.get_text(strip=True)
        if not is_self_contained_unit(local_text) or not en_text:
            continue
        if looks_like_pii(local_text) or looks_like_pii(en_text):
            continue
        if mentions_named_person(local_text) or mentions_named_person(en_text):
            continue
        units.append(
            ScrapedUnit(
                language=lang,
                text=local_text,
                translation_en=en_text,
                source_url=story_url,
                site_name=STORYBOOKS_UGANDA_SITE_NAME,
                source_license=STORYBOOKS_UGANDA_LICENSE,
                translation_source="site",  # human-translated per the site's credits
            )
        )
    return units


# ---------------------------------------------------------------------------
# Source 2: www.africanstorybook.org (requires live internet; NOT reachable
# from the assistant's sandbox -- see module docstring)
# ---------------------------------------------------------------------------

ASB_SITE_NAME = "African Storybook (africanstorybook.org)"
ASB_LICENSE = "CC BY 4.0 (per-story; confirm on each story's credits page)"
ASB_EPUB_URL = "https://www.africanstorybook.org/makeapp/data/landscape.php?id={book_id}"


def discover_book_ids(language_name: str, book_ids_file: Path | None) -> list[str]:
    """Book-catalogue discovery needs a JS-executing browser (the site
    populates `bookItemsAppr`/`languages` via client-side JS -- confirmed
    against the sushi-chef-african-storybook project's own scraper code,
    which uses `pyppeteer` for exactly this; see LOG.md). This script
    does not bundle a headless-browser dependency, so:
      - if `book_ids_file` is given (one numeric id per line, found by
        the author browsing the site's language filter by hand and
        copying each story's `id=` value), those ids are used directly;
      - otherwise this raises, rather than silently returning nothing,
        so a missing book-ids file is never mistaken for "no stories
        exist".
    """
    if book_ids_file is not None:
        return [
            line.strip()
            for line in book_ids_file.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
    raise RuntimeError(
        f"No automated way to discover africanstorybook.org book ids for "
        f"{language_name!r} without a JS-executing browser (see module "
        "docstring). Pass --book-ids-file, or add a headless-browser "
        "catalogue step (selenium/pyppeteer) before calling this."
    )


def scrape_africanstorybook(lang: str, language_name: str, book_ids_file: Path | None) -> list[ScrapedUnit]:
    import requests
    from bs4 import BeautifulSoup

    book_ids = discover_book_ids(language_name, book_ids_file)
    units: list[ScrapedUnit] = []
    session = requests.Session()
    session.headers["User-Agent"] = USER_AGENT

    for book_id in book_ids:
        epub_page_url = f"https://www.africanstorybook.org/reader.php?id={book_id}"
        if not allowed_by_robots(epub_page_url):
            print(f"[africanstorybook] robots.txt disallows {epub_page_url}, skipping.", file=sys.stderr)
            continue

        download_url = ASB_EPUB_URL.format(book_id=book_id)
        rate_limit(download_url)
        response = session.get(download_url, timeout=30)
        response.raise_for_status()

        import io
        import zipfile

        with zipfile.ZipFile(io.BytesIO(response.content)) as epub_zip:
            for name in epub_zip.namelist():
                if not name.endswith((".xhtml", ".html")):
                    continue
                content = epub_zip.read(name).decode("utf-8", errors="replace")
                soup = BeautifulSoup(content, "html.parser")
                for para in soup.find_all(["p", "h1", "h2", "h3"]):
                    text = para.get_text(strip=True)
                    if not is_self_contained_unit(text):
                        continue
                    if looks_like_pii(text) or mentions_named_person(text):
                        continue
                    # The EPUB export bundles all language variants of a
                    # story together in some ASB books; without a
                    # per-paragraph language tag, this script cannot
                    # safely tell target-language text apart from the
                    # English/other-language text also present. Rather
                    # than guess, this is left as an explicit TODO for
                    # whoever runs this with real internet access to
                    # resolve by inspecting a real downloaded EPUB
                    # (structure could not be verified in the sandbox --
                    # see LOG.md) and to make PARAGRAPH LANGUAGE
                    # DETECTION EXPLICIT here before trusting any output.
                    raise NotImplementedError(
                        "EPUB paragraph-language separation was not "
                        "verified against a real downloaded file in the "
                        "sandboxed session (network blocked -- see "
                        "LOG.md Stage 9). Inspect a real EPUB's XHTML "
                        "structure first, then implement the "
                        "target-language-vs-other-language split here "
                        "before using this function."
                    )
    return units


# ---------------------------------------------------------------------------
# Source 3: yo.wikipedia.org REST API (Yoruba backup only; NOT reachable
# from the assistant's sandbox -- see module docstring)
# ---------------------------------------------------------------------------

YOWIKI_SITE_NAME = "Yoruba Wikipedia (yo.wikipedia.org)"
YOWIKI_LICENSE = "CC BY-SA 4.0"
YOWIKI_API_BASE = "https://yo.wikipedia.org/api/rest_v1"


def translate(text: str) -> str:
    """Machine-translation stub -- NOT implemented. This pipeline ships
    no MT backend (no network access to any MT API/model was available
    in the assistant's sandbox, and bundling one is a decision an author
    should make deliberately, e.g. which service, whether it needs an
    API key). Wire this up to a real MT call before using
    scrape_yoruba_wikipedia() for anything beyond a dry run, and keep
    translation_source="machine" so this is never mistaken for a site's
    own human translation (see DECISIONS.md D026)."""
    raise NotImplementedError(
        "translate() is a stub -- wire up a real machine-translation "
        "backend before scraping Yoruba Wikipedia content (see "
        "docstring). Never fabricate a translation by hand here."
    )


def scrape_yoruba_wikipedia(titles: list[str]) -> list[ScrapedUnit]:
    import requests

    session = requests.Session()
    session.headers["User-Agent"] = USER_AGENT
    units: list[ScrapedUnit] = []

    for title in titles:
        summary_url = f"{YOWIKI_API_BASE}/page/summary/{title}"
        if not allowed_by_robots(summary_url):
            print(f"[yo.wikipedia] robots.txt disallows {summary_url}, skipping.", file=sys.stderr)
            continue

        rate_limit(summary_url)
        response = session.get(summary_url, timeout=30)
        response.raise_for_status()
        data = response.json()
        extract = data.get("extract", "")

        # Split into sentence-like units on Yoruba sentence-final
        # punctuation. This is a coarse heuristic (this pipeline is not
        # fluent in Yoruba -- see VIVA_NOTES.md) and should be checked
        # by the Layer 1 independent reviewer like any other entry.
        for sentence in re.split(r"(?<=[.!?])\s+", extract):
            sentence = sentence.strip()
            if not is_self_contained_unit(sentence):
                continue
            if looks_like_pii(sentence) or mentions_named_person(sentence):
                continue
            units.append(
                ScrapedUnit(
                    language="yor",
                    text=sentence,
                    translation_en=translate(sentence),  # raises until wired up -- see translate()
                    source_url=data.get("content_urls", {}).get("desktop", {}).get("page", summary_url),
                    site_name=YOWIKI_SITE_NAME,
                    source_license=YOWIKI_LICENSE,
                    translation_source="machine",
                )
            )
    return units


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        choices=["storybooks-uganda", "africanstorybook", "yo-wikipedia"],
        required=True,
    )
    parser.add_argument("--lang", choices=common.LANGUAGES, required=True)
    parser.add_argument(
        "--storybooks-uganda-repo",
        type=Path,
        help="Path to a local `git clone` of global-asp/storybooks-uganda.",
    )
    parser.add_argument(
        "--book-ids-file",
        type=Path,
        help="For --source africanstorybook: file of numeric book ids, one per line.",
    )
    parser.add_argument(
        "--yowiki-titles-file",
        type=Path,
        help="For --source yo-wikipedia: file of Yoruba Wikipedia article titles, one per line.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        help="Output CSV path. Default: data/raw/raw_<lang>_scraped.csv",
    )
    args = parser.parse_args()

    if args.source == "storybooks-uganda":
        if args.storybooks_uganda_repo is None:
            parser.error("--storybooks-uganda-repo is required for --source storybooks-uganda")
        units = scrape_storybooks_uganda(args.storybooks_uganda_repo, args.lang)
    elif args.source == "africanstorybook":
        language_name = common.LANGUAGE_NAMES[args.lang]
        units = scrape_africanstorybook(args.lang, language_name, args.book_ids_file)
    else:
        if args.lang != "yor":
            parser.error("--source yo-wikipedia only supports --lang yor (no Wikipedia backup for Rukiga)")
        if args.yowiki_titles_file is None:
            parser.error("--yowiki-titles-file is required for --source yo-wikipedia")
        titles = [
            line.strip()
            for line in args.yowiki_titles_file.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        units = scrape_yoruba_wikipedia(titles)

    out_path = args.out or (RAW_DIR / f"raw_{args.lang}_scraped.csv")
    rows = [u.to_row() for u in units]
    common.write_csv(out_path, common.ALL_FIELDS, rows)
    print(f"Wrote {len(rows)} scraped units for lang={args.lang!r} to {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
