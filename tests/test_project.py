from pydantic import ValidationError

from sales_agent.demo import demo_brief, demo_findings
from sales_agent.research import WebResearcher
from sales_agent.schemas import SalesRequest


def sample_request() -> SalesRequest:
    return SalesRequest(
        product_name="SecureFlow Cloud",
        company_url="https://example.com",
        product_category="Cloud security",
        competitor_urls=["https://competitor.example.com"],
        value_proposition="Reduce investigation time with unified security visibility.",
        target_customer="CISO",
    )


def test_request_validation():
    request = sample_request()
    assert request.company_url.host == "example.com"


def test_invalid_url_rejected():
    try:
        SalesRequest(
            product_name="Test",
            company_url="not-a-url",
            product_category="Security",
            value_proposition="A useful value proposition",
            target_customer="CISO",
        )
    except ValidationError:
        return
    raise AssertionError("Invalid URL should fail validation")


def test_local_url_blocked():
    try:
        WebResearcher._validate_url("http://localhost:8501")
    except ValueError:
        return
    raise AssertionError("Local URLs should be blocked")


def test_demo_pipeline():
    request = sample_request()
    finding = demo_findings(request, str(request.company_url), "Company Analyst")
    brief = demo_brief(request, [finding])
    assert brief.prospect_name == "example.com"
    assert brief.discovery_questions

