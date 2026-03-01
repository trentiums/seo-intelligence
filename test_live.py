"""Live test -- run SEO tools against a real website."""

import asyncio
import sys
import os

# Force UTF-8 output
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from crawler import crawl_page, parse_page, format_page_analysis
from analyzer import calculate_seo_score, find_quick_wins, format_seo_score, format_quick_wins


# Test against a well-known site
TEST_URL = "https://www.python.org/"


async def main():
    print("=" * 70)
    print("SEO INTELLIGENCE PLUGIN -- LIVE TEST")
    print("=" * 70)
    print()

    # ---- Test 1: Crawl & Analyze ----
    print("[TEST 1] Crawling and analyzing page...")
    print(f"   URL: {TEST_URL}")
    print()

    try:
        html = await crawl_page(TEST_URL)
        print(f"   [OK] Fetched {len(html):,} bytes of HTML")
    except Exception as e:
        print(f"   [FAIL] Crawl failed: {e}")
        return

    analysis = parse_page(html, TEST_URL)

    # Print raw analysis
    report = format_page_analysis(analysis)
    print()
    print(report)
    print()

    # ---- Test 2: SEO Score ----
    print("=" * 70)
    print("[TEST 2] Calculating SEO Score...")
    print()

    score = calculate_seo_score(analysis)
    score_report = format_seo_score(score, TEST_URL)
    print(score_report)
    print()

    # ---- Test 3: Quick Wins ----
    print("=" * 70)
    print("[TEST 3] Finding Quick Wins...")
    print()

    wins = find_quick_wins(analysis)
    if wins:
        wins_report = format_quick_wins(wins, TEST_URL)
        print(wins_report)
    else:
        print("   [OK] No quick wins -- page covers all the basics!")
    print()

    # ---- Summary ----
    print("=" * 70)
    print("[RESULT] LIVE TEST COMPLETE")
    print(f"   Page: {TEST_URL}")
    print(f"   Title: {analysis.title}")
    print(f"   Word count: {analysis.word_count}")
    print(f"   SEO Score: {score.overall}/100")
    print(f"   Headings: {analysis.h1_count} H1, {analysis.h2_count} H2, {analysis.h3_count} H3")
    print(f"   Links: {analysis.internal_link_count} internal, {analysis.external_link_count} external")
    print(f"   Images: {analysis.total_images} ({analysis.images_with_alt} with alt)")
    print(f"   FAQ: {'Yes' if analysis.has_faq_section else 'No'}")
    print(f"   Schema: {', '.join(analysis.schema_types) if analysis.schema_types else 'None'}")
    print(f"   Quick wins: {len(wins)}")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
