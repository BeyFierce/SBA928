from typing import Literal

from pydantic import BaseModel, Field, HttpUrl


class SalesRequest(BaseModel):
    product_name: str = Field(min_length=2)
    company_url: HttpUrl
    product_category: str = Field(min_length=2)
    competitor_urls: list[HttpUrl] = Field(default_factory=list)
    research_urls: list[HttpUrl] = Field(
        default_factory=list,
        description=(
            "Optional public evidence pages such as press releases, leadership "
            "pages, annual reports, and job postings."
        ),
    )
    value_proposition: str = Field(min_length=5)
    target_customer: str = Field(min_length=2)
    product_overview: str = ""


class EvidenceItem(BaseModel):
    claim: str
    source_url: str
    source_title: str
    confidence: Literal["high", "medium", "low"]


class AgentFinding(BaseModel):
    summary: str
    findings: list[str]
    evidence: list[EvidenceItem]
    limitations: list[str]


class SalesBrief(BaseModel):
    prospect_name: str
    executive_summary: str
    company_strategy: list[str]
    competitor_mentions: list[str]
    leadership_information: list[str]
    product_alignment: list[str]
    discovery_questions: list[str]
    risks_and_gaps: list[str]
    sources: list[EvidenceItem]
