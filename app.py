from __future__ import annotations

import json
import os

import streamlit as st
from dotenv import load_dotenv
from pydantic import ValidationError

from sales_agent import SalesAgentOrchestrator, SalesRequest

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
    with right:
        value_proposition = st.text_area(
            "Value proposition",
            "Reduce cloud-security investigation time through unified visibility and automation.",
        )
        target_customer = st.text_input("Target customer", "Chief Information Security Officer")
        product_overview = st.text_area(
            "Optional product overview",
            "SecureFlow Cloud centralizes alerts, prioritizes risk, and automates common response steps.",
        )
    submitted = st.form_submit_button("Generate account brief", type="primary")

if submitted:
    try:
        request = SalesRequest(
            product_name=product_name,
            company_url=company_url,
            product_category=product_category,
            competitor_urls=[line.strip() for line in competitor_text.splitlines() if line.strip()],
            value_proposition=value_proposition,
            target_customer=target_customer,
            product_overview=product_overview,
        )
        if not demo_mode and not has_key:
            st.error("Add OPENAI_API_KEY to your .env file or enable demonstration mode.")
            st.stop()

        with st.spinner("Specialist agents are researching and synthesizing…"):
            brief, findings = SalesAgentOrchestrator(demo_mode=demo_mode).run(request)

        st.success("Account brief generated")
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

        report_json = json.dumps(brief.model_dump(), indent=2)
        st.download_button(
            "Download account brief (JSON)",
            data=report_json,
            file_name="account_brief.json",
            mime="application/json",
        )
    except (ValidationError, ValueError) as exc:
        st.error(f"Please correct the inputs: {exc}")
    except Exception as exc:
        st.error(f"The analysis could not be completed: {exc}")

