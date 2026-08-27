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

## Code structure

- `app.py` — Streamlit interface, validation messages, report display/download.
- `sales_agent/schemas.py` — typed input, specialist finding, evidence, and final
  brief models.
- `sales_agent/research.py` — validates and extracts bounded text from supplied
  public URLs.
- `sales_agent/prompts.py` — task-specific prompts and safety constraints.
- `sales_agent/llm.py` — structured OpenAI model call.
- `sales_agent/orchestrator.py` — routes work across specialists and synthesis.
- `sales_agent/demo.py` — testable no-cost demonstration path.
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

## Time management record

| Workstream | Allocation | Reason |
|---|---:|---|
| Requirements and architecture | 15% | Translate rubric into components |
| Interface and input validation | 20% | Ensure all required inputs are usable |
| Research and multi-agent workflow | 30% | Core technical functionality |
| Prompt experiments and safeguards | 15% | Improve relevance and reliability |
| Testing, documentation, demo | 20% | Make the project reproducible |

## Production deployment plan

Deploy the Streamlit app in a managed container or Streamlit Community Cloud.
Keep the API key in a managed secret store rather than source control. Add user
authentication, request limits, logging with sensitive-data redaction, source
allow/deny policies, monitoring, and automated tests. Cache safe public content
with expiration to reduce cost. A production research service should support
JavaScript-rendered pages and honor site access rules.

## Evaluation plan

Run at least three sample accounts and grade each output for source coverage,
unsupported claims, missing required sections, sales usefulness, latency, and
cost. Compare the multi-agent version to a single-prompt baseline and record
which approach produces the most reliable one-page brief.

