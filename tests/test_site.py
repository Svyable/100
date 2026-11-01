import json
import posixpath
import re
import sys
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_site
import mdlite
import sitegen

DOCS = ROOT / "docs"
FILES = build_site.site_files()


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids, self.links, self.h1, self.titles = set(), [], 0, []
        self._in_title = False
        self.canonical = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.add(a["id"])
        if tag == "h1":
            self.h1 += 1
        if tag == "title":
            self._in_title = True
        if tag == "link" and a.get("rel") == "canonical":
            self.canonical = a.get("href")
        for key in ("href", "src"):
            if key in a and tag in ("a", "link", "script", "img"):
                self.links.append(a[key])

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.titles.append(data)


def parse(text):
    page = Page()
    page.feed(text)
    return page


PAGES = {path: parse(text) for path, text in FILES.items() if path.endswith(".html")}


def resolve(page_path, href):
    """Site-relative target path (or None for external links)."""
    parts = urlsplit(href)
    if parts.scheme or href.startswith("//"):
        return None, None
    if href.startswith("/100/"):
        path = href[len("/100/"):]
    elif parts.path == "":
        return page_path, parts.fragment
    else:
        base = posixpath.dirname(page_path)
        path = posixpath.join(base, parts.path)
    trailing = parts.path.endswith("/") or parts.path in (".", "./")
    target = posixpath.normpath(unquote(urlsplit(path).path))
    target = "" if target == "." else target
    if trailing or target == "":
        target = (target + "/" if target else "") + "index.html"
    return target, parts.fragment


class TestSnapshot(unittest.TestCase):
    def test_committed_site_is_current(self):
        drift, stale = build_site.check(FILES)
        self.assertEqual(drift, [], "run python3 scripts/build_site.py")
        self.assertEqual(stale, [])

    def test_all_100_with_stable_ranks(self):
        doc = json.loads(FILES["data/portfolio.json"])
        p = doc["problems"]
        self.assertEqual(len(p), 100)
        self.assertEqual([item["rank"] for item in p], list(range(1, 101)))
        self.assertEqual(len({item["id"] for item in p}), 100)
        self.assertEqual(sum(doc["status_counts"].values()), 100)
        self.assertEqual(sorted(p, key=lambda x: (-x["score"], x["id"])), p)
        self.assertTrue(all(20 <= item["score"] <= 100 for item in p))
        self.assertEqual(sorted(x["execution_rank"] for x in p), list(range(1, 101)))
        self.assertTrue(all(x["execution_score"] == x["score"] + x["readiness"] for x in p))
        self.assertEqual(len(doc["execution_queue"]), doc["summary"]["campaigns"])
        self.assertEqual(doc["summary"]["fully_solved"], len(doc["solved"]))
        lab = doc["lab"]
        self.assertEqual(doc["summary"]["problems_with_exact_verifier"], len(lab["covered_problems"]))
        self.assertTrue(all(run["holds"] for probe in lab["probes"] for run in probe["runs"].values()))

    def test_build_is_deterministic(self):
        self.assertEqual(FILES, build_site.site_files())


