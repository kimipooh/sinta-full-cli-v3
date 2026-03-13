#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SINTA Journal Metadata CLI

Command-line tool for retrieving journal metadata from the Indonesian
academic database SINTA (Science and Technology Index).

Version 1.1.0 preserves the original 1.0.1 search-result extraction logic
as the basis of discovery and adds an optional detail retrieval mode.

In this adjusted 1.1.0 policy:
- basic mode returns only fields considered stable on the search result page
- detail mode returns enriched fields from journal profile pages
- Google Scholar values are returned as registered in SINTA
"""

__author__ = "Kimiya Kitani"
__copyright__ = "Copyright (c) 2026 Kimiya Kitani"
__license__ = "MIT"
__version__ = "1.1.0"
__status__ = "Research Tool"

import argparse
import csv
import json
import random
import re
import sys
import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://sinta.kemdiktisaintek.go.id"
SEARCH_URL = f"{BASE_URL}/journals"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    )
}

BASIC_FIELDS = [
    "journal_name",
    "sinta_level",
    "affiliation",
    "journal_id",
    "profile_url",
]

DETAIL_FIELDS = [
    "journal_name",
    "sinta_level",
    "affiliation",
    "journal_id",
    "profile_url",
    "p_issn",
    "e_issn",
    "subject_area",
    "website_url",
    "editor_url",
    "garuda_url",
    "google_scholar_url",
]


def polite_sleep(min_sec=1.5, max_sec=3.5):
    time.sleep(random.uniform(min_sec, max_sec))


def polite_sleep_detail(min_sec=3.0, max_sec=6.0):
    time.sleep(random.uniform(min_sec, max_sec))


def fetch_html(session, url, params=None, retries=3, detail=False):
    for attempt in range(retries):
        try:
            if detail:
                polite_sleep_detail()
            else:
                polite_sleep()
            response = session.get(url, params=params, headers=HEADERS, timeout=25)
            if response.status_code in (403, 429):
                time.sleep(random.uniform(10, 30) * (attempt + 1))
                continue
            response.raise_for_status()
            return response.text
        except requests.RequestException:
            if attempt == retries - 1:
                return None
            time.sleep(random.uniform(5, 12) * (attempt + 1))
    return None


def normalize_spaces(text):
    return re.sub(r"\s+", " ", text or "").strip()


def format_sinta_level(value):
    value = normalize_spaces(value)
    if not value or value == "N/A":
        return "N/A"
    value = re.sub(r"(?<=\d)(?=[A-Za-z])", " ", value)
    value = re.sub(r"(?i)^sinta\s*(\d)$", r"Sinta \1", value)
    return value


def extract_stat_value(stats, candidates, default="0"):
    for key in candidates:
        if key in stats:
            return stats[key]
    return default


def parse_search_results(html, affil_filter=None):
    soup = BeautifulSoup(html, "html.parser")
    journals = []
    items = soup.find_all("div", class_="list-item")

    for item in items:
        name_tag = item.find("div", class_="affil-name")
        name = normalize_spaces(name_tag.get_text(" ", strip=True)) if name_tag else "Unknown"

        meta_info = item.find("div", class_="affil-loc")
        meta_text = normalize_spaces(meta_info.get_text(" ", strip=True)) if meta_info else ""
        if affil_filter and affil_filter.lower() not in meta_text.lower():
            continue

        level_tag = item.find("span", class_="num-stat")
        level = format_sinta_level(level_tag.get_text(" ", strip=True)) if level_tag else "N/A"

        p_issn_match = re.search(r"P-ISSN\s*:\s*([0-9Xx-]+)", meta_text, re.IGNORECASE)
        e_issn_match = re.search(r"E-ISSN\s*:\s*([0-9Xx-]+)", meta_text, re.IGNORECASE)
        p_issn = p_issn_match.group(1).upper() if p_issn_match else "N/A"
        e_issn = e_issn_match.group(1).upper() if e_issn_match else "N/A"

        stats = {}
        stat_items = item.find_all("div", class_="stat-item")
        for stat_item in stat_items:
            label_tag = stat_item.find("div", class_="stat-label")
            num_tag = stat_item.find("div", class_="stat-num")
            if label_tag and num_tag:
                stats[normalize_spaces(label_tag.get_text(" ", strip=True))] = normalize_spaces(num_tag.get_text(" ", strip=True))

        profile_url = "N/A"
        journal_id = "N/A"
        for link in item.find_all("a", href=True):
            href = link["href"]
            if "/journals/profile/" in href or "/journals/detail?id=" in href:
                profile_url = urljoin(BASE_URL, href)
                m = re.search(r"/journals/profile/(\d+)|[?&]id=(\d+)", profile_url)
                if m:
                    journal_id = m.group(1) or m.group(2)
                break

        journals.append({
            # original/internal discovery fields
            "journal_name": name,
            "sinta_level": level,
            "p_issn": p_issn,
            "e_issn": e_issn,
            "affiliation": normalize_spaces(meta_text.split("|")[0]) if "|" in meta_text else meta_text,
            "sinta_score_3y": extract_stat_value(stats, ["SINTA Score 3Yr"], "0"),
            "sinta_score_overall": extract_stat_value(stats, ["SINTA Score Overall"], "0"),
            "h_index_google": extract_stat_value(stats, ["H-Index Google Scholar", "H Index Google Scholar"], "0"),
            "h_index_sinta": extract_stat_value(stats, ["H-Index Sinta", "H Index Sinta"], "0"),
            "citations_google": extract_stat_value(stats, ["Citations Google Scholar", "Citation Google Scholar"], "0"),
            "citations_sinta": extract_stat_value(stats, ["Citations Sinta", "Citation Sinta"], "0"),
            # 1.1.0 additions/internal status
            "journal_id": journal_id,
            "profile_url": profile_url,
            "fetch_mode": "basic",
            "detail_fetched": "no",
            "source_page_type": "search",
            "parse_status": "search_only",
            "subject_area": "N/A",
            "website_url": "N/A",
            "editor_url": "N/A",
            "garuda_url": "N/A",
            "google_scholar_url": "N/A",
            "current_accreditation": "N/A",
            "impact": "N/A",
            "i10_index_google": "N/A",
            "citations_google_since_2021": "N/A",
            "h_index_google_since_2021": "N/A",
            "i10_index_google_since_2021": "N/A",
            "accreditation_history": "N/A",
        })

    return journals


def regex_after_label(text, label, pattern):
    m = re.search(rf"{re.escape(label)}\s*:\s*{pattern}", text, re.IGNORECASE)
    return normalize_spaces(m.group(1)) if m else None


def regex_before_label(text, label, pattern):
    m = re.search(rf"{pattern}\s+{re.escape(label)}", text, re.IGNORECASE)
    return normalize_spaces(m.group(1)) if m else None


def parse_detail_page(html, record):
    soup = BeautifulSoup(html, "html.parser")
    text = normalize_spaces(soup.get_text(" ", strip=True))

    # ISSN with X support
    p_issn = regex_after_label(text, "P-ISSN", r"([0-9Xx-]+)")
    e_issn = regex_after_label(text, "E-ISSN", r"([0-9Xx-]+)")
    if p_issn:
        record["p_issn"] = p_issn.upper()
    if e_issn:
        record["e_issn"] = e_issn.upper()

    subject_area = regex_after_label(
        text,
        "Subject Area",
        r"(.+?)(?=\s+(?:\d+[.,]?\d*\s+Impact|Impact|Google Citations|Sinta\s*\d|Current Acreditation|Google Scholar|Garuda|Website|Editor URL|History Accreditation|$))"
    )
    if subject_area:
        record["subject_area"] = subject_area.rstrip(".,;")

    current_acc = regex_before_label(text, "Current Acreditation", r"([A-Za-z]+\s*\d+)")
    if current_acc:
        record["current_accreditation"] = format_sinta_level(current_acc)

    impact = regex_before_label(text, "Impact", r"([\d.,]+)")
    if impact:
        record["impact"] = impact

    citations_google = regex_before_label(text, "Google Citations", r"([\d.,]+)")
    if citations_google:
        record["citations_google"] = citations_google.replace(",", "")

    # SINTA page summary block: Citation 1859 817 h-index 19 11 i10-index 59 15
    m = re.search(
        r"Citation\s+([\d.,]+)\s+([\d.,]+)\s+h-index\s+([\d.,]+)\s+([\d.,]+)\s+i10-index\s+([\d.,]+)\s+([\d.,]+)",
        text,
        re.IGNORECASE,
    )
    if m:
        record["citations_google"] = m.group(1).replace(",", "")
        record["citations_google_since_2021"] = m.group(2).replace(",", "")
        record["h_index_google"] = m.group(3).replace(",", "")
        record["h_index_google_since_2021"] = m.group(4).replace(",", "")
        record["i10_index_google"] = m.group(5).replace(",", "")
        record["i10_index_google_since_2021"] = m.group(6).replace(",", "")

    # link harvesting from visible labels or href targets
    for a in soup.find_all("a", href=True):
        label = normalize_spaces(a.get_text(" ", strip=True)).lower()
        href = a["href"].strip()
        if not href:
            continue
        full_href = urljoin(BASE_URL, href)

        if "garuda" in label and record["garuda_url"] == "N/A":
            record["garuda_url"] = full_href
        elif "website" in label and record["website_url"] == "N/A":
            record["website_url"] = full_href
        elif "editor" in label and record["editor_url"] == "N/A":
            record["editor_url"] = full_href
        elif "google scholar" in label and record["google_scholar_url"] == "N/A":
            # return the SINTA-registered value as-is. When the link is just #! on the
            # profile page, keep the profile-page value with #! rather than guessing.
            if href in {"#!", "#", ""} and record.get("profile_url") not in (None, "", "N/A"):
                record["google_scholar_url"] = record["profile_url"] + "#!"
            else:
                record["google_scholar_url"] = full_href

    if record["google_scholar_url"] == "N/A" and record.get("profile_url") not in (None, "", "N/A"):
        # fallback aligned with the current project decision: if the page exposes only
        # the SINTA-registered placeholder for Google Scholar, return profile_url + #!
        if "Google Scholar" in text:
            record["google_scholar_url"] = record["profile_url"] + "#!"

    years = re.findall(r"\b(20\d{2})\b", text)
    if years:
        uniq = []
        for y in years:
            if y not in uniq:
                uniq.append(y)
        if len(uniq) >= 2:
            record["accreditation_history"] = ", ".join(uniq)

    record["detail_fetched"] = "yes"
    record["fetch_mode"] = "detail"
    record["source_page_type"] = "search+detail"
    record["parse_status"] = "detail_ok"
    return record


def project_record(record, fetch_mode):
    fields = BASIC_FIELDS if fetch_mode == "basic" else DETAIL_FIELDS
    return {k: record.get(k, "N/A") for k in fields}


def search_sinta_journal(keyword, search_type=1, affil_filter=None, fetch_mode="basic"):
    session = requests.Session()
    html = fetch_html(session, SEARCH_URL, params={"q": keyword, "search": search_type}, detail=False)
    if not html:
        print("Error: failed to retrieve SINTA search results", file=sys.stderr)
        return []

    journals = parse_search_results(html, affil_filter=affil_filter)

    if fetch_mode == "detail":
        for record in journals:
            profile_url = record.get("profile_url")
            if not profile_url or profile_url == "N/A":
                record["detail_fetched"] = "error"
                record["parse_status"] = "detail_skipped_no_profile_url"
                continue
            detail_html = fetch_html(session, profile_url, detail=True)
            if not detail_html:
                record["detail_fetched"] = "error"
                record["fetch_mode"] = "detail"
                record["parse_status"] = "detail_fetch_failed"
                continue
            parse_detail_page(detail_html, record)

    return [project_record(r, fetch_mode) for r in journals]


def main():
    parser = argparse.ArgumentParser(description="SINTA Journal Metadata CLI")
    parser.add_argument("-q", "--query", required=True, help="Search keyword")
    parser.add_argument("-m", "--mode", choices=["title", "all"], default="title",
                        help="Search scope on the SINTA search page")
    parser.add_argument("-a", "--affil", help="Affiliation filter")
    parser.add_argument("-f", "--format", choices=["csv", "json"], default="json")
    parser.add_argument("--fetch-mode", choices=["basic", "detail"], default="basic",
                        help="Retrieval mode: basic (search only) or detail (search + profile pages)")

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()
    results = search_sinta_journal(
        args.query,
        1 if args.mode == "title" else 0,
        args.affil,
        args.fetch_mode,
    )

    if not results:
        sys.exit(0)

    if args.format == "json":
        print(json.dumps(results, indent=4, ensure_ascii=False))
    elif args.format == "csv":
        fieldnames = list(results[0].keys())
        writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    main()
