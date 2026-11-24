#!/usr/bin/env python3
"""AI Visibility Audit - checks whether an AI assistant recommends a local business.

It asks an AI engine the questions real customers ask ("best emergency plumber in
Austin"), records which businesses the answer names, and writes an HTML report
showing whether the target business appears and which competitors appear instead.

Engines:
  claude - Claude with live web search (needs ANTHROPIC_API_KEY; costs money per run)
  mock   - deterministic fake answers for testing the pipeline. Mock reports are
           stamped SAMPLE DATA and must never be shown to a prospect as real results.

Usage:
  python audit.py --business "Acme Plumbing" --domain acmeplumbing.com \
      --trade plumber --city "Austin, TX" --engine mock --out report.html
"""
from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import re
import sys
from collections import Counter
from dataclasses import dataclass, field

MODEL = "claude-opus-5-5"

PROMPT_TEMPLATES = [
    "Who is the best {trade} in {city}?",
    "I need a reliable {trade} in {city}. Who would you recommend?",
    "Recommend a highly rated {trade} near {city} with good reviews.",
    "Which {trade} in {city} offers emergency or same-day service?",
    "What are the top 3 {trade} companies in {city} and why?",
    "Affordable but trustworthy {trade} in {city} - any suggestions?",
    "How much does a {trade} cost in {city}, and who should I call?",
    "Who do locals use for {trade} services in {city}?",
]

EXTRACT_SCHEMA = {
    "type": "object",
    "properties": {
        "businesses": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "website": {"type": "string"},
                },
                "required": ["name", "website"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["businesses"],
    "additionalProperties": False,
}


@dataclass
class PromptResult:
    prompt: str
    answer: str
    businesses: list[dict] = field(default_factory=list)
    mentioned: bool = False


def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"\b(llc|inc|co|ltd|the|company|services?)\b", " ", text)
    return re.sub(r"[^a-z0-9]+", "", text)


def is_mentioned(business: str, domain: str, answer: str, names: list[dict]) -> bool:
    target = normalize(business)
    dom = domain.lower().removeprefix("https://").removeprefix("http://").removeprefix("www.").strip("/")
    if dom and dom in answer.lower():
        return True
    if target and target in normalize(answer):
        return True
    for b in names:
        if target and (target in normalize(b.get("name", "")) or normalize(b.get("name", "")) == target):
            return True
        if dom and dom in b.get("website", "").lower():
            return True
    return False


# ---------------------------------------------------------------- engines
class MockEngine:
    label = "Mock engine (SAMPLE DATA)"
    sample = True

    def __init__(self, business: str):
        self.business = business

    def ask(self, prompt: str, idx: int) -> tuple[str, list[dict]]:
        pool = ["Lone Star Pros", "Capital City Services", "BlueLine Experts", "Hill Country Co"]
        picks = [pool[(idx + k) % len(pool)] for k in range(3)]
        if idx % 4 == 1:  # target appears in a quarter of answers
            picks[2] = self.business
        answer = "Here are some options people often recommend: " + ", ".join(picks) + "."
        return answer, [{"name": p, "website": ""} for p in picks]


class ClaudeEngine:
    label = f"Claude ({MODEL}) with live web search"
    sample = False

    def __init__(self, city: str):
        try:
            import anthropic
        except ImportError:
            sys.exit("Install the SDK first: pip install anthropic")
        self.client = anthropic.Anthropic()
        self.city = city

    def ask(self, prompt: str, idx: int) -> tuple[str, list[dict]]:
        resp = self.client.beta.messages.create(
            model=MODEL,
            max_tokens=16000,
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
            output_config={"effort": "low"},
            tools=[{"type": "web_search_20260209", "name": "web_search", "max_uses": 3}],
            messages=[{"role": "user", "content": prompt}],
        )
        if resp.stop_reason == "refusal":
            return "(engine declined to answer)", []
        answer = "".join(b.text for b in resp.content if getattr(b, "type", "") == "text").strip()
        return answer, self._extract(answer)

    def _extract(self, answer: str) -> list[dict]:
        if not answer:
            return []
        resp = self.client.beta.messages.create(
            model=MODEL,
            max_tokens=4000,
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
            output_config={"effort": "low", "format": {"type": "json_schema", "schema": EXTRACT_SCHEMA}},
            messages=[{
                "role": "user",
                "content": "List every business this answer recommends or names, in order. "
                           "Use an empty string for website when none is given.\n\n" + answer,
            }],
        )
        if resp.stop_reason == "refusal":
            return []
        text = "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")
        try:
            return json.loads(text).get("businesses", [])
        except json.JSONDecodeError:
            return []


# ---------------------------------------------------------------- report
RECOMMENDATIONS = [
    ("Google Business Profile", "Complete every field, pick precise categories, add services, photos and current hours. "
     "Local AI answers lean heavily on these listings."),
    ("Review volume and recency", "Ask every finished job for a review. Businesses AI names tend to have far more Google reviews."),
    ("Local cost and process pages", "Publish pages that answer 'how much does X cost in [city]' with real price ranges. "
     "Cost questions trigger AI answers almost every time."),
    ("Directory consistency", "Keep name, address and phone identical on Yelp, Angi, BBB, Facebook and niche directories AI tools cite."),
    ("Re-measure monthly", "AI answers change week to week. Track the same questions over time and judge success by calls and bookings."),
]


