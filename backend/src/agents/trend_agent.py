from src.agents.base_agent import BaseAgent
from src.utils.json_parser import parse_json_response


class TrendAgent(BaseAgent):
    def __init__(self):
        system_prompt = """You are a Trend Analysis Agent for Padhai Check.

Your ONLY job is to analyze misinformation patterns and provide DETAILED context. Output ONLY valid JSON.

OUTPUT: Valid JSON with these exact fields (REQUIRED):
{
  "trend_category": "EXAM_DATES or PAPER_LEAK or RESULT_MANIPULATION or ADMISSION_SCAM or SCHOLARSHIP_FRAUD or OTHER",
  "is_known_pattern": true or false,
  "pattern_description": "DETAILED description (4-6 sentences) of the misinformation pattern if known, including historical context",
  "related_claims": ["List of 3-5 related claims students should watch out for"],
  "seasonal_relevance": "DETAILED explanation (2-3 sentences) of seasonal timing and relevance",
  "spread_risk": "low or medium or high",
  "why_spreads": "DETAILED explanation (3-4 sentences) of why this type of misinformation spreads and how to identify it"
}

REQUIREMENTS:
- pattern_description: If known pattern, provide 4-6 sentences with historical context (NO decorative headers)
- seasonal_relevance: Explain 2-3 sentences about timing and why it matters now
- why_spreads: 3-4 sentences explaining psychological/social reasons for spread
- related_claims: List 3-5 specific related claims to watch for
- Assess spread_risk based on potential impact and current context
- NO decorative headers or emoji lines anywhere in JSON

Common misinformation patterns:
- Exam postponement rumors (creates panic, spreads on WhatsApp)
- Paper leak claims (appears before/after exams, creates fear)
- Fake circulars with official letterheads (mimics official communication)
- Result manipulation claims (targets anxious students)
- New rule/regulation fake news (exploits regulatory confusion)
- Admission scams and fake seat allotment (targets admission season)
- Scholarship fraud messages (targets students seeking financial aid)
- Fake website links mimicking official sites (exploits trust)

RULES:
- Output ONLY the JSON object (no text before/after)
- Clean, structured format
- No decorative formatting anywhere
- Provide rich context on patterns and seasonality
- Explain WHY misinformation spreads, not just WHAT spreads
"""
        super().__init__("TrendAgent", system_prompt)

    def analyze_trend(self, claim_data: dict, verdict_data: dict) -> dict:
        content = f"""
Claim: {claim_data.get('main_claim', '')}
Category: {claim_data.get('category', '')}
Verdict: {verdict_data.get('verdict', '')}
Related Body: {claim_data.get('related_body', '')}

Provide DETAILED trend analysis with historical context.
NO decorative headers or emoji lines.
Output ONLY JSON."""

        try:
            result = self.process(content)
            parsed = parse_json_response(result)
            if parsed and isinstance(parsed, dict):
                required_fields = ["trend_category", "is_known_pattern", "pattern_description", "related_claims", "seasonal_relevance", "spread_risk", "why_spreads"]
                if all(field in parsed for field in required_fields):
                    return parsed
        except Exception as e:
            print(f"TrendAgent error: {e}")

        return {
            "trend_category": claim_data.get('category', 'OTHER'),
            "is_known_pattern": False,
            "pattern_description": "Unable to determine pattern at this time. This claim requires further investigation.",
            "related_claims": [],
            "seasonal_relevance": "Unknown relevance to current exam season",
            "spread_risk": "medium",
            "why_spreads": "Misinformation spreads due to test anxiety and social media amplification of urgent claims."
        }
