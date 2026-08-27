from __future__ import annotations

import json
import os

import streamlit as st
from dotenv import load_dotenv
from pydantic import ValidationError

from sales_agent import SalesAgentOrchestrator, SalesRequest
from sales_agent.documents import extract_product_document
from sales_agent.quality import evaluate_brief
from sales_agent.rendering import brief_to_markdown

load_dotenv()

st.set_page_config(page_title="AccountLens AI", page_icon="🔎", layout="wide")
st.title("AccountLens AI")
st.caption("CAP 931 · Multi-agent sales intelligence prototype")

with st.sidebar:
    st.header("Run settings")
    has_key = bool(os.getenv("OPENAI_API_KEY"))
    demo_mode = st.toggle("Demonstration mode", value=not has_key)
    st.info(
        "Demo mode validates the complete interface and orchestration without "
        "making factual claims. Add OPENAI_API_KEY for live analysis."
    )

with st.form("sales_intake"):
    left, right = st.columns(2)
    with left:
        product_name = st.text_input("Product name", "SecureFlow Cloud")
        company_url = st.text_input("Prospect company URL", "https://www.microsoft.com")
        product_category = st.text_input("Product category", "Cloud security platform")
        competitor_text = st.text_area(
            "Competitor URLs (one per line)", "https://www.paloaltonetworks.com"
        )
        research_text = st.text_area(
            "Additional research URLs (one per line)",
            "",
            help=(
                "Add public press releases, leadership pages, annual reports, "
                "articles, or job postings for deeper evidence."
            ),
        )
    with right:
        value_proposition = st.text_area(
            "Value proposition",
            "Reduce cloud-security investigation time through unified visibility and automation.",
        )
        target_customer = st.text_input("Target customer", "Chief Information Security Officer")
        product_overview = st.text_area(
            "Optional product overview text",
            "SecureFlow Cloud centralizes alerts, prioritizes risk, and automates common response steps.",
        )
        product_file = st.file_uploader(
            "Optional product overview document",
            type=["pdf", "docx", "txt", "md"],
            help="Upload a PDF, DOCX, TXT, or Markdown product sheet/deck.",
        )
    submitted = st.form_submit_button("Generate account brief", type="primary")

if submitted:
    try:
        overview_parts = [product_overview.strip()] if product_overview.strip() else []
        if product_file is not None:
            extracted_text = extract_product_document(
                product_file.getvalue(), product_file.name
            )
            overview_parts.append(
                f"Uploaded product document ({product_file.name}):\n{extracted_text}"
            )

        request = SalesRequest(
            product_name=product_name,
            company_url=company_url,
            product_category=product_category,
            competitor_urls=[line.strip() for line in competitor_text.splitlines() if line.strip()],
            research_urls=[line.strip() for line in research_text.splitlines() if line.strip()],
            value_proposition=value_proposition,
            target_customer=target_customer,
            product_overview="\n\n".join(overview_parts),
        )
        if not demo_mode and not has_key:
            st.error("Add OPENAI_API_KEY to your .env file or enable demonstration mode.")
            st.stop()

        with st.spinner("Specialist agents are researching and synthesizing…"):
            brief, findings = SalesAgentOrchestrator(demo_mode=demo_mode).run(request)

        st.success("Account brief generated")
        quality = evaluate_brief(brief)
        one_pager = brief_to_markdown(request, brief)

        quality_left, quality_middle, quality_right = st.columns(3)
        quality_left.metric("Completeness", f"{quality.completeness_percent}%")
        quality_middle.metric("Unique sources", quality.unique_source_count)
        quality_right.metric("Quality status", quality.status)
        if quality.warnings:
            with st.expander("Quality review warnings", expanded=True):
                for warning in quality.warnings:
                    st.warning(warning)

        st.subheader(brief.prospect_name)
        st.write(brief.executive_summary)

        sections = [
            ("Company strategy", brief.company_strategy),
            ("Competitor intelligence", brief.competitor_mentions),
            ("Leadership information", brief.leadership_information),
            ("Product alignment", brief.product_alignment),
            ("Discovery questions", brief.discovery_questions),
            ("Risks and evidence gaps", brief.risks_and_gaps),
        ]
        for heading, items in sections:
            st.markdown(f"### {heading}")
            for item in items:
                st.markdown(f"- {item}")

        st.markdown("### Sources")
        for source in brief.sources:
            st.markdown(
                f"- [{source.source_title}]({source.source_url}) — "
                f"{source.claim} · confidence: {source.confidence}"
            )

        with st.expander("View specialist-agent outputs"):
            st.json([finding.model_dump() for finding in findings])

        st.download_button(
            "Download one-page brief (Markdown)",
            data=one_pager,
            file_name="account_brief.md",
            mime="text/markdown",
            type="primary",
        )
        report_json = json.dumps(brief.model_dump(), indent=2)
        st.download_button(
            "Download structured evidence (JSON)",
            data=report_json,
            file_name="account_brief.json",
            mime="application/json",
        )
    except (ValidationError, ValueError) as exc:
        st.error(f"Please correct the inputs: {exc}")
    except Exception as exc:
        st.error(f"The analysis could not be completed: {exc}")
