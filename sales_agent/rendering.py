from __future__ import annotations

from .schemas import SalesBrief, SalesRequest


def _bullets(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items) or "- No supported finding available."


def brief_to_markdown(request: SalesRequest, brief: SalesBrief) -> str:
    """Render the structured result as a concise, shareable account one-pager."""

    sources = "\n".join(
        f"- [{item.source_title}]({item.source_url}) — {item.claim} "
        f"(confidence: {item.confidence})"
        for item in brief.sources
    ) or "- No sources were returned; do not use this brief for outreach."

    return f"""# Account Brief: {brief.prospect_name}

**Product:** {request.product_name}  
**Category:** {request.product_category}  
**Target customer:** {request.target_customer}  
**Human review required:** Verify all claims and sources before customer outreach.

## Executive summary

{brief.executive_summary}

## Company strategy

{_bullets(brief.company_strategy)}

## Competitor intelligence

{_bullets(brief.competitor_mentions)}

## Leadership information

{_bullets(brief.leadership_information)}

## Product alignment

{_bullets(brief.product_alignment)}

## Discovery questions

{_bullets(brief.discovery_questions)}

## Risks and evidence gaps

{_bullets(brief.risks_and_gaps)}

## Sources

{sources}
"""
