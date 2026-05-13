/**
 * Booking + payment configuration.
 *
 * SETUP (one-time, done by Natasha — no code changes needed after):
 *
 * 1. Create a Cal.com account at https://cal.com → pick a username.
 *    Update `CAL_USERNAME` below to match (e.g. "natasha-coaching").
 *
 * 2. In Cal.com, create three Event Types with these URL slugs
 *    (matching the `slug` fields below):
 *      - discovery-call    — 60 min, free
 *      - online-coaching   — 60 min, $70
 *      - returning-client  — 60 min, $60
 *
 * 3. For each PAID event type:
 *      Cal.com → Event Type → Apps → install "Stripe" →
 *      connect Stripe account → set price + currency.
 *    The Discovery Call stays free (no Stripe app needed).
 *
 * 4. Set availability under Cal.com → Availability.
 *    Add Zoom under Cal.com → Apps → "Zoom Video" so the meeting
 *    link is auto-included in confirmation emails.
 *
 * Once the username + slugs match, the embedded booking modal on the
 * site will show Natasha's real availability and collect payment via
 * Stripe before confirming the slot. No backend on our side.
 */

export const CAL_USERNAME = 'tashcoach';

export type EventKey = 'discovery' | 'coaching' | 'returning';

export const calEvents: Record<EventKey, { slug: string; priceLabel: string; durationMin: number }> = {
  discovery: { slug: 'discovery-call',   priceLabel: 'Free', durationMin: 60 },
  coaching:  { slug: 'online-coaching',  priceLabel: '$70',  durationMin: 60 },
  returning: { slug: 'returning-client', priceLabel: '$60',  durationMin: 60 },
};

export const calLink = (key: EventKey) => `${CAL_USERNAME}/${calEvents[key].slug}`;
