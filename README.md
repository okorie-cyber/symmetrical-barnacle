# $1M Mission: Business Operating Repo

Working business: **Findable** (working name), a productized "Get Found by AI" service for US home-service businesses.

| Path | What it is |
|---|---|
| `REPORT.md` | Report #1: 10 opportunities, evidence, top 3, the chosen business, 30-day plan, decisions needed |
| `docs/milestones.md` | $100 → $1M milestone model, with assumptions and expenses |
| `docs/outreach.md` | Cold email sequence (draft, not sent) |
| `docs/fiverr-gigs.md` | Fiverr gig copy (draft, not published) |
| `docs/progress-log.md` | Running progress log (activity is not achievement) |
| `tools/ai_visibility_audit/` | The audit engine that produces the free personalised report |
| `site/index.html` | Landing page draft |

## Run the audit tool

```bash
cd tools/ai_visibility_audit
python3 audit.py --business "Acme Roofing" --domain acmeroofing.com \
  --trade roofer --city "Dallas, TX" --engine mock --out report.html   # free test run, SAMPLE DATA
pip install anthropic && export ANTHROPIC_API_KEY=...                 # real runs (about $1-2 per audit)
python3 audit.py ... --engine claude --out report.html
```
