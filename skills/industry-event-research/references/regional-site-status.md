# Regional Exhibition Website Reliability

Known status of regional exhibition organizer websites. Use this to set expectations when fetching dates and information.

## Generally Reliable Sources

| Source | Status | Notes |
|--------|--------|-------|
| Koelnmesse (ism-cologne.com, anuga.com) | ✅ Excellent | Full dates, JSON-LD structured data, reliable |
| Gulfood (gulfood.com) | ✅ Excellent | Official site, clear dates, extensive data |
| Foodex Japan (foodex.jma.or.jp) | ✅ Good | Official JMA site, reliable English content |
| TradeFairDates.com | ✅ Good | Aggregator, cross-references official sources |
| Eventseye.com | ✅ Good | Reliable dates and venue info |
| Showsbee.com | ✅ Good | Aggregator, mostly accurate |
| Cantonfair.net | ✅ Good | Chinese events |

---

## Unreliable / Problematic Sources

| Source | Status | Issues | Workaround |
|--------|--------|--------|------------|
| sweetexpo.ru | ❌ Blocked | Returns empty body or Cloudflare challenge | Check alternate sources |
| worldfoodmoscow.com | ❌ Blocked | Private/internal network detection | Use aggregator sites |
| foodexpo.ru | ❌ Blocked | Same issue | Use aggregator sites |
| interfood.uz | ❌ Blocked | Uzbekistan site often blocked | Search via TradeFairDates |
| confectioneryexpo.com | ❌ Blocked | Unresponsive | Check alternative |
| foodingredients.ru | ❌ Blocked | Russian domain issues | Use aggregator sites |
| Food Week Korea (foodweek.co.kr) | ⚠️ Partial | Korean site, limited English content | Cross-reference with showsbee.com |

---

## Aggregators as Fallbacks

When primary sites fail, use these aggregators:

- **TradeFairDates.com** — global database, cross-references official sources
- **Showsbee.com** — good for Asian and Middle Eastern events
- **Eventseye.com** — reliable for international exhibitions
- **ExpoTobi.com** — regional focus, good for Asia/Korea
- **FindInfoFood.com** — food-specific events globally
- **Cantonfair.net** — China-focused events

---

## Search Strategy Tips

1. **Primary first**: Try official site with `curl -sL --max-time 15`
2. **Date extraction**: Look for `<span class="date">`, `data-begin-date`, or JSON-LD `startDate`/`endDate`
3. **Fallback to aggregators**: When official site fails, search `"<event name> 2027 dates"`
4. **Cross-reference**: If multiple sources agree, confidence is high
5. **Last resort**: Contact organizer directly via email or LinkedIn

---

## Known Date Patterns

| Event | Typical Month | Confirmed Dates (Recent) |
|-------|---------------|--------------------------|
| ISM Cologne | Late Jan/Early Feb | 31.01–03.02.2027 |
| Gulfood Dubai | February/March | 15–19 March 2027 |
| Anuga FoodTec | February | 23–26 Feb 2027 |
| Foodex Japan | March | 9–12 March 2027 |
| Sweets & Snacks Expo | May (moved from June) | 18–20 May 2027 |
| SIAL China Shanghai | May | 18–20 May 2027 |
| FIC China | March | 17–19 March 2026 (past), TBD 2027 |
