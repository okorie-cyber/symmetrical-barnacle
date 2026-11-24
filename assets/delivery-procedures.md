# Delivery Procedures (SOPs)

## A. Website build: 7-day standard (Business package)

**Day 0, sale**
1. Confirm scope in writing (WhatsApp or email): package, pages, price, deadline, revision rounds, what the client provides.
2. Send the invoice (template below) and receive the 50% deposit. **No work before the deposit.**
3. Send the intake questions.

**Intake questions**
- Business name, what you sell, area served, opening hours, phone/WhatsApp, address/Google Maps link
- Top 3–6 services or products with prices (or "from" prices)
- Your main customer and the one action you want them to take (call / WhatsApp / book / visit)
- 5–15 photos (your real work beats stock photos), logo, brand colours
- 3 customer reviews you're allowed to quote (with first name)
- 2–3 websites you like
- Domain: do you own one? (If not, the client buys it: we send instructions.)

**Days 1–3, build**
4. Start from the closest portfolio template (`site/portfolio/`). Replace all content, never leaving placeholder text.
5. Write the copy: headline = what you do + where + main benefit. Every section ends with the call-to-action.
6. Technical checklist:
   - Mobile first
   - Images compressed (under 200 KB each)
   - `<title>` and meta description on every page
   - LocalBusiness JSON-LD schema with the real name, address, phone and hours
   - Click-to-call and wa.me links that work
   - Alt text on images
   - Favicon
   - 404 page

**Day 4, review**
7. Deploy a preview to a free Cloudflare Pages URL (`project.pages.dev`) and send the link. Collect feedback in one consolidated message.

**Days 5–6, revisions**
8. Apply the revisions. Run the QA list:
   - Test on a real phone
   - Check every link and button
   - Check spelling
   - Check load speed in PageSpeed Insights (free)
   - Check the contact form arrives

**Day 7, launch**
9. Receive the balance. **Don't connect the domain or transfer the project before full payment.**
10. In the client's own free Cloudflare account (we create it together on a call or screen-share, using their email): upload the site, connect their domain, confirm HTTPS.
11. Handover pack: logins live in the client's own password manager or notes (we never keep their passwords), a 1-page edit guide, and the source files (zip).
12. Ask for a review/testimonial and a referral. Offer the care plan.

**Invoice template**
```
INVOICE #{{n}}   Date: {{date}}
From: {{your name}}, {{phone}}, {{email}}
To: {{client}}
Item: {{package}}, as agreed on {{date}}                ₦{{total}}
Deposit due now (50%): ₦{{half}}   Balance due before launch: ₦{{half}}
Pay to: {{bank}}, {{account name}}, {{account number}}
```

## B. Google Business Profile setup (Lagos or remote)
1. Search Maps for the business. Claim the listing if it exists; otherwise create it with the owner's Google account. **The owner completes Google's verification themselves** (video or postcard; we never fake an address).
2. Pick the primary category (the most specific true one) and 2–4 secondary categories.
3. Fill in: description (750 characters, no keyword stuffing), hours, phone, website/WhatsApp link, service area, services/menu with prices, attributes, opening date.
4. Upload 10+ real photos: exterior, interior, team, work and products. Add a logo and cover photo.
5. Create the review link and a printable QR card (free QR generator). Teach the owner to ask every customer. **No fake reviews and no paying for reviews.**
6. Before/after screenshots sent to the client. Remind them to post monthly.

## C. Manual AI visibility audit (the free version of our tool)
1. Generate the questions: `python3 tools/ai_visibility_audit/audit.py prompts --prospects <file> --runs 2 --out sheet.csv` (works offline, free).
2. For US clients, connect Proton VPN free to a US server.
3. Use clean sessions: ChatGPT (logged out, or a temporary chat), Perplexity (logged out), Gemini, and Google search in a private window. Paste each question exactly as written.
4. Copy the full answer and any cited links into the sheet. Note the date, engine and whether search was used.
5. Import and report: `audit.py run --engine manual --input sheet.csv ...` then `audit.py report ...`. Read every report against the raw answers.
6. Add the GBP check (section B, steps 2–4, as findings) and a directory check (Yelp, BBB, Facebook, Apple Maps, Bing Places; for Lagos: VConnect, BusinessList.com.ng, Google).
7. Deliver the HTML report (or print it to PDF from the browser, free), plus 3–10 fixes in priority order.

## D. Quality rules for every job
- Never claim results we haven't measured. Never use fake reviews, fake stats or "guaranteed #1".
- All client accounts are owned by the client.
- Deadlines are missed only with notice and a new date agreed in writing.
- Keep a copy of every deliverable and the client's written approval in their project folder (Google Drive free).

## E. AI-assisted fast delivery (target: first preview within 24 hours of the deposit)
1. **Intake by WhatsApp.** The client sends voice notes, photos and a price list. You forward the text and photos into our session; no forms needed.
2. **Same-day draft.** I generate the site from the closest demo (food → Ewà, beauty → Kínní, services → Oakvale), replacing **every** placeholder, writing the copy and adding schema.
3. **Your 20-minute check:** open it on your phone, tap every button, read every price aloud against the client's list.
4. **Preview.** Deploy to the client's free Cloudflare Pages account during a short screen-share, or send screenshots plus a local preview until their account exists.
5. **One consolidated revision round,** applied in the session within hours.
6. **Quality never skipped:** real client content only, mobile test, links tested, a spelling pass, PageSpeed check.

Typical time per Starter site: about 3 hours of your time, spread over 2 days.
