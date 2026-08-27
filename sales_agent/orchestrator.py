from __future__ import annotations

import json

from .demo import demo_brief, demo_findings
from .llm import StructuredLLM
from .prompts import COMPANY_PROMPT, COMPETITOR_PROMPT, LEADERSHIP_PROMPT, SYNTHESIS_PROMPT
from .research import WebDocument, WebResearcher
from .schemas import AgentFinding, SalesBrief, SalesRequest


class SalesAgentOrchestrator:
    """Coordinates three research specialists and one synthesis agent."""

    def __init__(self, demo_mode: bool = False):
        self.demo_mode = demo_mode
        self.researcher = WebResearcher()
        self.llm = None if demo_mode else StructuredLLM()

    def run(self, request: SalesRequest) -> tuple[SalesBrief, list[AgentFinding]]:
        urls = list(
            dict.fromkeys(
                [
                    str(request.company_url),
                    *map(str, request.competitor_urls),
                    *map(str, request.research_urls),
                ]
            )
        )
        documents = [self.researcher.fetch(url) for url in urls]

        if self.demo_mode:
            roles = ["Company Strategy Analyst", "Competitive Intelligence Analyst", "Leadership Analyst"]
            findings = [demo_findings(request, urls[0], role) for role in roles]
            return demo_brief(request, findings), findings

        context = self._context(request, documents)
        assert self.llm is not None
        findings = [
            self.llm.run(COMPANY_PROMPT, context, AgentFinding),
            self.llm.run(COMPETITOR_PROMPT, context, AgentFinding),
            self.llm.run(LEADERSHIP_PROMPT, context, AgentFinding),
        ]
        synthesis_input = json.dumps(
            {"request": request.model_dump(mode="json"), "specialist_findings": [x.model_dump() for x in findings]},
            indent=2,
        )
        brief = self.llm.run(SYNTHESIS_PROMPT, synthesis_input, SalesBrief)
        return brief, findings

    @staticmethod
    def _context(request: SalesRequest, documents: list[WebDocument]) -> str:
        payload = {
            "sales_request": request.model_dump(mode="json"),
            "sources": [doc.__dict__ for doc in documents],
        }
        return json.dumps(payload, indent=2)
