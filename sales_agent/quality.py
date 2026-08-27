from __future__ import annotations

from dataclasses import asdict, dataclass

from .schemas import SalesBrief


@dataclass(frozen=True)
class QualityReport:
    status: str
    completeness_percent: int
    source_count: int
    unique_source_count: int
    low_confidence_sources: int
    warnings: list[str]

    def model_dump(self) -> dict[str, object]:
        return asdict(self)


def evaluate_brief(brief: SalesBrief) -> QualityReport:
    """Check structural readiness; this does not replace factual human review."""

    required_sections = {
        "executive summary": bool(brief.executive_summary.strip()),
        "company strategy": bool(brief.company_strategy),
        "competitor intelligence": bool(brief.competitor_mentions),
        "leadership information": bool(brief.leadership_information),
        "product alignment": bool(brief.product_alignment),
        "discovery questions": bool(brief.discovery_questions),
        "risks and evidence gaps": bool(brief.risks_and_gaps),
        "sources": bool(brief.sources),
    }
    completed = sum(required_sections.values())
    completeness = round(100 * completed / len(required_sections))
    warnings = [
        f"Missing required section: {name}."
        for name, present in required_sections.items()
        if not present
    ]

    source_urls = [item.source_url for item in brief.sources]
    unique_source_count = len(set(source_urls))
    low_confidence = sum(item.confidence == "low" for item in brief.sources)
    if unique_source_count < 2:
        warnings.append("Use at least two independent public sources when available.")
    if low_confidence:
        warnings.append(
            f"Review {low_confidence} low-confidence source item(s) before outreach."
        )
    if not brief.risks_and_gaps:
        warnings.append("Document evidence gaps and uncertainty before outreach.")

    status = "Ready for human review" if completeness == 100 else "Needs attention"
    return QualityReport(
        status=status,
        completeness_percent=completeness,
        source_count=len(source_urls),
        unique_source_count=unique_source_count,
        low_confidence_sources=low_confidence,
        warnings=warnings,
    )
