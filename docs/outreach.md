# Outreach: personalised-audit approach (NOTHING SENT, pending approval)

## Principles

1. **Every number in an email comes from that prospect's own evidence file.** `audit.py drafts` fills the numbers in; a person checks them against the report.
2. **No links or attachments in the first email.** This protects deliverability. The report goes out only after a "yes".
3. **Honest identity:** your real name. If asked, say plainly that you work remotely from Lagos, Nigeria. Never imply a US office.
4. **Never claim guaranteed rankings or AI placement.** Never cite unverified statistics (see `market-verification.md`).
5. **Legal:**
   - US CAN-SPAM: a truthful subject line, a valid postal address and a working opt-out honoured within 10 business days
   - Contact businesses only, at addresses they publish
   - Skip anyone who opts out, permanently
6. **Volume:** 10 to 20 hand-reviewed emails a day at most. No bulk tools.

## Personalisation fields (from the audit)

| Field | Source |
|---|---|
| `{{named}} / {{answers}}` | Times the business was named out of total answers |
| `{{top_rival}} / {{rival_count}}` | Most-named *verified* local competitor |
| `{{best_question}}` | One question where a competitor was named and they weren't |
| `{{gap_fix}}` | The single most obvious fix seen on their profile or site (e.g. no cost page, missing GBP services). **Checked by a person, not generated.** |

## Email 1: day 0 (template filled by `audit.py drafts`)

Subject: {{business}} and AI search in {{city}}

Hi {{first_name or "there"}},

I asked AI assistants the questions homeowners ask, like "who is the best {{trade}} in {{city}}?", and checked {{answers}} answers. {{business}} was named in {{named}} of them. {{top_rival}} was named {{rival_count}} times.

I wrote up the results in a short report: the exact questions, who was recommended, and the three fixes most likely to change it. Would you like me to send it? There's no cost.

{{your_name}}
{{brand}}, {{postal_address}}
If this isn't useful, reply "no" and I won't contact you again.

## Email 2: day 3
Subject: re: {{business}} and AI search in {{city}}

Quick follow-up. One specific thing from your results: when asked "{{best_question}}", the AI named {{top_rival}} but not {{business}}. The report shows why that's likely. Should I send it?

## Email 3: day 7
Subject: one fix for {{business}}

{{gap_fix}}. It's usually the quickest change, and you can do it yourself. The full report is ready if you want it.

## Email 4: day 14
Subject: closing the loop

I'll stop here. If AI search becomes a priority, reply any time and I'll re-run your questions with fresh results.

## After a "yes"
1. Send the HTML/PDF report, plus an optional 3-minute Loom walkthrough.
2. Offer: "I can do everything in the report's fix list for a fixed $497: half to start, half when it's delivered. Each deliverable is listed with how you'll verify it. Anything not delivered within 14 days is refunded. Then I re-run these same questions after 30 days so you can see what changed."
3. Attach `offer.md` as a one-page PDF.

## Prospects without a public email (#3, #8, #11, #12, #14, #16, #17)
Use their website contact form with the same text, or skip. Don't scrape for hidden addresses.
