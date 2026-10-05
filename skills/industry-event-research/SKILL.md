---
name: industry-event-research
description: Find industry exhibitions and trade fairs by sector, date — with B2B assessment and priority classification.
category: research
version: 2.0.0
author: hermes-agent
license: MIT
metadata:
  hermes:
    tags:
      - research
      - events
      - trade-fairs
      - industry
      - B2B
      - confectionery
    related_skills:
      - web-search
---

## When to Use

Use when the user needs to find industry exhibitions, trade fairs, or conferences for a specific sector (e.g., confectionery, food technology, packaging) within a date range — especially for B2B decision-making.

Returns structured results with period, name, topic, country, priority classification, and commercial assessment.

**Prerequisite:** Verify search engines are working before starting. If SearXNG returns no results and web_search is empty, the search infrastructure may be broken (DuckDuckGo CAPTCHA, disabled engines). Report this upfront rather than looping.

## Procedure

1. **Clarify scope** — confirm sector (e.g., confectionery, food tech, packaging), date window, geographic focus, and purpose (exhibit vs. visit).
2. **Check major venue calendars first** — they aggregate multiple events and have reliable dates:
   - `https://www.koelnmesse.com/current-dates/all-trade-fairs/` (filter by branch: Food, Sweets and Snacks, FoodTechnology)
   - `https://www.ism-cologne.com/` (ISM, ISM Ingredients, ISM Manufacturing, ISM Snacks & Sweets — all share dates)
   - `https://www.anuga.com/` (Anuga, Anuga FoodTec)
   - `https://www.sweetsandsnacks.com/` (Sweets & Snacks Expo)
3. **Query venue sites directly** — use `curl` + grep for date patterns (`2026`, `2027`, `october`, `november`, etc.) and event names (`<strong class="sort_fairname">`).
4. **Check sector-specific sites** — but expect many to be empty, blocked, or only show next edition:
   - Confectionery: sweetexpo.ru, worldfoodmoscow.com, interfood.uz, confectioneryexpo.com
   - Ingredients: foodingredients.ru, fi-europe.com
5. **Cross-reference** — if a venue calendar lists an event, verify on the event's own site for exact dates and topic scope.
6. **Fallback to aggregators** when primary sources fail:
   - TradeFairDates.com, Showsbee.com, Eventseye.com, FindInfoFood.com
7. **Assess each event** against priority framework (see references/priority-classification.md).
8. **Compile final report** with tables organized by Priority A/B/C/Not Recommended, plus statistics summary.

### Reporting Standards

- Save full report to `/mnt/ai-ssd/hermes/cache/scratch/exhibitions_report_<period>.md`
- Include: detailed analysis per event, statistics, key conclusions, recommendations
- Always separate confirmed facts from assumptions
- Never fabricate dates or data — if unavailable, mark as "Даты требуют подтверждения" (dates require confirmation)

## Key Sources & Patterns

- **Koelnmesse calendar** returns `<span class="date">DD.MM. – DD.MM.YYYY, City</span>` and `<strong class="sort_fairname">Event Name</strong>`. Filter by `branche=Sweets+and+Snacks` or `branche=Food`.
- **ISM Cologne** — all four sub-events run simultaneously. Date in meta `startDate`/`endDate` and `<span class="date">31.01–03.02.2027</span>`.
- **Anuga** — `"startDate": "2027-10-09"`, `"endDate": "2027-10-13"` in JSON-LD; `<span class="date">09.–13.10.2027</span>`.
- **Sweets & Snacks Expo** — `"startDate": "2027-05-18"`, `"endDate": "2027-05-20"` in og:description.
- **Gulfood** — official site shows dates clearly; third-party sites may vary.
- **Russian sites** (sweetexpo.ru, worldfoodmoscow.com, etc.) often return empty or blocked responses — note this limitation.

## Pitfalls

- **Venue calendars list everything** — filter by branch/sector before reading; otherwise you parse hundreds of irrelevant events.
- **Sub-events share dates** — ISM's four tracks are one physical event; report as one entry with combined topic or note the split.
- **Next-edition bias** — most event sites only publish the upcoming edition; historical or past dates are removed. If the window spans two editions, you may only get the later one.
- **Russian/regional sites unreliable** — many return 200 with empty body or Cloudflare challenges. Treat "no data" as "check organizer directly", not "event doesn't exist". Use proper User-Agent and Accept-Language headers. If curl fails, try browser_navigate or archive.today.
- **Date format variance** — DD.MM.YYYY vs YYYY-MM-DD vs month names. Normalize to DD.MM – DD.MM.YYYY for output.
- **Timezone/locale** — Koelnmesse uses German locale (dd.MM.), Anuga uses ISO in JSON-LD. Parse both.
- **Aggregator conflicts** — different sites may show slightly different dates; prefer official source or note discrepancy.
- **Do not confuse construction/logistics expos with food expos** — Big 5 Dubai is construction; Big 5 Gourmet is separate.
- **Never assume Russia/Belarus absence from incomplete exhibitor lists** — mark as "подтверждено"/"не обнаружено в проверенных источниках"/"данных недостаточно".
- **GitHub search pattern for event research**: When official event sites are blocked or unreliable, use `web_search` with `site:` operator to find announcements from third-party sources. Filter by `sort=stars` for popular repositories if looking for software tools related to the event.

## References

- `references/venue-calendar-selectors.md` — CSS/regex selectors for major venue sites
- `references/sector-keywords.md` — search terms by industry (confectionery, food-tech, packaging, etc.)
- `references/priority-classification.md` — event assessment framework (Priority A/B/C/Not Recommended)
- `references/regional-site-status.md` — known reliability of regional exhibition websites
