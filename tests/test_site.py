#!/usr/bin/env python3
"""Validate source metadata and the generated NGINX Wiki site."""

from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from dataclasses import dataclass, field
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
SITE = ROOT / "site"
SITE_URL = "https://nginx-wiki.getpagespeed.com/"


@dataclass
class PageData:
    """SEO-relevant values extracted from one generated HTML page."""

    titles: list[str] = field(default_factory=list)
    descriptions: list[str] = field(default_factory=list)
    canonicals: list[str] = field(default_factory=list)
    json_ld: list[dict[str, object]] = field(default_factory=list)
    json_ld_raw: list[str] = field(default_factory=list)


class SiteParser(HTMLParser):
    """Extract SEO metadata without third-party parser dependencies."""

    def __init__(self) -> None:
        super().__init__()
        self.data = PageData()
        self._in_title = False
        self._in_json_ld = False
        self._buffer: list[str] = []

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        values = dict(attrs)
        if tag == "title":
            self._in_title = True
            self._buffer = []
        elif tag == "meta" and values.get("name") == "description":
            self.data.descriptions.append(values.get("content") or "")
        elif tag == "link" and values.get("rel") == "canonical":
            self.data.canonicals.append(values.get("href") or "")
        elif tag == "script" and values.get("type") == "application/ld+json":
            self._in_json_ld = True
            self._buffer = []

    def handle_data(self, value: str) -> None:
        if self._in_title or self._in_json_ld:
            self._buffer.append(value)

    def handle_endtag(self, tag: str) -> None:
        if tag == "title" and self._in_title:
            self.data.titles.append("".join(self._buffer).strip())
            self._in_title = False
        elif tag == "script" and self._in_json_ld:
            self.data.json_ld_raw.append("".join(self._buffer).strip())
            self._in_json_ld = False


def fail(errors: list[str], message: str) -> None:
    """Collect a validation failure without stopping the full audit."""

    errors.append(message)


def front_matter(path: Path) -> dict[str, str]:
    """Read the scalar fields used by the site's simple YAML front matter."""

    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n") or "\n---\n" not in text:
        return {}
    block = text.split("\n---\n", 1)[0]
    values: dict[str, str] = {}
    for key in ("title", "description", "date", "updated", "schema_type"):
        match = re.search(rf"(?m)^{key}:\s*(.*)$", block)
        if match:
            values[key] = match.group(1).strip().strip('"\'')
    return values


def validate_source(errors: list[str]) -> None:
    """Validate unique metadata and honest article dates at source."""

    titles: Counter[str] = Counter()
    descriptions: Counter[str] = Counter()
    for path in sorted(DOCS.rglob("*.md")):
        if path.name.endswith(".ru.md") or "includes" in path.parts:
            continue
        metadata = front_matter(path)
        relative = path.relative_to(ROOT)
        for key in ("title", "description"):
            if not metadata.get(key):
                fail(errors, f"{relative}: missing {key} front matter")
        if metadata.get("title"):
            titles[metadata["title"]] += 1
        if metadata.get("description"):
            descriptions[metadata["description"]] += 1
        if metadata.get("schema_type") == "TechArticle":
            try:
                published = date.fromisoformat(metadata["date"])
                modified = date.fromisoformat(metadata["updated"])
            except (KeyError, ValueError):
                fail(errors, f"{relative}: TechArticle requires ISO date and updated")
            else:
                if published > modified:
                    fail(errors, f"{relative}: published date is after modified date")
    for label, values in (("title", titles), ("description", descriptions)):
        for value, count in values.items():
            if count > 1:
                fail(errors, f"duplicate {label} on {count} source pages: {value}")


def validate_html(errors: list[str]) -> None:
    """Validate canonical tags, descriptions, titles, and JSON-LD."""

    html_files = sorted(SITE.rglob("*.html"))
    if not html_files:
        fail(errors, "site contains no generated HTML files")
        return
    for path in html_files:
        if path.name == "404.html" or "overrides" in path.parts:
            continue
        parser = SiteParser()
        text = path.read_text(encoding="utf-8")
        parser.feed(text)
        relative = path.relative_to(SITE)
        if "G-XXXXXXXXXX" in text:
            fail(errors, f"{relative}: placeholder analytics ID is present")
        for label, values in (
            ("title", parser.data.titles),
            ("description", parser.data.descriptions),
            ("canonical", parser.data.canonicals),
        ):
            if len(values) != 1 or not values[0]:
                fail(errors, f"{relative}: expected one non-empty {label}, got {len(values)}")
        if parser.data.canonicals:
            canonical = parser.data.canonicals[0]
            if not canonical.startswith(SITE_URL):
                fail(errors, f"{relative}: canonical is outside the production site")
        for index, raw in enumerate(parser.data.json_ld_raw):
            try:
                parser.data.json_ld.append(json.loads(raw))
            except json.JSONDecodeError as exc:
                fail(errors, f"{relative}: JSON-LD block {index} is invalid: {exc}")
        website_nodes = [
            item for item in parser.data.json_ld if item.get("@type") == "WebSite"
        ]
        if relative == Path("index.html"):
            if len(website_nodes) != 1:
                fail(errors, f"homepage: expected one WebSite node, got {len(website_nodes)}")
        elif website_nodes:
            fail(errors, f"{relative}: WebSite schema must only appear on the homepage")


def validate_locales(errors: list[str]) -> None:
    """Ensure the incomplete Russian locale is not published."""

    ru_pages = sorted((SITE / "ru").rglob("*.html")) if (SITE / "ru").exists() else []
    if ru_pages:
        found = ", ".join(str(path.relative_to(SITE)) for path in ru_pages)
        fail(errors, f"incomplete Russian locale was published: {found}")


def validate_sitemap(errors: list[str]) -> None:
    """Validate sitemap URLs and prevent duplicate language fallbacks."""

    path = SITE / "sitemap.xml"
    if not path.exists():
        fail(errors, "sitemap.xml was not generated")
        return
    root = ET.parse(path).getroot()
    namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    locations = [node.text or "" for node in root.findall("sm:url/sm:loc", namespace)]
    if len(locations) != len(set(locations)):
        fail(errors, "sitemap.xml contains duplicate URLs")
    for location in locations:
        parsed = urlparse(location)
        if f"{parsed.scheme}://{parsed.netloc}/" != SITE_URL:
            fail(errors, f"sitemap contains URL outside production site: {location}")
        if parsed.path.startswith("/ru/"):
            fail(errors, f"sitemap contains incomplete Russian locale: {location}")


def validate_tags(errors: list[str]) -> None:
    """Confirm the tag index was rendered rather than left as a placeholder."""

    path = SITE / "tags" / "index.html"
    if not path.exists():
        fail(errors, "tag index was not generated")
        return
    text = path.read_text(encoding="utf-8")
    if "[TAGS]" in text or "md-tag" not in text:
        fail(errors, "tag index did not render the configured tag listing")


def main() -> int:
    """Run all checks and return a shell-friendly status."""

    errors: list[str] = []
    validate_source(errors)
    validate_html(errors)
    validate_locales(errors)
    validate_sitemap(errors)
    validate_tags(errors)
    if errors:
        print("SEO validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("SEO validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