def render(args, engine, results: list[PromptResult]) -> str:
    hits = sum(r.mentioned for r in results)
    total = len(results)
    comp = Counter()
    for r in results:
        for b in r.businesses:
            if not is_mentioned(args.business, args.domain, b.get("name", ""), [b]):
                comp[b.get("name", "").strip()] += 1
    comp.pop("", None)
    e = html.escape
    rows = "".join(
        f"<tr><td>{e(r.prompt)}</td><td class='{'yes' if r.mentioned else 'no'}'>{'Named' if r.mentioned else 'Not named'}</td>"
        f"<td>{e(', '.join(b.get('name', '') for b in r.businesses) or '-')}</td></tr>"
        for r in results
    )
    comp_rows = "".join(f"<tr><td>{e(n)}</td><td>{c} of {total}</td></tr>" for n, c in comp.most_common(8)) or \
        "<tr><td colspan='2'>No other businesses detected</td></tr>"
    recs = "".join(f"<li><b>{e(t)}.</b> {e(d)}</li>" for t, d in RECOMMENDATIONS)
    banner = ("<div class='sample'>SAMPLE DATA - generated by the mock engine for testing. "
              "Not a real measurement.</div>") if engine.sample else ""
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>AI Visibility Audit</title>
<style>
:root{{--bg:#fff;--fg:#14171f;--muted:#5b6270;--line:#e3e6ec;--yes:#137a3f;--no:#b3261e;--accent:#2647d9}}
@media (prefers-color-scheme:dark){{:root{{--bg:#111318;--fg:#eceef2;--muted:#a0a6b2;--line:#2a2e37;--yes:#4cc985;--no:#ff8a80;--accent:#8ea2ff}}}}
body{{background:var(--bg);color:var(--fg);font:16px/1.5 system-ui,sans-serif;margin:0;padding:24px 16px}}
main{{max-width:860px;margin:auto}} h1{{margin:0 0 4px}} .muted{{color:var(--muted)}}
.score{{font-size:48px;font-weight:700;color:var(--accent)}} table{{width:100%;border-collapse:collapse;margin:12px 0 28px}}
td,th{{border-bottom:1px solid var(--line);padding:8px;text-align:left;vertical-align:top}}
.yes{{color:var(--yes);font-weight:600}} .no{{color:var(--no);font-weight:600}}
.sample{{border:2px dashed var(--no);padding:10px;margin-bottom:16px;color:var(--no);font-weight:700}}
.wrap{{overflow-x:auto}}
</style></head><body><main>{banner}
<h1>AI Visibility Audit: {e(args.business)}</h1>
<p class="muted">{e(args.trade.title())} in {e(args.city)} &middot; Engine: {e(engine.label)} &middot; {dt.date.today():%d %B %Y}</p>
<p><span class="score">{hits}/{total}</span><br>customer questions where the AI named {e(args.business)}.</p>
<h2>What the AI said</h2><div class="wrap"><table><tr><th>Customer question</th><th>Result</th><th>Businesses named</th></tr>{rows}</table></div>
<h2>Who the AI recommends instead</h2><div class="wrap"><table><tr><th>Business</th><th>Times named</th></tr>{comp_rows}</table></div>
<h2>What usually moves this number</h2><ol>{recs}</ol>
<p class="muted">Method: each question was sent once, unprimed, to the engine above. AI answers vary between runs and between engines
(ChatGPT, Perplexity, Google AI Overviews), so treat this as a snapshot, not a ranking guarantee.</p>
</main></body></html>"""


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--business", required=True)
    p.add_argument("--domain", default="")
    p.add_argument("--trade", required=True, help="e.g. plumber, dentist, roofer")
    p.add_argument("--city", required=True)
    p.add_argument("--engine", choices=["mock", "claude"], default="mock")
    p.add_argument("--prompts", type=int, default=len(PROMPT_TEMPLATES))
    p.add_argument("--out", default="report.html")
    p.add_argument("--json", help="also write raw results to this JSON file")
    args = p.parse_args()

    engine = MockEngine(args.business) if args.engine == "mock" else ClaudeEngine(args.city)
    results = []
    for i, tpl in enumerate(PROMPT_TEMPLATES[: args.prompts]):
        prompt = tpl.format(trade=args.trade, city=args.city)
        answer, names = engine.ask(prompt, i)
        results.append(PromptResult(prompt, answer, names, is_mentioned(args.business, args.domain, answer, names)))
        print(f"[{i + 1}/{args.prompts}] {'NAMED' if results[-1].mentioned else 'not named'} - {prompt}")

    with open(args.out, "w", encoding="utf-8") as f:
        f.write(render(args, engine, results))
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump([r.__dict__ for r in results], f, indent=2)
    print(f"Report written to {args.out}")


if __name__ == "__main__":
    main()