class TestPages(unittest.TestCase):
    def test_one_page_per_problem_field_and_document(self):
        ids = [p["id"] for p in json.loads((ROOT / "data" / "problems.json").read_text(encoding="utf-8"))]
        for pid in ids:
            self.assertIn(f"problems/{pid}/index.html", FILES)
            self.assertIn(f"api/problems/{pid}.json", FILES)
        self.assertEqual(sum(k.startswith("fields/") for k in FILES), 10)
        for path in ("index.html", "atlas/index.html", "lab/index.html", "formal/index.html",
                     "campaigns/index.html", "claims/index.html", "ledger/index.html",
                     "library/index.html", "api/index.html", "404.html", "feed.xml",
                     "sitemap.xml", "robots.txt", "api/problems.csv", "api/search.json"):
            self.assertIn(path, FILES)
        self.assertTrue(any(k.startswith("library/") and k != "library/index.html" for k in FILES))

    def test_every_internal_link_and_fragment_resolves(self):
        broken = []
        for path, page in PAGES.items():
            for href in page.links:
                target, frag = resolve(path, href)
                if target is None:
                    continue
                if target.startswith("assets/"):
                    if not (DOCS / target).is_file():
                        broken.append((path, href))
                    continue
                if target not in FILES:
                    broken.append((path, href))
                elif frag and target.endswith(".html") and frag not in PAGES[target].ids:
                    broken.append((path, href + " (missing fragment)"))
        self.assertEqual(broken, [])

    def test_external_links_are_https_only(self):
        for path, page in PAGES.items():
            for href in page.links:
                if urlsplit(href).scheme:
                    self.assertEqual(urlsplit(href).scheme, "https", (path, href))

    def test_page_metadata(self):
        titles = {}
        for path, page in PAGES.items():
            self.assertEqual(page.h1, 1, path)
            title = "".join(page.titles).strip()
            self.assertTrue(title, path)
            titles.setdefault(title, []).append(path)
            if path != "404.html":
                self.assertTrue(page.canonical.startswith(sitegen.SITE_URL), path)
        self.assertEqual({t: p for t, p in titles.items() if len(p) > 1}, {})

    def test_sitemap_lists_every_page(self):
        locs = set(re.findall(r"<loc>([^<]+)</loc>", FILES["sitemap.xml"]))
        pages = {sitegen.SITE_URL + k[:-len("index.html")] for k in FILES if k.endswith("index.html")}
        self.assertEqual(locs, pages)

    def test_problem_page_content(self):
        page = FILES["problems/M071/index.html"]
        for needle in ("Hadwiger conjecture", 'id="formal"', 'id="campaign"', 'id="claim-review"',
                       "Hundred.Hadwiger.Statement", "rel=\"prev\"", "rel=\"next\"", "Permalink"):
            self.assertIn(needle, page)
        self.assertIn('id="formal"', FILES["problems/M001/index.html"])
        self.assertIn("No Lean comparator statement yet", FILES["problems/M001/index.html"])

    def test_index_rows_and_controls(self):
        index = FILES["index.html"]
        page = PAGES["index.html"]
        self.assertEqual(index.count('class="row"'), 100)
        self.assertTrue({"problem-list", "results-count", "search-problems", "filter-field", "filter-status",
                         "filter-modality", "sort-problems", "only-verifier", "only-campaign", "only-lean",
                         "reset-filters", "empty-state", "palette", "palette-input"} <= page.ids)
        for path in ("assets/app.js", "assets/style.css", "assets/favicon.svg"):
            self.assertIn("./" + path, page.links)
        self.assertTrue((DOCS / ".nojekyll").is_file())

    def test_api_matches_registry(self):
        api = json.loads(FILES["api/problems.json"])
        self.assertEqual(api["count"], 100)
        self.assertEqual([p["execution_rank"] for p in api["problems"]], list(range(1, 101)))
        one = json.loads(FILES["api/problems/M094.json"])
        self.assertEqual(one["id"], "M094")
        self.assertTrue(one["formal_statement"]["module"].endswith("Hadamard.lean"))
        self.assertEqual(len(FILES["api/problems.csv"].strip().splitlines()), 101)
        search = json.loads(FILES["api/search.json"])
        self.assertTrue(all(resolve("index.html", item["u"])[0] in FILES for item in search))

    def test_untrusted_text_is_escaped(self):
        self.assertNotIn("<script>alert", "".join(FILES[k] for k in PAGES))
        self.assertEqual(sitegen.ext("javascript:alert(1)", "x"), "x")
        self.assertNotIn("<a", sitegen.repo_link("../../etc/passwd"))


class TestMarkdown(unittest.TestCase):
    def test_escapes_raw_html_and_unsafe_links(self):
        out = mdlite.render("<script>x</script> [a](javascript:alert(1)) [b](https://ok.example/x_(y))")
        self.assertNotIn("<script>", out)
        self.assertNotIn("javascript:", out)
        self.assertIn('href="https://ok.example/x_(y)"', out)

    def test_tables_headings_lists_code(self):
        out = mdlite.render("# T\n\n## Sec one\n\n| a | b |\n|---|--:|\n| `x|y` | 2<br>3 |\n\n1. one\n2. two\n\n```sh\na < b\n```\n")
        self.assertIn('<h2 id="sec-one">', out)
        self.assertIn('<td class="al-right">2<br>3</td>', out)
        self.assertIn("<code>x|y</code>", out)
        self.assertIn("<ol><li>one</li><li>two</li></ol>", out)
        self.assertIn("a &lt; b", out)

    def test_github_compatible_slugs(self):
        self.assertEqual(mdlite.slugify("M074 — Caccetta–Häggkvist (r = 6)"), "m074--caccettahäggkvist-r--6")


if __name__ == "__main__":
    unittest.main()
