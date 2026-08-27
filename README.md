# AccountLens AI — CAP 931

AccountLens AI is a functional Python and Streamlit sales-assistant prototype.
It uses a four-agent GPT workflow to turn public account evidence and an
optional product document into a concise, sourced one-page sales brief.

## Rubric-ready features

- All required Streamlit inputs: product, prospect URL, category, competitor
  URLs, value proposition, and target customer.
- Optional PDF, DOCX, TXT, or Markdown product-sheet/deck parsing.
- Additional evidence URLs for annual reports, press releases, leadership
  pages, articles, and job postings.
- Three specialist agents plus a Sales Strategy Lead synthesis agent.
- Evidence-first prompts, structured Pydantic handoffs, uncertainty labels,
  source links, and prompt-injection constraints.
- Downloadable Markdown one-pager and structured JSON evidence.
- Automated completeness, source-diversity, and confidence checks.
- No-cost demonstration mode and a human-reviewed sample output.
- Reproducible `uv` and `pip` setup, automated tests, Docker deployment files,
  and a production operations plan.

## Workflow

1. Collect and validate the sales context and public URLs.
2. Extract bounded text from public webpages and the optional product document.
3. Route the evidence to three specialist agents:
   - Company Strategy Analyst
   - Competitive Intelligence Analyst
   - Leadership Research Analyst
4. Send their typed findings to the Sales Strategy Lead.
5. Validate and render a sourced account one-pager for human review.

The system treats webpage text as untrusted data, requires sourced factual
claims, labels uncertainty, and never infers competitor usage from category
similarity alone.

## Quick start with uv

Prerequisites: Python 3.11+ and [`uv`](https://docs.astral.sh/uv/).

```bash
uv sync
cp .env.example .env
uv run streamlit run app.py
```

Add an OpenAI API key to `.env` for live research. Do not commit `.env`.
Without a key, keep **Demonstration mode** enabled to test the complete
interface, validation, orchestration, quality review, and downloads at no cost.

## Alternative pip setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
streamlit run app.py
```

## Test

```bash
uv run pytest -q
```

## Input guidance

For a strong live brief, provide the prospect homepage plus two or more focused
research URLs. Primary sources are preferred: annual reports, investor releases,
official leadership pages, security or strategy announcements, and relevant job
postings. Competitor URLs are comparison evidence; they do not prove that the
prospect uses that competitor.

The optional product upload accepts `.pdf`, `.docx`, `.txt`, and `.md` files.
Extracted content is limited to 20,000 characters to control context size and
cost.

## Sample output

[`SAMPLE_ACCOUNT_BRIEF.md`](SAMPLE_ACCOUNT_BRIEF.md) is a sourced,
human-reviewed example of the required one-page deliverable. It is clearly
labeled illustrative and must be reverified before outreach.

## Model decision

The default is `gpt-4o-mini` because the classroom prototype benefits from its
structured-output support and favorable speed/cost profile. The model is
configurable with `OPENAI_MODEL`, allowing a higher-capability compatible model
for difficult synthesis tasks. Pydantic schemas constrain every handoff so the
report renderer receives predictable fields regardless of the chosen model.

See [`EXPERIMENT_RESULTS.md`](EXPERIMENT_RESULTS.md) for the completed offline
experiments, model decision record, and the honestly documented API-quota limit
on live A/B testing.

## Repository guide

- `app.py` — Streamlit interface, document upload, validation, report display,
  quality checks, and downloads.
- `sales_agent/research.py` — public webpage retrieval and bounded extraction.
- `sales_agent/documents.py` — PDF, DOCX, TXT, and Markdown parsing.
- `sales_agent/prompts.py` — specialist and synthesis prompts.
- `sales_agent/llm.py` — structured OpenAI model call.
- `sales_agent/orchestrator.py` — four-agent routing and synthesis.
- `sales_agent/quality.py` — deterministic output-readiness checks.
- `sales_agent/rendering.py` — one-page Markdown renderer.
- `sales_agent/schemas.py` — typed requests, evidence, findings, and final brief.
- `tests/` — validation, security, parsing, rendering, and workflow tests.
- `DEPLOYMENT.md` — scalability, security, maintenance, and rollback plan.
- `CAPSTONE_DOCUMENTATION.md` — design, time management, and challenges.
- `RUBRIC_CHECKLIST.md` — direct map from all seven grading criteria to evidence.

## Known limitations

- Some sites block automated retrieval or render important content with
  JavaScript.
- Public URLs cannot establish private technology usage, buying intent, budget,
  or authority.
- File parsing extracts text only; charts and images are not interpreted.
- LLM output requires source review before customer outreach.
- Demo mode proves workflow behavior but intentionally makes no prospect claims.

## Production

The included Dockerfile runs the prototype as a container. Production use still
requires managed secrets, authenticated users, rate limits, outbound URL policy,
monitoring, audit logs, safe caching, and an approved deployment environment.
The complete operational design is in [`DEPLOYMENT.md`](DEPLOYMENT.md).
