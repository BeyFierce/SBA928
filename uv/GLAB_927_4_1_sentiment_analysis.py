"""
GLAB 927.4.1 - Hands-On Sentiment Analysis With Python

This program uses TextBlob to measure the polarity and subjectivity of
customer feedback, classify each comment, and summarize the overall trend.

Install the dependency before running:
    python -m pip install textblob
"""

from collections import Counter
from textblob import TextBlob


def sentiment_label(polarity: float) -> str:
    """Convert a TextBlob polarity score into a readable category."""
    if polarity > 0:
        return "Positive"
    if polarity < 0:
        return "Negative"
    return "Neutral"


def analyze_sentiment(text: str) -> dict[str, float | str]:
    """Return polarity, subjectivity, and a sentiment label for text."""
    sentiment = TextBlob(text).sentiment
    return {
        "polarity": sentiment.polarity,
        "subjectivity": sentiment.subjectivity,
        "label": sentiment_label(sentiment.polarity),
    }


def main() -> None:
    """Complete Tasks 1-3 and print actionable business insights."""
    # Task 1: Confirm that TextBlob is installed and imported.
    sample_text = "TextBlob is successfully installed and ready to use!"
    print("TASK 1 - IMPORTING TEXTBLOB")
    print(f"TextBlob library successfully imported. Sample text: {sample_text}\n")

    # Task 2: Analyze one positive product review.
    product_review = (
        "I absolutely love this product! The quality is excellent "
        "and it arrived on time."
    )
    review_result = analyze_sentiment(product_review)

    print("TASK 2 - SAMPLE SENTIMENT ANALYSIS")
    print(f"Original Text: {product_review}")
    print(f"Polarity: {review_result['polarity']:.3f}")
    print(f"Subjectivity: {review_result['subjectivity']:.3f}")
    print(f"Classification: {review_result['label']}\n")

    # Task 3: Analyze several customer feedback comments.
    feedback_comments = [
        "The service was fantastic and the staff was very helpful.",
        "I am unhappy with the product quality and delivery was delayed.",
        "The product is okay, but it could be improved.",
        "Amazing experience! I am very satisfied with my purchase.",
    ]

    results = []
    print("TASK 3 - CUSTOMER FEEDBACK ANALYSIS")
    for number, comment in enumerate(feedback_comments, start=1):
        result = analyze_sentiment(comment)
        results.append(result)
        print(f"\nFeedback {number}: {comment}")
        print(f"Polarity: {result['polarity']:.3f}")
        print(f"Subjectivity: {result['subjectivity']:.3f}")
        print(f"Classification: {result['label']}")

    # Evaluation: summarize the results and turn them into business insights.
    counts = Counter(str(result["label"]) for result in results)
    average_polarity = sum(float(result["polarity"]) for result in results) / len(results)

    print("\nEVALUATION AND BUSINESS INSIGHTS")
    print(f"Positive comments: {counts['Positive']}")
    print(f"Neutral comments: {counts['Neutral']}")
    print(f"Negative comments: {counts['Negative']}")
    print(f"Average polarity: {average_polarity:.3f}")
    print(
        "Insight: Customers frequently praise the staff and overall experience, "
        "while product quality and delivery delays need attention. The company "
        "should preserve its service strengths and prioritize delivery reliability "
        "and product-quality improvements."
    )


if __name__ == "__main__":
    main()
