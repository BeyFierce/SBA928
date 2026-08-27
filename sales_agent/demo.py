from .schemas import AgentFinding, EvidenceItem, SalesBrief, SalesRequest


def demo_findings(request: SalesRequest, source_url: str, role: str) -> AgentFinding:
    evidence = EvidenceItem(
        claim=f"Demo evidence placeholder for the {role} workflow.",
        source_url=source_url,
        source_title="Demo source",
        confidence="low",
    )
    return AgentFinding(
        summary=f"{role} completed in demonstration mode for {request.product_name}.",
        findings=[
            "The multi-agent routing and structured-output pipeline are operational.",
            "Live factual findings require an API key and accessible public source pages.",
        ],
        evidence=[evidence],
        limitations=["Demonstration mode does not make factual claims about the prospect."],
    )


def demo_brief(request: SalesRequest, findings: list[AgentFinding]) -> SalesBrief:
    company = request.company_url.host or "Prospective account"
    sources = [item for finding in findings for item in finding.evidence]
    return SalesBrief(
        prospect_name=company,
        executive_summary=(
            f"Prototype demonstration for positioning {request.product_name} to "
            f"{request.target_customer}. Live mode will replace these placeholders "
            "with source-grounded account intelligence."
        ),
        company_strategy=["Pending live analysis of the supplied company URL."],
        competitor_mentions=["No competitor relationship is asserted in demo mode."],
        leadership_information=["Pending live, source-grounded leadership research."],
        product_alignment=[request.value_proposition],
        discovery_questions=[
            f"What outcomes are most important for your {request.product_category} strategy?",
            "Which current processes create the greatest cost or delay?",
            "How will leadership measure success for a new solution?",
        ],
        risks_and_gaps=["Live research and human verification are required before outreach."],
        sources=sources,
    )

