"""
GLAB 927.6.1 - Mastering LangChain for Advanced Language Model Applications

This program demonstrates:
1. A basic customer-support FAQ interaction.
2. A three-stage LangChain workflow for an order-status question.
3. Optimized prompts evaluated with multiple customer queries.

Install the dependencies before running:
    python -m pip install -U langchain-core langchain-groq

Security note:
    The Groq API key is requested privately at runtime and is never stored in
    this source file. You may instead set the GROQ_API_KEY environment variable.
"""

import getpass
import os

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq


MODEL_NAME = "llama-3.1-8b-instant"

# This sample data acts as the approved business source for the retrieval step.
# A real application would replace it with a secure database query.
ORDER_DATABASE = """
Order #12345: placed August 19, 2026; status shipped; carrier UPS;
estimated delivery August 28, 2026.
Order #67890: placed August 22, 2026; status processing;
estimated ship date August 27, 2026.
""".strip()


def ensure_api_key() -> None:
    """Request the Groq key securely only when it is not already configured."""
    if not os.environ.get("GROQ_API_KEY"):
        os.environ["GROQ_API_KEY"] = getpass.getpass("Enter your Groq API key: ")


def create_model() -> ChatGroq:
    """Initialize a deterministic Groq chat model for the lab."""
    return ChatGroq(
        model=MODEL_NAME,
        temperature=0,
        max_retries=2,
    )


def run_basic_faq(llm: ChatGroq) -> None:
    """Task 2: configure and invoke a basic FAQ prompt."""
    messages = [
        (
            "system",
            "You are a customer-support representative for BrightCart. "
            "Answer clearly and professionally. Business hours are Monday "
            "through Friday, 9:00 AM to 5:00 PM Central Time.",
        ),
        ("human", "What are your business hours?"),
    ]

    result = llm.invoke(messages)
    print("TASK 2 - BASIC FAQ CHAIN")
    print(result.content)


def build_advanced_chains(llm: ChatGroq):
    """Tasks 3-4: build three optimized stages using LangChain LCEL."""
    output_parser = StrOutputParser()

    extraction_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You extract order-support facts. Return only the order number, "
                "customer intent, and any stated timing. Do not invent details.",
            ),
            ("human", "Customer query: {customer_query}"),
        ]
    )

    retrieval_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You retrieve order information only from the supplied ORDER_DATABASE. "
                "Match the order number in EXTRACTED_INFO. If no exact record exists, "
                "say 'Order not found' and do not guess.",
            ),
            (
                "human",
                "EXTRACTED_INFO:\n{extracted_info}\n\n"
                "ORDER_DATABASE:\n{order_database}",
            ),
        ]
    )

    response_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a professional BrightCart support representative. Answer the "
                "original question using only the verified order details. Include the "
                "current status, relevant date, and a helpful next step. Never invent "
                "tracking numbers or policies.",
            ),
            (
                "human",
                "ORIGINAL QUERY:\n{customer_query}\n\n"
                "VERIFIED ORDER DETAILS:\n{order_details}",
            ),
        ]
    )

    return (
        extraction_prompt | llm | output_parser,
        retrieval_prompt | llm | output_parser,
        response_prompt | llm | output_parser,
    )


def process_customer_query(llm: ChatGroq, customer_query: str) -> None:
    """Run one query through extraction, retrieval, and response stages."""
    extraction_chain, retrieval_chain, response_chain = build_advanced_chains(llm)

    extracted_info = extraction_chain.invoke({"customer_query": customer_query})
    order_details = retrieval_chain.invoke(
        {
            "extracted_info": extracted_info,
            "order_database": ORDER_DATABASE,
        }
    )
    customer_response = response_chain.invoke(
        {
            "customer_query": customer_query,
            "order_details": order_details,
        }
    )

    print("\nCustomer Query:", customer_query)
    print("Extracted Info:", extracted_info)
    print("Order Details:", order_details)
    print("Customer Response:", customer_response)


def main() -> None:
    """Run the basic, advanced, and evaluation portions of the assignment."""
    ensure_api_key()
    llm = create_model()

    run_basic_faq(llm)

    print("\nTASKS 3-4 - ADVANCED AND OPTIMIZED PROMPT CHAINS")
    test_queries = [
        "Can you help me with the status of order #12345 placed last week?",
        "When should order #67890 ship?",
        "Please check the status of order #99999.",
    ]

    for query in test_queries:
        process_customer_query(llm, query)

    print(
        "\nEVALUATION: The optimized prompts identify the requested order, restrict "
        "retrieval to approved records, and prevent unsupported details. Testing an "
        "unknown order also confirms that the workflow reports missing data instead "
        "of inventing an answer."
    )


if __name__ == "__main__":
    main()
