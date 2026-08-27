# AccountLens AI — CAP 931

AccountLens AI is a Python and Streamlit prototype that uses a multi-agent GPT
workflow to help a sales representative research a prospective account and
prepare for discovery.

## What it does

1. Collects the product, prospect URL, category, competitor URLs, value
   proposition, target customer, and optional product overview.
2. Downloads text from the user-supplied public pages.
3. Routes the evidence to three specialist agents:
   - Company Strategy Analyst
   - Competitive Intelligence Analyst
   - Leadership Research Analyst
4. Sends the structured findings to a Sales Strategy Lead agent.
5. Displays and downloads a one-page account brief with evidence and sources.

The system treats webpage text as untrusted data, requires sourced factual
claims, labels uncertainty, and does not assert competitor usage without proof.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Add your OpenAI API key to `.env`, then run:

```bash
streamlit run app.py
```

The interface starts in demonstration mode when no API key is present. Demo
mode exercises the full UI, validation, agent-routing, and report-rendering
pipeline without making factual claims or incurring API charges.

## Test

```bash
python -m pytest -q
```

## Sample output

See [`SAMPLE_ACCOUNT_BRIEF.md`](SAMPLE_ACCOUNT_BRIEF.md) for a sourced,
human-reviewed example of the one-page deliverable produced by the workflow.

## Model decision

The default is `gpt-4o-mini` because it supports structured output while
balancing speed and cost for a classroom prototype. Set `OPENAI_MODEL` in
`.env` to test another compatible model. The Pydantic schemas constrain each
agent's output so that downstream report generation receives predictable data.

## Architecture

```text
Streamlit intake
    -> URL collection and cleaning
    -> Company Strategy Analyst
    -> Competitive Intelligence Analyst
    -> Leadership Research Analyst
    -> Sales Strategy Lead
    -> sourced one-page brief
```

## Experiments to document

- Compare one large prompt with the specialist-agent workflow.
- Compare a short prompt with the guarded, evidence-first prompts.
- Compare output consistency with free-form text versus Pydantic schemas.
- Record latency, factual errors, missing fields, and usefulness to a sales rep.

## Known limitations

- Some websites block automated retrieval or render content with JavaScript.
- A URL alone cannot prove that a prospect uses a competitor.
- LLM output still requires human review before customer outreach.
- The prototype does not crawl private sources, social profiles, or paywalls.
- Production use would require authentication, rate limiting, audit logs,
  encrypted secret storage, monitoring, and a more robust retrieval layer.

## Optional enhancements

- PDF or product-deck upload and parsing.
- Scheduled alerts for new press releases and job postings.
- DOCX/PDF one-pager export.
- CRM integration and saved account history.
- Production deployment with managed secrets and role-based access.
