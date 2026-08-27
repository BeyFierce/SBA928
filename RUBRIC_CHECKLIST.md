# CAP 931 Rubric Checklist

| Criterion | Repository evidence |
|---|---|
| Technical Setup | `pyproject.toml`, `uv.lock`, `requirements.txt`, `.env.example`, Streamlit `app.py`, Dockerfile, and setup commands in README |
| Inputs Handling | All required fields in `app.py`; Pydantic validation; competitor and additional research URL lists; optional PDF/DOCX/TXT/MD parsing in `sales_agent/documents.py` |
| LLM Model Selection & Use | Four-agent chain, structured outputs, strengthened prompts, configurable model, and decision/experiment record in `EXPERIMENT_RESULTS.md` |
| Data Integration & Output Relevance | Bounded public-page extraction, extra primary-source inputs, separate specialist roles, Markdown one-pager, source links, quality checks, and `SAMPLE_ACCOUNT_BRIEF.md` |
| Optional Enhancements | Product document parsing, quality/readiness report, structured evidence download, demo mode, and additional-source workflow |
| Production Deployment | Dockerfile, health check, Streamlit config, and detailed scalability/security/maintenance/rollback plan in `DEPLOYMENT.md` |
| Documentation Quality | README, technical documentation, time allocation, challenges, experiment outcomes, sample output, deployment plan, tests, and this direct rubric map |

## Submission evidence

- GitHub branch: `cap931-accountlens`
- Main application: `app.py`
- Generated one-pager example: `SAMPLE_ACCOUNT_BRIEF.md`
- Automated verification: `uv run pytest -q`
- Secret handling: `.env` is ignored and no API key is stored in the repository.
