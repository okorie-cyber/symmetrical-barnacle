# AI Visibility Audit

Measures whether AI answer engines name a local business, labelling each answer as **observed** (the real product) or **API approximation**. See `../../docs/technical-verification.md` for what each engine really measures, the costs, and the false-result safeguards.

```bash
P=../../data/prospects.csv
python3 audit.py prompts --prospects $P --runs 1 --out capture-sheet.csv        # manual capture sheet
python3 audit.py run --engine manual --prospects $P --input capture-sheet.csv --out evidence/manual.json
GEMINI_API_KEY=... python3 audit.py run --engine gemini --prospects $P --runs 3 --out evidence/gemini.json
SERPAPI_API_KEY=... python3 audit.py run --engine serpapi_ai_mode --prospects $P --runs 1 --out evidence/aimode.json
python3 audit.py report --prospects $P --evidence evidence/*.json --outdir reports
python3 audit.py drafts --prospects $P --evidence evidence/*.json --out drafts.md   # never sends anything
python3 -m unittest test_audit                                                   # 7 tests
```

Standard library only (Claude engine optional: `pip install anthropic`). The live API adapters are untested until the first keyed run.
