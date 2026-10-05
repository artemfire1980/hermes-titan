# Venue Calendar CSS/Regex Selectors

Selectors for extracting event data from major exhibition venue websites.

## Koelnmesse (koelnmesse.com)

### Date Extraction
```
<span class=\"date\">DD.MM. – DD.MM.YYYY, City</span>
```
**Pattern:** `data-begin-date="YYYY-MM-DD"` + `<span class="date">`

### Event Name
```
<strong class="sort_fairname">Event Name</strong>
```

### Filter Parameters
- Branch filter: `branche=Sweets+and+Snacks` or `branche=Food`
- URL pattern: `https://www.koelnmesse.com/current-dates/all-trade-fairs/?branche=Food`

### JSON-LD Structured Data
```json
{
  "startDate": "2027-10-09",
  "endDate": "2027-10-13"
}
```

---

## ISM Cologne (ism-cologne.com)

All four sub-events share the same dates:
- ISM (main)
- ISM Ingredients
- ISM Manufacturing
- ISM Snacks & Sweets

**Date selector:**
```
<span class="date">31.01&ndash;03.02.2027</span>
```
Note: uses HTML entity `&ndash;` for en-dash.

---

## Gulfood (gulfood.com)

### Image-based Date Info
```
alt="Gulfood - 15 to 19 March 2027 at Dubai World Trade Center"
```

### Meta Description
```
<meta name="description" content="Join Gulfood 2027...">
```

---

## Foodex Japan (foodex.jma.or.jp)

### Title Tag
```
<title>FOODEX JAPAN 2027 "The 52th International Food and Beverage Exhibition"</title>
```

### Meta Description
```
<meta name="description" content="It will take place from Mar.9 to 12, 2027 at Tokyo Big Sight, Tokyo, Japan.">
```

---

## Aggregator Sites

### TradeFairDates.com
- Uses slug format: `/ExhibitionName-M1234/City.html`
- Reliable cross-reference source

### Showsbee.com
- Format: `/fairs/12345-Event-Name.html`
- Good for Asian events

### Eventseye.com
- Format: `/fairs/f-event-name-123-1.html`
- Often has more detailed info

---

## Date Normalization

Convert all formats to: `DD.MM – DD.MM.YYYY`

Examples:
- `31.01–03.02.2027` → `31.01 – 03.02.2027`
- `March 9-12, 2027` → `09.03 – 12.03.2027`
- `2027-03-09` → `09.03.2027`
