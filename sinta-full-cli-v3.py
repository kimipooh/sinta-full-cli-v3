#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SINTA 3 Journal Metadata CLI

Command-line tool for retrieving journal metadata from the Indonesian
academic database SINTA (Science and Technology Index).

This tool extracts journal metadata including SINTA rank, ISSN,
citation counts, and H-index values from the current SINTA 3 journal
search interface.

Author:
    Kimiya Kitani
    Center for Southeast Asian Studies
    Kyoto University

Project:
    https://github.com/kimipooh/sinta-full-cli-v3

License:
    MIT License

Copyright (c) 2026 Kimiya Kitani

If you use this tool in academic research, citation of the repository
or Zenodo DOI is appreciated.
"""

__author__ = "Kimiya Kitani"
__copyright__ = "Copyright (c) 2026 Kimiya Kitani"
__license__ = "MIT"
__version__ = "1.0.0"
__status__ = "Research Tool"

import argparse
import csv
import json
import random
import re
import sys
import time

import requests
from bs4 import BeautifulSoup


def search_sinta_journal_max(keyword, search_type=1, affil_filter=None):
    """
    Max Metadata Scraper for SINTA 3 (2026).
    Extracts ISSNs, scores, h-index, and citations.
    """
    base_url = "https://sinta.kemdiktisaintek.go.id/journals"
    params = {"q": keyword, "search": search_type}
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        )
    }

    try:
        # Rate limiting to prevent IP ban
        time.sleep(random.uniform(1.5, 3.5))
        response = requests.get(base_url, params=params, headers=headers, timeout=25)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        journals = []

        items = soup.find_all("div", class_="list-item")

        for item in items:
            # Basic Info
            name_tag = item.find("div", class_="affil-name")
            name = name_tag.text.strip() if name_tag else "Unknown"

            meta_info = item.find("div", class_="affil-loc")
            meta_text = meta_info.get_text(strip=True, separator=" ") if meta_info else ""

            # Filtering by affiliation (case-insensitive)
            if affil_filter and affil_filter.lower() not in meta_text.lower():
                continue

            # Level (S1-S6)
            level_tag = item.find("span", class_="num-stat")
            level = level_tag.text.strip() if level_tag else "N/A"

            # ISSN extraction using regex
            p_issn_match = re.search(r"P-ISSN\s*:\s*([\d-]+)", meta_text, re.IGNORECASE)
            e_issn_match = re.search(r"E-ISSN\s*:\s*([\d-]+)", meta_text, re.IGNORECASE)

            p_issn = p_issn_match.group(1) if p_issn_match else "N/A"
            e_issn = e_issn_match.group(1) if e_issn_match else "N/A"

            # Stats parsing
            stats = {}
            stat_items = item.find_all("div", class_="stat-item")
            for stat_item in stat_items:
                label_tag = stat_item.find("div", class_="stat-label")
                num_tag = stat_item.find("div", class_="stat-num")
                if label_tag and num_tag:
                    stats[label_tag.text.strip()] = num_tag.text.strip()

            journals.append(
                {
                    "journal_name": name,
                    "sinta_level": level,
                    "p_issn": p_issn,
                    "e_issn": e_issn,
                    "affiliation": meta_text.split("|")[0].strip() if "|" in meta_text else meta_text,
                    "sinta_score_3y": stats.get("SINTA Score 3Yr", "0"),
                    "sinta_score_overall": stats.get("SINTA Score Overall", "0"),
                    "h_index_google": stats.get("H-Index Google Scholar", "0"),
                    "h_index_sinta": stats.get("H-Index Sinta", "0"),
                    "citations_google": stats.get("Citations Google Scholar", "0"),
                    "citations_sinta": stats.get("Citations Sinta", "0"),
                }
            )

        return journals

    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return []


def main():
    parser = argparse.ArgumentParser(description="SINTA 3 Max Metadata CLI")
    parser.add_argument("-q", "--query", required=True, help="Search keyword")
    parser.add_argument("-m", "--mode", choices=["title", "all"], default="title")
    parser.add_argument("-a", "--affil", help="Affiliation filter")
    parser.add_argument("-f", "--format", choices=["csv", "json"], default="json")

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()
    results = search_sinta_journal_max(
        args.query, 1 if args.mode == "title" else 0, args.affil
    )

    if not results:
        sys.exit(0)

    if args.format == "json":
        print(json.dumps(results, indent=4, ensure_ascii=False))
    elif args.format == "csv":
        writer = csv.DictWriter(sys.stdout, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    main()
