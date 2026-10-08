from src.agents.ingestion_agent import IngestionAgent
from src.agents.claim_agent import ClaimAgent
from src.agents.factcheck_agent import FactCheckAgent
from src.agents.explainability_agent import ExplainabilityAgent
from src.agents.wellbeing_agent import WellbeingAgent
from src.agents.trend_agent import TrendAgent
from src.agents.summarization_agent import SummarizationAgent
from src.models.schemas import ClaimResult, Verdict, Evidence
from typing import Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AgentOrchestrator:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if AgentOrchestrator._initialized:
            return
        self._ingestion_agent = None
        self._claim_agent = None
        self._factcheck_agent = None
        self._explainability_agent = None
        self._wellbeing_agent = None
        self._trend_agent = None
        self._summarization_agent = None
        AgentOrchestrator._initialized = True

    @property
    def ingestion_agent(self):
        if self._ingestion_agent is None:
            self._ingestion_agent = IngestionAgent()
        return self._ingestion_agent

    @property
    def claim_agent(self):
        if self._claim_agent is None:
            self._claim_agent = ClaimAgent()
        return self._claim_agent

    @property
    def factcheck_agent(self):
        if self._factcheck_agent is None:
            self._factcheck_agent = FactCheckAgent()
        return self._factcheck_agent

    @property
    def explainability_agent(self):
        if self._explainability_agent is None:
            self._explainability_agent = ExplainabilityAgent()
        return self._explainability_agent

    @property
    def wellbeing_agent(self):
        if self._wellbeing_agent is None:
            self._wellbeing_agent = WellbeingAgent()
        return self._wellbeing_agent

    @property
    def trend_agent(self):
        if self._trend_agent is None:
            self._trend_agent = TrendAgent()
        return self._trend_agent

    @property
    def summarization_agent(self):
        if self._summarization_agent is None:
            self._summarization_agent = SummarizationAgent()
        return self._summarization_agent

    def process_claim(self, content: str, extracted_text: Optional[str] = None) -> ClaimResult:
        text_to_process = extracted_text if extracted_text else content

        logger.info("Step 1: Wellbeing Agent - Check student wellbeing")
        wellbeing_data = self.wellbeing_agent.assess_wellbeing(content, "")

        stress_detected = wellbeing_data.get('stress_detected', False)
        wellbeing_msg = (wellbeing_data.get('message') or '').strip()

        logger.info("Step 2: Ingestion Agent - Preparing text")
        prepared_text = self.ingestion_agent.prepare_text(text_to_process)

        logger.info("Step 3: Claim Agent - Identifying claim")
        claim_data = self.claim_agent.identify_claim(prepared_text)

        # Check if this is ONLY a wellbeing message (no actual claim to verify)
        claim_text = claim_data.get('main_claim', '').strip()

        # If stress detected and NO meaningful claim extracted, return ONLY wellbeing message
        if stress_detected and wellbeing_msg and (not claim_text or claim_text == "Claim extraction failed" or len(claim_text) < 10):
            logger.info("WELLBEING ONLY - No factual claim detected, returning support message only")
            result = ClaimResult(
                original_content=content,
                extracted_text=extracted_text,
                claim="Wellbeing Support",
                verdict=Verdict.UNVERIFIED,
                confidence=1.0,
                explanation_english=wellbeing_msg,
                explanation_hinglish=wellbeing_msg,
                evidence=[],
                wellbeing_message=wellbeing_msg,
                stress_detected=True,
                category="WELLBEING"
            )
            return result

        logger.info("Step 4: Fact-Check Agent - Verifying claim")
        verdict_data = self.factcheck_agent.verify_claim(claim_data, prepared_text)

        logger.info("Step 5: Explainability Agent - Creating explanation")
        explanation_data = self.explainability_agent.create_explanation(claim_data, verdict_data)

        logger.info("Step 6: Trend Agent - Analyzing trends")
        trend_data = self.trend_agent.analyze_trend(claim_data, verdict_data)

        verdict_map = {
            "True": Verdict.TRUE,
            "False": Verdict.FALSE,
            "Misleading": Verdict.MISLEADING,
            "Unverified": Verdict.UNVERIFIED,
            "Unverifiable": Verdict.UNVERIFIED
        }
        verdict = verdict_map.get(verdict_data.get('verdict', 'Unverified'), Verdict.UNVERIFIED)

        # Build evidence list
        evidence_list = []
        if verdict_data.get('evidence'):
            for ev in verdict_data.get('evidence', []):
                evidence_list.append(Evidence(
                    source=ev.get('source', 'Unknown'),
                    url=ev.get('url'),
                    snippet=ev.get('snippet', ''),
                    reliability_score=ev.get('reliability_score', 0.8)
                ))
        elif explanation_data.get('evidence'):
            for ev in explanation_data.get('evidence', []):
                evidence_list.append(Evidence(
                    source=ev.get('source', 'Unknown'),
                    url=ev.get('url'),
                    snippet=ev.get('snippet', ''),
                    reliability_score=ev.get('reliability_score', 0.8)
                ))

        # Build output with CONDITIONAL wellbeing message
        final_explanation_parts = []

        # ========== WELLBEING MESSAGE ==========
        # NOTE: Wellbeing message is stored separately in wellbeing_message field
        # DO NOT include it in the explanation text to avoid duplication

        # ========== FACT-CHECK ARTICLE ==========
        # Start directly with content

        # CLAIM
        final_explanation_parts.append(claim_text)
        final_explanation_parts.append("")  # Single blank line

        # VERDICT
        verdict_word = verdict_data.get('verdict', 'Unverified')
        final_explanation_parts.append(f"**VERDICT: {verdict_word}**")
        final_explanation_parts.append("")  # Single blank line

        # EXPLANATION (from FactCheckAgent)
        factcheck_reasoning = verdict_data.get('reasoning', '')
        if factcheck_reasoning:
            final_explanation_parts.append(factcheck_reasoning)
        else:
            final_explanation_parts.append(f"This claim has been assessed as {verdict_word}. Please review the evidence below.")

        final_explanation_parts.append("")  # Single blank line

        # EVIDENCE - Only show if we have evidence
        if evidence_list:
            final_explanation_parts.append("**EVIDENCE FROM TRUSTED SOURCES:**")
            final_explanation_parts.append("")  # Blank line after header
            for ev in evidence_list:
                final_explanation_parts.append(f"**{ev.source}**")
                if ev.snippet:
                    final_explanation_parts.append(ev.snippet)
                if ev.url:
                    final_explanation_parts.append(f"🔗 {ev.url}")
                final_explanation_parts.append("")  # Blank line between evidence items

        # HINDI/HINGLISH EXPLANATION
        expl_hi = explanation_data.get('explanation_hinglish', '').strip()
        if expl_hi:
            final_explanation_parts.append("**🇮🇳 हिंदी में समझाइए / Hinglish में:**")
            final_explanation_parts.append("")  # Blank line after header
            final_explanation_parts.append(expl_hi)
            final_explanation_parts.append("")  # Blank line after content

        # TREND INFORMATION
        trend_summary = trend_data.get('trend_summary') or trend_data.get('pattern_description') or ''
        if trend_summary:
            final_explanation_parts.append("**📊 TRENDING PATTERN:**")
            final_explanation_parts.append("")  # Blank line after header
            final_explanation_parts.append(trend_summary)
            final_explanation_parts.append("")  # Blank line after content

        final_explanation = "\n".join(final_explanation_parts)

        result = ClaimResult(
            original_content=content,
            extracted_text=extracted_text,
            claim=claim_text,
            verdict=verdict,
            confidence=verdict_data.get('confidence', 0.5),
            explanation_english=final_explanation,
            explanation_hinglish=expl_hi or '',
            evidence=evidence_list,
            wellbeing_message=wellbeing_msg if stress_detected else None,
            stress_detected=stress_detected,
            category=trend_data.get('trend_category', claim_data.get('category'))
        )

        return result


orchestrator = AgentOrchestrator()
