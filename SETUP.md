# Natasha Website — Setup

Astro rebuild of `https://nylifecoach4u.wixsite.com/nylifecoaching` (Natasha's life-coaching practice).

## Stack

- **Framework:** Astro 5 + TypeScript + Tailwind
- **Content:** Astro content-collections (`src/content/`)
- **Booking + payment:** Cal.com embed (zero backend) — see below
- **Source migration:** `scrape_wix.py` + `extract_wix.py` → `wix_content.json`
- **Output:** static, builds to `dist/`

## Local dev

```bash
cd ~/Documents/natasha_website
npm install
npm run dev           # http://localhost:4321
npm run build         # → dist/
npm run preview       # serve dist/
```

## Booking + payment architecture

No backend. The site uses Cal.com's embed widget (`data-cal-link` buttons + a bootstrap script in `BaseLayout.astro`). Cal.com handles availability, slot selection, payment (via its native Stripe integration), confirmation emails, and Zoom link generation.

**Single source of truth:** `src/data/booking.ts` — Cal username + event slugs + price labels. Change the username in one place.

**Used by:**
- `src/pages/book.astro` — three event-type cards
- `src/pages/services.astro` — embedded CTAs
- `src/pages/contact.astro` — schedule CTA
- `src/components/home/CTABanner.astro` — homepage CTA

## Message to send Natasha (Cal.com setup, one-time, ~10 min)

> Hey! I'm building out your new website and the booking page is ready — it just needs you to set up a free **Cal.com** account so it can show your real availability and take payments. Should take about 10 min:
>
> **1. Sign up at https://cal.com** (free plan is fine).
>    - Pick a username — this becomes your booking URL (e.g. `cal.com/natasha-coaching`).
>    - **Send me the username when you've picked it.**
>
> **2. Create 3 "Event Types"** (Cal.com → Event Types → New):
>
> | Name | URL slug | Length | Price |
> |---|---|---|---|
> | Discovery Call | `discovery-call` | 60 min | Free |
> | Online Coaching | `online-coaching` | 60 min | $70 |
> | Returning Client | `returning-client` | 60 min | $60 |
>
> The URL slug has to match exactly (lowercase, hyphens).
>
> **3. For the two paid ones** (Online Coaching + Returning Client):
>    - Open the event → **Apps** tab → install **Stripe** → connect your Stripe account → enter the price.
>    - (If you don't have a Stripe account yet, it'll walk you through making one — also free, takes ~5 min and needs your bank info for payouts.)
>
> **4. Set your availability:** Cal.com → **Availability** → set your weekly hours.
>
> **5. Add Zoom** so meeting links auto-generate: Cal.com → **Apps** → install **Zoom Video** → connect your Zoom account. Then on each event type → **Location** → pick "Zoom".
>
> That's it — once you send me your username, I'll plug it in and your booking page goes live.

## After Natasha sends her username

1. Edit `src/data/booking.ts`:
   ```ts
   export const CAL_USERNAME = '<her-actual-username>';
   ```
2. `npm run build` → deploy `dist/`.
3. Sanity-check by clicking a button on `/book` — the modal should now load real availability instead of a 404.

## Status

- [x] Astro site scaffolded, all pages rendering
- [x] Cal.com embed wired (bootstrap snippet in `BaseLayout.astro`, config in `src/data/booking.ts`)
- [x] Three event types referenced on book / services / contact / homepage
- [ ] Natasha creates Cal.com account → send username
- [ ] Natasha installs Stripe app on paid events + sets prices
- [ ] Update `CAL_USERNAME` once username received
- [ ] Deploy (no host chosen yet — likely Netlify / Cloudflare Pages / GitHub Pages, since output is static)
- [ ] Initialize git repo (currently no `.git`)
