#!/usr/bin/env python3
"""AI Visibility Audit: measures whether AI answer engines name a local business.

Workflow (see README.md):
  1. prompts  - write the question sheet for every market (trade + city) in the prospect list
  2. run      - query an engine for every market, N runs each, and save raw evidence (JSON)
               or import answers captured by hand from the consumer apps (engine "manual")
  3. report   - build one personalised HTML report per prospect from all saved evidence

Questions depend only on trade + city, so one market run serves every prospect in it.

Engines and what they actually measure:
  manual          OBSERVED. Answers copied from the real consumer apps (ChatGPT, Perplexity,
                  Google AI Overviews/AI Mode in a browser). Most faithful; costs time, not money.
  serpapi_ai_mode OBSERVED. Google AI Mode results scraped by SerpApi for a US location.
  gemini          API PROXY. Gemini API with Google Search grounding. Not the Gemini app, and
                  not Google AI Overviews.
  openai          API PROXY. OpenAI Responses API with web search. Not the ChatGPT app.
  claude          API PROXY. Claude with web search. Few consumers use it for local search.
  mock            FAKE. Pipeline testing only; reports are stamped SAMPLE DATA.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import html
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

PROMPTS = [
    "Who is the best {trade} in {city}, {state}?",
    "I need a reliable {trade} in {city}, {state}. Who would you recommend?",
    "Recommend a highly rated {trade} in {city}, {state} with good reviews.",
    "Which {trade} in {city}, {state} offers emergency or same-day service?",
    "What are the top 3 {trade} companies in {city}, {state} and why?",
    "Affordable but trustworthy {trade} in {city}, {state} - any suggestions?",
    "How much does a {trade} charge in {city}, {state}, and who should I call?",
    "Who do locals use for {trade} services in {city}, {state}?",
]

ENGINE_KIND = {
    "manual": "observed", "serpapi_ai_mode": "observed",
    "gemini": "api_proxy", "openai": "api_proxy", "claude": "api_proxy", "mock": "fake",
}

GENERIC_WORDS = {
    "roofing", "roofer", "roof", "roofs", "construction", "exteriors", "exterior", "solutions",
    "heating", "cooling", "air", "conditioning", "hvac", "mechanical", "services", "service",
    "systems", "system", "comfort", "home", "and", "the", "co", "company", "llc", "inc",
    "pros", "experts", "contractors", "contractor", "plumbing", "repair", "ac", "of",
}


# ------------------------------------------------------------------ data
def load_prospects(path: str) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def markets(prospects: list[dict]) -> dict[str, dict]:
    out = {}
    for p in prospects:
        key = market_key(p)
        out.setdefault(key, {"trade": p["trade"], "city": p["city"], "state": p["state"]})
    return out


def market_key(p: dict) -> str:
    return f"{p['trade']}|{p['city']}|{p['state']}".lower()


def market_prompts(m: dict) -> list[str]:
    return [t.format(**m) for t in PROMPTS]


# ------------------------------------------------------------------ matching
def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def bare_domain(d: str) -> str:
    d = d.lower().strip()
    d = re.sub(r"^https?://", "", d)
    d = d.removeprefix("www.")
    return d.split("/")[0]


def distinctive_tokens(name: str) -> list[str]:
    return [t for t in norm(name).split() if t not in GENERIC_WORDS and len(t) > 1]


def match_business(p: dict, text: str, sources: list[str]) -> dict:
    """Return {'named': bool, 'evidence': str, 'confidence': 'high'|'medium'|'none'}.

    High   = the business's own domain appears in the answer or its cited sources.
    Medium = the full business name (or a listed alias) appears and contains a
             distinctive word, so generic names like "Helping Hands" never match on text alone.
    """
    dom = bare_domain(p.get("website", ""))
    hay_sources = " ".join(s.lower() for s in sources)
    if dom and (dom in text.lower() or dom in hay_sources):
        return {"named": True, "confidence": "high", "evidence": f"domain {dom} cited"}
    ntext = f" {norm(text)} "
    names = [p["business"]] + [a for a in p.get("aliases", "").split(";") if a.strip()]
    generic_only = "match on domain only" in p.get("notes", "").lower()
    for n in names:
        if generic_only or not distinctive_tokens(n):
            continue
        if f" {norm(n)} " in ntext:
            return {"named": True, "confidence": "medium", "evidence": f'name "{n}" in answer'}
    return {"named": False, "confidence": "none", "evidence": ""}


NAME_PATTERNS = [
    re.compile(r"\*\*([A-Z][^*\n]{2,60}?)\*\*"),                       # **Bold Name**
    re.compile(r"^\s*(?:\d+[.)]|[-*•])\s+\**([A-Z][\w&'.\- ]{2,50}?)\**\s*(?:[:–—(-]|$)", re.M),
]


def extract_names(text: str) -> list[str]:
    """Heuristic list of business-like names. UNVERIFIED: shown only as hints."""
    found = []
    for pat in NAME_PATTERNS:
        for m in pat.finditer(text):
            n = m.group(1).strip(" *:-")
            if 2 <= len(n.split()) <= 7 and n not in found:
                found.append(n)
    return found


# ------------------------------------------------------------------ engines
def http_json(url: str, body: dict | None = None, headers: dict | None = None, timeout: int = 120) -> dict:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json", **(headers or {})})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


def need(var: str) -> str:
    v = os.environ.get(var)
    if not v:
        sys.exit(f"Set {var} first.")
    return v


def ask_gemini(prompt: str, m: dict) -> tuple[str, list[str], str]:
    model = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    data = http_json(url, {"contents": [{"parts": [{"text": prompt}]}], "tools": [{"google_search": {}}]},
                     {"x-goog-api-key": need("GEMINI_API_KEY")})
    cand = (data.get("candidates") or [{}])[0]
    text = "".join(p.get("text", "") for p in cand.get("content", {}).get("parts", []))
    chunks = cand.get("groundingMetadata", {}).get("groundingChunks", [])
    # Gemini returns redirect URIs; the title usually carries the real domain.
    sources = [f"{c.get('web', {}).get('title', '')} {c.get('web', {}).get('uri', '')}" for c in chunks]
    return text, sources, model


def ask_serpapi_ai_mode(prompt: str, m: dict) -> tuple[str, list[str], str]:
    q = urllib.parse.urlencode({"engine": "google_ai_mode", "q": prompt, "gl": "us", "hl": "en",
                                "location": f"{m['city']}, {m['state']}, United States",
                                "api_key": need("SERPAPI_API_KEY")})
    data = http_json(f"https://serpapi.com/search.json?{q}")
    text = data.get("reconstructed_markdown") or "\n".join(
        b.get("snippet", "") for b in data.get("text_blocks", []))
    sources = [f"{r.get('title', '')} {r.get('link', '')} {r.get('source', '')}" for r in data.get("references", [])]
    return text, sources, "google_ai_mode"


def ask_openai(prompt: str, m: dict) -> tuple[str, list[str], str]:
    model = need("OPENAI_MODEL")  # pick a current web-search-capable model from OpenAI's model list
    body = {"model": model, "input": prompt, "tools": [{
        "type": "web_search",
        "user_location": {"type": "approximate", "country": "US", "city": m["city"], "region": m["state"]}}]}
    data = http_json("https://api.openai.com/v1/responses", body, {"Authorization": f"Bearer {need('OPENAI_API_KEY')}"})
    text, sources = "", []
    for item in data.get("output", []):
        if item.get("type") == "message":
            for c in item.get("content", []):
                if c.get("type") == "output_text":
                    text += c.get("text", "")
                    sources += [f"{a.get('title', '')} {a.get('url', '')}" for a in c.get("annotations", [])]
    return text, sources, model


def ask_claude(prompt: str, m: dict) -> tuple[str, list[str], str]:
    try:
        import anthropic
    except ImportError:
        sys.exit("pip install anthropic")
    model = "claude-opus-5-5"
    resp = anthropic.Anthropic().beta.messages.create(
        model=model, max_tokens=16000, betas=["server-side-fallback-2026-07-01"], fallbacks="default",
        output_config={"effort": "low"},
        tools=[{"type": "web_search_20260209", "name": "web_search", "max_uses": 3,
                "user_location": {"type": "approximate", "country": "US", "city": m["city"], "region": m["state"]}}],
        messages=[{"role": "user", "content": prompt}])
    if resp.stop_reason == "refusal":
        return "", [], model
    text, sources = "", []
    for b in resp.content:
        if b.type == "text":
            text += b.text
            for c in getattr(b, "citations", None) or []:
                sources.append(f"{getattr(c, 'title', '')} {getattr(c, 'url', '')}")
    return text, sources, model


def ask_mock(prompt: str, m: dict, run: int = 0, i: int = 0) -> tuple[str, list[str], str]:
    names = ["Lone Star Pros", "Capital City Services", "BlueLine Experts", "Hill Country Co"]
    picks = [names[(i + run + k) % len(names)] for k in range(3)]
    return "Options people recommend:\n" + "\n".join(f"{k + 1}. **{n}** - well reviewed" for k, n in enumerate(picks)), [], "mock"


ENGINES = {"gemini": ask_gemini, "serpapi_ai_mode": ask_serpapi_ai_mode, "openai": ask_openai, "claude": ask_claude}


# ------------------------------------------------------------------ commands
def cmd_prompts(a) -> None:
    rows = []
    for key, m in markets(load_prospects(a.prospects)).items():
        for i, q in enumerate(market_prompts(m)):
            for run in range(1, a.runs + 1):
                rows.append({"market": key, "prompt_index": i, "prompt": q, "run": run,
                             "engine": "chatgpt_app|perplexity_app|google_ai_overview|google_ai_mode",
                             "captured_at": "", "answer": "", "sources": ""})
    with open(a.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} capture rows written to {a.out} (one row per engine you capture; copy rows as needed)")


def cmd_run(a) -> None:
    prospects = load_prospects(a.prospects)
    records = []
    if a.engine == "manual":
        with open(a.input, newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                if r.get("answer", "").strip():
                    records.append({"engine": "manual:" + r["engine"], "kind": "observed", "model": r["engine"],
                                    "market": r["market"], "prompt_index": int(r["prompt_index"]),
                                    "prompt": r["prompt"], "run": int(r["run"]),
                                    "captured_at": r.get("captured_at") or "", "answer": r["answer"],
                                    "sources": [s for s in r.get("sources", "").split() if s]})
    else:
        for key, m in markets(prospects).items():
            if a.market and a.market.lower() not in key:
                continue
            for i, q in enumerate(market_prompts(m)[: a.prompts]):
                for run in range(1, a.runs + 1):
                    try:
                        if a.engine == "mock":
                            text, sources, model = ask_mock(q, m, run, i)
                        else:
                            text, sources, model = ENGINES[a.engine](q, m)
                    except Exception as e:  # keep going; record the failure as evidence
                        text, sources, model = "", [], f"ERROR: {e}"
                    records.append({"engine": a.engine, "kind": ENGINE_KIND[a.engine], "model": model,
                                    "market": key, "prompt_index": i, "prompt": q, "run": run,
                                    "captured_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
                                    "answer": text, "sources": sources})
                    print(f"[{a.engine}] {key} q{i + 1} run{run}: {'ok' if text else 'EMPTY/ERROR ' + model}")
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=1)
    print(f"{len(records)} records saved to {a.out}")


def analyse(p: dict, peers: list[dict], records: list[dict]) -> dict:
    key = market_key(p)
    recs = [r for r in records if r["market"] == key and r["answer"].strip()]
    by_engine = defaultdict(lambda: {"answers": 0, "named": 0, "kind": ""})
    per_prompt = defaultdict(lambda: defaultdict(lambda: [0, 0]))  # prompt -> engine -> [named, total]
    rivals, unverified, evidence = Counter(), Counter(), []
    for r in recs:
        res = match_business(p, r["answer"], r["sources"])
        e = by_engine[r["engine"]]
        e["kind"], e["answers"] = r["kind"], e["answers"] + 1
        e["named"] += res["named"]
        cell = per_prompt[r["prompt"]][r["engine"]]
        cell[0] += res["named"]
        cell[1] += 1
        if res["named"]:
            evidence.append({**res, "engine": r["engine"], "prompt": r["prompt"], "run": r["run"]})
        named_peers = set()
        for q in peers:
            if q["id"] != p["id"] and match_business(q, r["answer"], r["sources"])["named"]:
                rivals[q["business"]] += 1
                named_peers.add(norm(q["business"]))
        for n in extract_names(r["answer"]):
            if norm(n) not in named_peers and not match_business(p, n, [])["named"]:
                unverified[n] += 1
    return {"answers": len(recs), "by_engine": dict(by_engine), "per_prompt": per_prompt,
            "rivals": rivals, "unverified": unverified, "evidence": evidence,
            "fake": any(r["kind"] == "fake" for r in recs)}


RECS = [
    ("Google Business Profile", "Complete services, service areas, categories, photos and hours. Google's AI answers cite these profiles more than any other source."),
    ("Review volume and recency", "Ask every finished job for a review. Businesses AI names tend to have far more Google reviews."),
    ("Local cost pages", "Publish a page answering 'how much does a new roof / AC cost in [city]' with real ranges. Cost questions trigger AI answers almost every time."),
    ("Directory consistency", "Keep name, address and phone identical on Yelp, Angi, BBB, Facebook and Nextdoor, which AI tools cite."),
]


def render(p: dict, a: dict) -> str:
    e = html.escape
    engines = sorted(a["by_engine"])
    label = {"observed": "observed in the real product", "api_proxy": "API approximation", "fake": "FAKE TEST DATA"}
    eng_rows = "".join(
        f"<tr><td>{e(n)}</td><td>{e(label[v['kind']])}</td><td>{v['named']} of {v['answers']}</td></tr>"
        for n, v in sorted(a["by_engine"].items()))
    head = "".join(f"<th>{e(n)}</th>" for n in engines)
    rows = ""
    for q, cells in a["per_prompt"].items():
        tds = "".join(
            (f"<td class='{'yes' if cells[n][0] else 'no'}'>{cells[n][0]}/{cells[n][1]}</td>" if n in cells else "<td>-</td>")
            for n in engines)
        rows += f"<tr><td>{e(q)}</td>{tds}</tr>"
    rival_rows = "".join(f"<li>{e(n)} - named {c} times</li>" for n, c in a["rivals"].most_common(6)) or "<li>None of the other businesses we checked were named.</li>"
    unv = [f"{e(n)} ({c})" for n, c in a["unverified"].most_common(10) if c >= 2]
    unv_html = f"<p class='muted'>Other names that appeared at least twice (not yet verified as real local businesses): {', '.join(unv)}</p>" if unv else ""
    ev = "".join(f"<li>{e(x['engine'])}, run {x['run']}: {e(x['evidence'])} - <i>{e(x['prompt'])}</i></li>" for x in a["evidence"][:12])
    total_named = sum(v["named"] for v in a["by_engine"].values())
    recs = "".join(f"<li><b>{e(t)}.</b> {e(d)}</li>" for t, d in RECS)
    banner = "<div class='sample'>SAMPLE DATA. Produced by the mock engine for testing. Not a measurement.</div>" if a["fake"] else ""
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>AI Visibility Audit</title>
<style>
:root{{--bg:#fff;--fg:#14171f;--muted:#5b6270;--line:#e3e6ec;--yes:#137a3f;--no:#b3261e;--accent:#2647d9}}
@media (prefers-color-scheme:dark){{:root{{--bg:#111318;--fg:#eceef2;--muted:#a0a6b2;--line:#2a2e37;--yes:#4cc985;--no:#ff8a80;--accent:#8ea2ff}}}}
body{{background:var(--bg);color:var(--fg);font:16px/1.5 system-ui,sans-serif;margin:0;padding:24px 16px}}
main{{max-width:900px;margin:auto}} .muted{{color:var(--muted)}} .wrap{{overflow-x:auto}}
table{{width:100%;border-collapse:collapse;margin:12px 0 28px}} td,th{{border-bottom:1px solid var(--line);padding:8px;text-align:left;vertical-align:top}}
.yes{{color:var(--yes);font-weight:600}} .no{{color:var(--no);font-weight:600}}
.big{{font-size:40px;font-weight:700;color:var(--accent)}} .sample{{border:2px dashed var(--no);padding:10px;color:var(--no);font-weight:700}}
</style></head><body><main>{banner}
<h1>AI Visibility Audit: {e(p['business'])}</h1>
<p class="muted">{e(p['trade'].title())} &middot; {e(p['city'])}, {e(p['state'])} &middot; {a['answers']} AI answers checked &middot; prepared {dt.date.today():%d %B %Y}</p>
<p><span class="big">{total_named} of {a['answers']}</span><br>AI answers named {e(p['business'])}.</p>
<h2>By AI engine</h2><div class="wrap"><table><tr><th>Engine</th><th>What it measures</th><th>Times named</th></tr>{eng_rows}</table></div>
<h2>Question by question</h2><p class="muted">Each cell shows times named / times asked. We ask every question more than once because AI answers change between runs.</p>
<div class="wrap"><table><tr><th>Customer question</th>{head}</tr>{rows}</table></div>
<h2>Local competitors named in the same answers</h2><ul>{rival_rows}</ul>{unv_html}
<h2>Evidence</h2><ul>{ev or '<li>No mentions found.</li>'}</ul>
<h2>What usually moves this</h2><ol>{recs}</ol>
<p class="muted">How to read this: "observed" rows come from the real consumer products; "API approximation" rows come from developer APIs
that use similar models and search but can differ from what a customer sees. Answers vary by day, device and location. This is a dated snapshot,
not a ranking, and nobody can guarantee placement in AI answers. Raw answers are kept and available on request.</p>
</main></body></html>"""


