# Technical Verification: the AI Visibility Audit Tool

Checked 24 Nov 2026. API prices come from the vendors' own pricing pages on that date; they change often.

## The core distinction

**Generating an AI answer is not the same as measuring what a customer sees.**

- A customer asking the ChatGPT app gets an answer shaped by ChatGPT's own search, their location, chat memory and app version.
- A developer API call with web search uses similar models and a similar search, but it is a different product. Its answers can differ.

The tool therefore labels every answer with one of three measurement types and shows the label in the report:

| Label | Meaning | Engines |
|---|---|---|
| **Observed** | Captured from the real consumer product | `manual` (copied from the ChatGPT app, Perplexity app, Google in a browser), `serpapi_ai_mode` (Google AI Mode scraped for a US location) |
| **API proxy** | A developer API that approximates the product | `gemini`, `openai`, `claude` |
| **Fake** | Test data | `mock`. Reports are stamped SAMPLE DATA and the email-draft command refuses to use them. |

The first version of the tool (session 1) queried only Claude, which few consumers use for local search. **That was a proxy for a proxy, and it has been replaced.**

## Which platforms can it check, and how?

| Platform customers use | Can we measure it? | How | Access needed | Cost |
|---|---|---|---|---|
| **ChatGPT (app)** | Yes, observed, by hand | Paste the questions into ChatGPT (logged out or a clean account), copy the answer into the capture sheet | A free ChatGPT account | $0, about 1 minute per question |
| ChatGPT (approximation) | Yes, API proxy | OpenAI Responses API + `web_search` tool, with a US user location | OpenAI API key (paid) | $10 per 1,000 searches + tokens |
| **Perplexity (app)** | Yes, observed, by hand | Same manual capture | Free account | $0 |
| Perplexity API | Not built yet | Sonar Chat Completions was retired on 27 Sep 2026 (secondary source); the replacement Agent API's request format isn't verified yet. I won't write an adapter against an unverified format. | Perplexity API key | ~$2.50 per 1,000 searches + tokens |
| **Google AI Mode** | Yes, observed | SerpApi `google_ai_mode` engine with a US city location | Free SerpApi account | **250 searches/month free**, then $25/mo for 1,000 |
| **Google AI Overviews** | Partly | They appear on only ~21% of "[service] [city]" searches (Make It Loud, Nov 2026), and SerpApi sometimes needs a second request to load them. Planned after AI Mode. | Same | Same |
| **Gemini** | API proxy only | Gemini API with Google Search grounding. This is not the Gemini app and not AI Overviews. | Free Google AI Studio key | Free tier: 500 grounded requests/day on Flash models |
| Claude | API proxy | Kept as an option, not recommended | Anthropic key | Highest cost per query |

**Important location limit:** you are in Lagos. If you check Google in your own browser, it localises results to Nigeria, so Google checks must go through SerpApi with a US location. ChatGPT and Perplexity questions name the city explicitly ("best roofer in Garland, TX"), which avoids most location effects. Their consumer apps may still use your IP address, so the report labels those answers with the date and engine.

## Cost of 50 audits

Questions depend only on trade + city, so **one market run serves every prospect in that market.** Assumptions:

- 50 prospects ≈ 35 markets
- 8 questions per market, 3 runs each, so ≈ 840 queries per engine

| Engine | Queries | Estimated cost |
|---|---|---|
| Gemini (free tier) | 840 | **$0** (2 days of the daily free limit) |
| SerpApi AI Mode | 840 (or 1 run = 280) | $0 for the first 250/month; one run of 280 needs the $25 Starter month, or spread it over two months |
| OpenAI web search | 840 | ~$10 to $30: $8.40 in search fees plus tokens. Token cost depends on the model chosen, so this is an estimate. |
| Manual ChatGPT + Perplexity | 280 × 2 (1 run each) | $0, about 9 hours of copy-paste. Can be cut to 4 questions per market. |
| Claude (not recommended) | 840 | ~$40 to $120 (estimate) |

**Our first validation batch (20 prospects, 17 markets):**
- Gemini at $0
- SerpApi AI Mode, 1 run of 136 queries: $0
- Manual ChatGPT + Perplexity, 4 questions × 17 markets × 2 apps = 136 captures, about 2.5 hours: $0
- **Total: $0.**

## How reliable is competitor identification?

Two layers, each shown differently in the report:

1. **Verified competitors (reliable).** We check every answer for each *known* business in the same metro (our prospect list, extendable with competitors we look up), using the same matching rules as below. A name in this list is a real business we've confirmed exists.
2. **Unverified names (hints only).** A pattern extractor pulls bold or listed names out of the answer text. These can be misspellings, chains, directories or businesses the AI invented. They appear only if seen at least twice, under an explicit "not yet verified" label, and **never in outreach emails.**

## How false results are prevented

| Risk | Safeguard in the code |
|---|---|
| **False positive:** a generic name matches the wrong business (e.g. "Helping Hands") | Text matching requires the full name *and* a distinctive word. Names made only of generic words never match on text. Prospects flagged "match on domain only" need their website domain in the answer or sources. |
| **False positive:** a partial word ("Westexas" matching "Westex") | Matching is on whole words (tested) |
| **False negative:** the AI uses a shorter name | An aliases column per prospect, plus domain matching against cited sources |
| **One-off answer variance** | Every question is asked 3 times. The report shows "named 2/3", never a single yes/no. |
| **Proxy presented as reality** | Each engine row says "observed" or "API approximation" |
| **Invented competitors** | Only verified businesses appear as competitors. Extracted names are labelled unverified. |
| **Fake data reaching a prospect** | Mock reports are stamped. The drafts command skips fake evidence. |
| **Errors silently counted as "not named"** | Failed API calls are stored with the error text and excluded from counts (only non-empty answers are scored) |
| **Unverifiable claims** | Raw answers, sources, timestamps and model names are stored in the evidence JSON for every report |
| **Human error** | Rule: a person reads every report against its raw answers before anything is sent |

**Tests:** `python3 -m unittest test_audit` runs 7 tests: matching, the partial-word guard, the generic-name guard, name extraction, and a full manual-import → report pipeline with a rival detected. All pass. **The Gemini, SerpApi and OpenAI adapters have not been run against the live APIs yet (no keys).** Their request formats follow the vendors' documentation and will be verified on the first real run.

## Prospect list caveat

The 20 businesses in `data/prospects.csv` come from their own websites. All are marked `unverified` until we confirm each has an active Google Business Profile. I excluded one candidate (Tutela Roofing) because its site lists a 555 placeholder phone number and a placeholder licence number.
