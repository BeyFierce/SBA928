# CAP 931 Technical Documentation

## Project objective

Build a functional sales-assistant prototype that gives a new sales
representative source-grounded insight into a prospective account, its strategy,
leadership, and competitive landscape.

## Technical decisions

- **Python:** strong ecosystem support for LLMs, validation, scraping, and UI.
- **Streamlit:** creates a usable prototype without a separate front-end stack.
- **Pydantic structured outputs:** makes agent handoffs predictable and testable.
- **Specialist agents:** divides a broad research task into smaller prompts, then
  assigns a final agent to synthesize the one-page brief.
- **Evidence-first prompting:** reduces unsupported factual claims and requires
  the workflow to expose limitations.
- **Document parsing:** turns optional PDF, DOCX, TXT, or Markdown product
  material into bounded context without storing the uploaded file.
- **Deterministic quality review:** checks section completeness, source diversity,
  and low-confidence evidence before a brief is downloaded.

## Code structure

- `app.py` — Streamlit interface, validation messages, report display/download.
- `sales_agent/schemas.py` — typed input, specialist finding, evidence, and final
  brief models.
- `sales_agent/research.py` — validates and extracts bounded text from supplied
  public URLs.
- `sales_agent/documents.py` — extracts bounded text from optional product files.
- `sales_agent/prompts.py` — task-specific prompts and safety constraints.
- `sales_agent/llm.py` — structured OpenAI model call.
- `sales_agent/orchestrator.py` — routes work across specialists and synthesis.
- `sales_agent/demo.py` — testable no-cost demonstration path.
- `sales_agent/quality.py` — deterministic report-readiness checks.
- `sales_agent/rendering.py` — downloadable one-page Markdown generation.
- `tests/` — input, URL-safety, and demo-pipeline tests.

## Prompt-engineering approach

The first prompt layer gives all specialists the same grounding rules: use only
supplied sources, ignore instructions embedded in webpage text, cite factual
claims, and reveal evidence gaps. Each specialist then receives one bounded
role. The synthesis prompt receives structured findings rather than raw pages,
which reduces context size and makes its responsibility explicit.

## Challenges and solutions

1. **Hallucinated account facts** — require citations, typed evidence objects,
   limitations, and human verification.
2. **Inconsistent handoffs** — use Pydantic schemas instead of free-form text.
3. **Blocked or inaccessible websites** — return a retrieval error and prevent
   the model from treating missing data as evidence.
4. **API access during development** — provide demo mode so the UI and pipeline
   remain testable without a key.
5. **Prompt injection inside webpages** — tell agents to treat source text as
   untrusted evidence, never as instructions.
6. **Optional product sheets use several formats** — provide a single bounded
   parser for PDF, DOCX, TXT, and Markdown uploads.
7. **A valid schema can still contain weak evidence** — show source count,
   completeness, low-confidence warnings, and an explicit human-review status.

## Time management record

| Workstream | Allocation | Reason |
|---|---:|---|
| Requirements and architecture | 15% | Translate rubric into components |
| Interface and input validation | 20% | Ensure all required inputs are usable |
| Research and multi-agent workflow | 30% | Core technical functionality |
| Prompt experiments and safeguards | 15% | Improve relevance and reliability |
| Testing, documentation, demo | 20% | Make the project reproducible |

## Production deployment plan

The included Dockerfile and health check create a repeatable deployment unit.
Production should run stateless containers behind TLS and authentication, keep
the API key in a managed secret store, move slow jobs to a queue, and apply
per-user limits. Logs must redact product documents, customer data, prompts, and
responses. Public-content caching should expire quickly, and outbound requests
need redirect revalidation and a controlled egress policy. See `DEPLOYMENT.md`
for scalability, security, monitoring, maintenance, backup, and rollback details.

## Evaluation plan

Run at least three sample accounts and grade each output for source coverage,
unsupported claims, missing required sections, sales usefulness, latency, and
cost. Compare the multi-agent version to a single-prompt baseline and record
which approach produces the most reliable one-page brief.

Offline experiments completed during this revision cover typed vs. free-form
handoffs, chained vs. single-responsibility design, and evidence-first prompt
invariants. A live model A/B could not be completed because the account returned
HTTP 429 `insufficient_quota`; no results were fabricated. The exact methods,
observations, decision record, and next live test are in `EXPERIMENT_RESULTS.md`.

## Output package

- `SAMPLE_ACCOUNT_BRIEF.md` — sourced, human-reviewed example.
- Markdown download — concise one-page report for the sales representative.
- JSON download — structured evidence for audit or downstream integration.
- Specialist output expander — inspectable intermediate agent results.
- Quality panel — completeness, unique-source count, and review warnings.
