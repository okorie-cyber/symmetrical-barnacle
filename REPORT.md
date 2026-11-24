# Report #1: Opportunity Assessment and Launch Plan

Date: 24 November 2026
Status: Phase 1 (Discovery) and Phase 2 (Selection) done. Phase 3 (Validation) and Phase 4 (Build) started.

> **Corrections (24 Nov 2026, Report #2):** three claims below were overstated and one was missing.
> - The 45% figure means "used AI for a local recommendation in the past 12 months".
> - In the same BrightLocal survey, 65% of owners say they're already working on AI visibility.
> - The call-answering statistics are unverified and have been removed from sales material.
> - Google's map pack, not AI Overviews, still appears on most "[service] [city]" searches.
> - The audit tool no longer relies on Claude alone.
>
> See `docs/market-verification.md`, `docs/technical-verification.md` and `docs/offer.md`. Where they conflict with this report, they win.

> Nothing here is a guaranteed result. Every revenue figure below is a target built on stated assumptions. **Revenue is not profit, profit is not cash in hand, and cash in hand is not personal wealth.** We have $0 in revenue today.

---

## 0. Starting position (the constraints that shape every recommendation)

| Factor | Reality | What it means |
|---|---|---|
| Location | Lagos, Nigeria | Sell to US/UK/EU buyers for hard-currency pricing. Lagos (WAT) overlaps UK business hours fully and US East Coast mornings. |
| Payments | No native Stripe. PayPal receiving works through the Paga partnership (launched Jan 2026), but early users reported account restrictions. | Main rail: **Grey or Raenest USD account** (ACH, about 0.8% fee) for direct invoices, plus **Payoneer** for Fiverr/Upwork payouts. PayPal stays a backup, not a primary rail. Stripe Atlas ($500 plus US tax filings, including Form 5472 with a $25k penalty for missing it) waits until revenue justifies it. |
| Capital | Close to zero | Only businesses with under $100 to start qualify. |
| Skills | Software development plus AI tools | Build the product ourselves. Engineering time is our cheapest input. |
| Time | You are a full-time student (UNILAG) | The plan assumes 15 to 25 hours a week. Anything that needs live phone sales during US hours ranks lower. |

---

## 1. The 10 opportunities, ranked

Scores run 1 to 5 (5 is best). "Speed" means speed to the first $1,000.

| # | Opportunity | Demand | Margin | Capital | Speed | Scale | Competition (5 = light) | **Total** |
|---|---|---|---|---|---|---|---|---|
| 1 | **AI Search Visibility audit + fix for local service businesses** (done-for-you GEO) | 5 | 5 | 5 | 4 | 4 | 3 | **26** |
| 2 | Productized AI front office for one trade (missed-call text-back, quote follow-up, review requests) | 5 | 4 | 4 | 3 | 4 | 2 | **22** |
| 3 | Packaged n8n / AI-agent gigs on Fiverr and Upwork | 4 | 4 | 5 | 5 | 2 | 2 | **22** |
| 4 | Vertical micro-SaaS: quote/estimate + follow-up for one trade (photo/voice note to quote) | 4 | 5 | 4 | 2 | 5 | 4 | **24*** |
| 5 | Plain-English website accessibility (WCAG) scanner + fix list for SMBs | 3 | 5 | 5 | 3 | 4 | 3 | **23** |
| 6 | AI review response + review generation for local businesses | 4 | 4 | 5 | 3 | 3 | 2 | **21** |
| 7 | AI document processing for bookkeepers and accounting firms (invoices to ledger) | 4 | 4 | 4 | 2 | 4 | 3 | **21** |
| 8 | AI grant-writing assistant for nonprofits and NGOs | 3 | 4 | 5 | 2 | 3 | 4 | **21** |
| 9 | WhatsApp AI sales agents for Nigerian SMEs | 4 | 3 | 5 | 4 | 3 | 3 | **22** |
| 10 | Programmatic-SEO micro-tools (niche document generators, e.g. superbills, SEO contracts) | 3 | 5 | 5 | 1 | 3 | 4 | **21** |

\*#4 scores well on paper but is slow to first revenue and needs deep trade knowledge we don't have yet. **It is the natural Phase 7 product once #1 gives us 30+ trade clients to learn from.**

---

## 2. Evidence of real demand (sources checked November 2026)

**Consumers have moved to AI for local recommendations. Businesses haven't caught up.**
- 45% of consumers now use AI tools for local business recommendations, up from 6% a year earlier (BrightLocal Local Consumer Review Survey, Mar 2026).
- Only 20% of 2,862 small businesses in Austin, Denver, Nashville and Phoenix appeared in ChatGPT, Perplexity or Google AI answers to typical customer questions. 64% of those that did appear showed up in only one tool (Mandalytics, Nov 2026).
- 46% of SMB owners haven't checked, or don't know, whether AI recommends them (BrightLocal, Oct 2026).
- The answers are still up for grabs. The top business takes only about 25% of AI mentions in a market, and 68% of markets had a new #1 when re-measured about 127 days later (MentionedOn, 881 markets, Jun to Nov 2026).
- Being named tracks with things we can improve. Businesses AI found had a median of 349 Google reviews against 88 for the rest. Google Business Profiles were cited in 57% of local AI Overviews, and cost/how-to questions triggered AI Overviews 97% of the time (Mandalytics; Make It Loud Atlanta study, Nov 2026).

**Buyers already pay for the adjacent services.**
- Published small-business automation retainers run $250 to $1,500 a month. First builds run $1,500 to $7,500 (Nova Solutions, Data Prism, LinkTech and Retailbox pricing pages, Oct to Nov 2026).
- Indie AI-visibility products report real revenue: SEO STACK at $25.7k MRR, ReddGrow AI at $13.8k a month (DirectoryGems, Aug 2026). The space is filling, so we enter through one vertical and done-for-you service, not a generic dashboard.
- On Fiverr, a search for done-for-you AI-search visibility returned specialists with as few as 2 completed orders. Supply of proven sellers is thin.

**Front-office automation (#2) has measured pain.**
- 48% of home-services calls are not answered by a person (Invoca, 70M calls). Up to 85% of unanswered callers never call back (CallRail).
- Self-serve AI receptionists sell for $29 to $349 a month, so **reselling a receptionist adds little**. The open ground is quote follow-up and integration work (Krajewski, *Missed Calls and Unanswered Leads*, Oct 2026).

**The freelance market (#3) is real, but it's a barbell.**
- Upwork had 3,324 "AI automation" postings in May 2026, with a $30/hr median and a $150 median fixed budget. n8n was tagged on 16% of them, ahead of Zapier (Upwatcher). The money sits in the $1k to $5k fixed projects. The median job is cheap.

---

## 3 to 7. Detail on the top candidates

| | #1 AI Visibility | #2 AI Front Office | #3 Freelance gigs |
|---|---|---|---|
| **Startup capital** | $15 to $60 (domain, sending mailbox, about $1 to $2 of API cost per audit) | $50 to $150 (Twilio number, tool trials) | $0 |
| **Time to first revenue** | 3 to 6 weeks (cold email warm-up takes 2 to 4 weeks) | 4 to 8 weeks | 1 to 4 weeks (first gig orders) |
| **Gross margin** | 80 to 90% (labour is the main cost) | 60 to 75% (telephony and SaaS costs) | 85 to 95% |
| **Competition / risk** | Category heating up (BrightLocal and others ship trackers). AI answers are unstable. A causal link to bookings is not yet proven. **Mitigation:** sell "get found + get reviewed + get booked" measured in calls, never guaranteed rankings. | Crowded with $29/mo self-serve tools. Integration breakage. Phone/SMS rules (TCPA, A2P 10DLC registration in the US). | Price race to the bottom. Platform fees (Fiverr takes 20%). Account risk. Doesn't build an asset. |
| **Automation potential** | High. The audit is fully automated (built today). Fixes are templated. Monthly re-audits run on a schedule. | Medium to high | Low. You are trading time. |
| **Recurring revenue** | Yes, monthly retainer plus re-audits | Yes | Rarely |

---

## 8. Top three recommendations

1. **AI Visibility audit + fix (#1).** The best risk-to-reward. A free, personalised audit is the most compelling cold-outreach hook available to us: *"ChatGPT recommends these 3 competitors when someone asks for a plumber in Austin. It doesn't mention you."* That message is specific, checkable and costs about $1 to produce.
2. **AI front office (#2) as the upsell, not a separate business.** Once a client trusts us with visibility, review-request automation and quote follow-up become add-ons on the same retainer.
3. **Fiverr/Upwork gigs (#3) as the short-term cash engine**, scoped tightly: an "AI Visibility Audit + action plan" gig and an "n8n lead follow-up automation" gig. They bring in early cash, reviews and case studies while cold email warms up.

## 9. The single business to start

**A productized "Get Found by AI" service for US home-service businesses, starting with one trade (recommendation: roofers or HVAC, where jobs are high-ticket and AI-answer competition is moderate).**

- **Free:** AI Visibility Audit (automated, sent as a personalised report).
- **$497 one-time:** Fix Sprint. Google Business Profile overhaul, 2 local cost pages, directory cleanup, schema markup, a review-request system.
- **$297 a month:** Found & Booked retainer. Monthly re-audit across engines, 1 new local content page, review automation, a competitor watch and a one-page results report.
- **Later ($99 to $199 a month add-on):** quote follow-up / missed-call text-back (opportunity #2).

Why it wins on our constraints: it needs no capital, sells in USD, runs async over email (no live calls during US hours needed), uses our engineering edge, and turns into software (a self-serve tracker at $49 to $99 a month) once the service is proven.

Unit economics at target (an estimate, not a forecast): average client = $497 setup + $297 × 9 months average lifetime ≈ **$3,170 lifetime value**. Delivery cost ≈ 3 to 4 hours a month plus about $15 a month in tools, so gross margin is about 80%.

---

## 10. 30-day execution plan

| Days | Goal | Actions | Done when |
|---|---|---|---|
| 1 to 3 | Tools ready | ✅ Audit tool built (`tools/ai_visibility_audit`). ✅ Landing page drafted (`site/`). **You:** approve the API key + $20 budget, pick a brand name, buy the domain (~$12). | First real audit runs on the Claude engine |
| 3 to 7 | Payment + sending setup | **You:** open a Grey or Raenest USD account and a Payoneer account. Set up a sending domain + 2 mailboxes and start warm-up. Publish 2 Fiverr gigs (I draft the copy). | Invoice can be paid; warm-up running |
| 5 to 10 | Validation | I build a list of 200 roofers/HVAC firms in 4 to 6 US metros (Google Maps data via Firecrawl/TinyFish) and run audits on 50 of them. Gate: if at least 60% are "Not named" in at least 6 of 8 questions, the hook holds. | 50 real audits + a go/no-go figure |
| 10 to 14 | Proof | Run 5 free Fix Sprints for audited businesses in exchange for a testimonial and before/after data. **Never fabricate results.** | 5 pilot clients, baseline metrics recorded |
| 14 to 30 | Sell | 20 to 30 personalised emails a day once warm-up is done, each with the prospect's own audit. Fiverr/Upwork proposals daily. Follow up at days 3, 7 and 14. | **Target: first paid Fix Sprint ($497) by day 30. Stretch: 2 retainers.** |

**Kill or pivot rule:** if 400 targeted emails produce fewer than 3 positive replies, the message or the vertical is wrong. Change one variable (trade, offer or price) and re-test before abandoning the model.

---

## Connector plan (what each tool actually does for us)

| Connector | Use in this business | Needs your approval? |
|---|---|---|
| Parallel Search / Firecrawl | Market research (used for this report). Building prospect lists from public business data. | No (research) / credits may bill |
| TinyFish | Browser automation for pulling Google Maps listings and checking competitor pages | Billed per run, so yes past light use |
| Fiverr | Pricing research (used). Cannot publish gigs for us; you publish the copy I draft. | Publishing is under your identity, so yes |
| Gmail | Drafting outreach and replies. **Cold email should go from a separate domain, not your personal Gmail.** | Every send needs approval |
| PayPal | Payment links and invoices as a backup rail | Creating payment links or invoices needs approval |
| Notion | Business OS: CRM pipeline, audit log, weekly reports | Offered below |
| Zapier | Lead form → CRM → audit → email draft pipeline | Only once workflows touch external accounts |
| PostHog | Landing page analytics (visits → audit requests → calls booked) | Free tier; needs your project key |
| Slack | Internal alerts (new lead, audit done). Optional until there is a team. | No |
| Spotify | No credible use in this business. Ignored. | — |

**Recommended additions (none purchased):** Anthropic API key (the audit engine, about $1 to $2 per audit), OpenAI and Perplexity API keys (to audit ChatGPT and Perplexity directly, which is what prospects actually use), Grey or Raenest (USD receiving), and a cold-email sender such as Instantly or Smartlead (~$37/mo, only after the first paid client).

## Decisions I need from you

1. **API budget:** approve an Anthropic API key with a $20 cap for the first 50 real audits.
2. **Brand + domain:** choose a name (working title "Findable") and approve about $12 for the domain.
3. **Vertical:** roofers / HVAC (my recommendation), or another trade.
4. **Payments:** open Grey or Raenest (USD) and Payoneer. These need your identity documents; I cannot do it for you.
5. **Outreach:** approve the email templates in `docs/outreach.md` before anything is sent.
6. **Fiverr:** approve publishing the two gigs under your account.
