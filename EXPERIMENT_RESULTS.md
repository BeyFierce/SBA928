# Prompt and Model Experiment Record

## Purpose

The experiments test whether structured handoffs and evidence-first prompting
make the prototype safer and more reproducible. Results below distinguish work
that was executed locally from live-model tests that could not be completed.

## Experiment 1 — Free-form output vs. Pydantic schemas

**Question:** Does typed output make downstream one-page generation more
reliable than accepting arbitrary model text?

**Method:** Construct complete and incomplete finding/brief objects and run the
test suite. The renderer receives only validated `SalesBrief` objects.

**Observed outcome:** Complete objects render every required section. Invalid
input URLs, unsupported confidence labels, and incomplete structures are
rejected before synthesis or rendering. This is deterministic and repeatable;
the relevant tests are in `tests/test_project.py`.

**Decision:** Keep Pydantic at every agent boundary even though it adds schema
maintenance, because predictable fields are more valuable than free-form
flexibility for a sales document.

## Experiment 2 — One broad prompt vs. specialist chaining

**Question:** Should one model prompt research everything, or should bounded
specialists feed a separate synthesis stage?

**Method:** Compare the responsibilities and testability of a single broad task
with three constrained roles: company strategy, competitor intelligence, and
leadership research. Run the offline demo to verify that each role returns an
independent typed finding and that synthesis receives only structured findings.

**Observed outcome:** The chained design exposes three auditable intermediate
results in the Streamlit expander and prevents the final renderer from depending
on raw webpage text. A single prompt would be shorter, but it would mix evidence
collection, competitor inference, leadership identification, and writing in one
uninspectable step.

**Decision:** Use the specialist chain for clarity and traceability. A live
quality A/B remains future work and is not represented as completed.

## Experiment 3 — Broad instructions vs. evidence-first guardrails

**Question:** Which prompt design better constrains unsupported claims?

**Method:** Add explicit instructions to use only supplied text, treat page
content as data rather than instructions, cite factual claims, separate facts
from hypotheses, and state evidence gaps. Automated tests verify that these
guardrail phrases remain present in the research prompt.

**Observed outcome:** The prompt package now has explicit, testable invariants
for citations, competitor-use claims, uncertainty, and prompt injection. The
human-reviewed sample follows the same rules by clearly distinguishing facts,
hypotheses, and missing evidence.

**Decision:** Retain the evidence-first prompt chain and human-review warning.

## Model selection record

| Model option | Accuracy/capability | Speed/cost | Prototype decision |
|---|---|---|---|
| `gpt-4o-mini` | Suitable for constrained extraction and structured output | Faster and lower-cost relative option | Default for all four stages |
| Configurable higher-capability compatible model | Better candidate for difficult synthesis | Typically slower and more expensive | Set with `OPENAI_MODEL` for targeted evaluation |

The same schema and prompt constraints apply regardless of the compatible model
selected. A production system could use the lower-cost model for extraction and
reserve a stronger model for final synthesis when a quality threshold is not met.

## Constraint encountered

A live model comparison was attempted during development, but the OpenAI account
returned HTTP 429 `insufficient_quota`. No live scores or model outputs have been
invented. Demo mode, deterministic tests, and the sourced human-reviewed sample
allow the prototype to remain inspectable while preserving this limitation.

## Next live evaluation

When API quota is available, run three accounts through both configurations and
record source coverage, unsupported claims, missing sections, usefulness rating,
latency, and estimated cost. Keep the same URLs and scoring sheet for a fair
comparison.