def cmd_report(a) -> None:
    prospects = load_prospects(a.prospects)
    records = []
    for path in a.evidence:
        with open(path, encoding="utf-8") as f:
            records += json.load(f)
    Path(a.outdir).mkdir(parents=True, exist_ok=True)
    targets = [p for p in prospects if not a.id or p["id"] in a.id]
    summary = []
    for p in targets:
        peers = [q for q in prospects if q["metro"] == p["metro"]]
        res = analyse(p, peers, records)
        if not res["answers"]:
            print(f"#{p['id']} {p['business']}: no evidence for its market, skipped")
            continue
        out = Path(a.outdir) / f"{p['id']}-{norm(p['business']).replace(' ', '-')}.html"
        out.write_text(render(p, res), encoding="utf-8")
        named = sum(v["named"] for v in res["by_engine"].values())
        summary.append((p["id"], p["business"], named, res["answers"]))
        print(f"#{p['id']} {p['business']}: named {named}/{res['answers']} -> {out}")


def cmd_drafts(a) -> None:
    """Write first-touch email drafts using only numbers found in the evidence. Nothing is sent."""
    prospects = load_prospects(a.prospects)
    records = []
    for path in a.evidence:
        with open(path, encoding="utf-8") as f:
            records += json.load(f)
    out = ["# Outreach drafts: NOT SENT. Review every line against the report before approval.\n"]
    for p in prospects:
        peers = [q for q in prospects if q["metro"] == p["metro"]]
        res = analyse(p, peers, records)
        if not res["answers"] or res["fake"]:
            continue
        named = sum(v["named"] for v in res["by_engine"].values())
        rival = res["rivals"].most_common(1)
        rival_line = f" {rival[0][0]} was named {rival[0][1]} times in the same answers." if rival else ""
        to = p.get("public_email") or "(no public email: use the contact form or phone)"
        out.append(f"""## #{p['id']} {p['business']}
To: {to}
Subject: {p['business']} and AI search in {p['city']}

Hi,

I asked AI assistants the questions homeowners ask, like "who is the best {p['trade']} in {p['city']}?", and checked {res['answers']} answers. {p['business']} was named in {named} of them.{rival_line}

I wrote up the results in a short report: the exact questions, who was recommended, and the three fixes most likely to change it. Would you like me to send it? There's no cost.

{{sender_name}}
{{brand}}, {{postal_address}}
If this isn't useful, reply "no" and I won't contact you again.
""")
    Path(a.out).write_text("\n".join(out), encoding="utf-8")
    print(f"Drafts written to {a.out}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("prompts", help="write a manual capture sheet (CSV)")
    s.add_argument("--prospects", required=True)
    s.add_argument("--runs", type=int, default=2)
    s.add_argument("--out", default="capture-sheet.csv")
    s = sub.add_parser("run", help="query an engine (or import a manual capture sheet)")
    s.add_argument("--engine", required=True, choices=["mock", "manual", *ENGINES])
    s.add_argument("--prospects", required=True)
    s.add_argument("--input", help="filled capture sheet, for --engine manual")
    s.add_argument("--market", help="only markets containing this text, e.g. 'garland'")
    s.add_argument("--prompts", type=int, default=len(PROMPTS))
    s.add_argument("--runs", type=int, default=3)
    s.add_argument("--out", required=True)
    s = sub.add_parser("report", help="build personalised HTML reports from evidence files")
    s.add_argument("--prospects", required=True)
    s.add_argument("--evidence", nargs="+", required=True)
    s.add_argument("--id", nargs="*", help="prospect ids (default: all)")
    s.add_argument("--outdir", default="reports")
    s = sub.add_parser("drafts", help="write outreach drafts from real evidence (never sends)")
    s.add_argument("--prospects", required=True)
    s.add_argument("--evidence", nargs="+", required=True)
    s.add_argument("--out", default="drafts.md")
    a = ap.parse_args()
    {"prompts": cmd_prompts, "run": cmd_run, "report": cmd_report, "drafts": cmd_drafts}[a.cmd](a)


if __name__ == "__main__":
    main()
