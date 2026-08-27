# Locked NLP GLabs — uv project

This folder contains the completed code for the two Canvas assignments that
were locked before they could be uploaded:

- **GLAB 927.4.1:** Hands-on Sentiment Analysis with Python
- **GLAB 927.6.1:** Mastering LangChain for Advanced Language Model Applications

Both scripts are fully commented. The project includes `pyproject.toml` and
`uv.lock` so the environment can be reproduced with `uv`.

## Install

From this `uv` folder, run:

```bash
uv sync --locked
```

## Run GLAB 927.4.1

```bash
uv run python GLAB_927_4_1_sentiment_analysis.py
```

The script prints polarity, subjectivity, sentiment classifications, a summary,
and actionable business insights.

## Run GLAB 927.6.1

```bash
uv run python GLAB_927_6_1_langchain_groq.py
```

Set `GROQ_API_KEY` in your environment or enter the key securely when prompted.
The key is never stored in this repository. The script demonstrates a basic FAQ
interaction, a three-stage LangChain workflow, optimized prompts, and multiple
evaluation queries.

## Security

No API key, password, or other secret is included in this folder.
