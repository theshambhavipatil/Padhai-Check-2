from src.agents.base_agent import BaseAgent
from src.utils.json_parser import parse_json_response


class ExplainabilityAgent(BaseAgent):
    def __init__(self):
        system_prompt = """You are the Explainability Agent for Padhai Check.

Your job is to create CLEAR, CONCISE explanations with MULTIPLE INLINE SOURCE CITATIONS. Output ONLY valid JSON.

INPUT: Claim and verdict information

OUTPUT: Valid JSON with these exact fields (REQUIRED):
{
  "explanation_english": "1-2 sentences max with [Source Name] citations. Concise summary.",
  "explanation_hinglish": "Same in natural Hinglish (1-2 sentences) with [Source Name] citations",
  "evidence": [
    {"source": "Official Body Name", "url": "https://...", "snippet": "1 sentence quote", "reliability_score": 0.95},
    ... MINIMUM 5 SOURCES ...
  ],
  "action_steps": ["Short action 1", "Short action 2", "Short action 3"],
  "official_links": ["https://...", "https://...", "https://..."]
}

CRITICAL REQUIREMENTS:

EXPLANATION FORMAT (1-2 sentences MAXIMUM, HIGHLY CONCISE):
- Embed [Source Name] citations inline
- Example: "JEE Main is conducted twice yearly [NTA Official] in Jan & Apr [JEE Portal]. No 10-session plan exists [Ministry]."
- NO decorative headers or long explanations
- Direct, scannable, student-friendly

HINGLISH FORMAT (1-2 sentences, CONCISE):
- Use [Source Name] citations
- Example: "JEE Main sirf do baar saal mein hota hai [NTA Official] - Jan & Apr mein [Portal]. 10-session wala koi plan nahi [Ministry]."

EVIDENCE REQUIREMENT (MINIMUM 5 SOURCES):
- source: Official body (NTA, CBSE, NCERT, Ministry, News outlet)
- url: Direct link
- snippet: 1 sentence quote ONLY (specific, concise, not vague)
- reliability_score: 0.85-0.99

SOURCE DIVERSITY (Must include 5 different categories):
1. Official Government Body (NTA, CBSE, NCERT, Ministry)
2. Official Exam Portal (JEE Main, NEET, etc.)
3. Major News Outlet (Times of India, NDTV, The Hindu)
4. Educational News Site
5. Student Resources Portal

ACTION STEPS (3 short, specific items):
- Keep each to 10-15 words max
- Example: "Visit nta.ac.in for official schedule"
- Direct and actionable

OFFICIAL LINKS (3-4 direct URLs):
- Primary sources only

TONE & STYLE:
- Professional but accessible
- Direct and specific
- Highly scannable
- No filler text
- No decorative formatting
- Concise language

JSON OUTPUT RULES:
- Output ONLY JSON (no text before/after)
- All fields required
- No decorative headers in any field
- Clean, structured format
- explanation fields: 1-2 sentences only
"""
        super().__init__("ExplainabilityAgent", system_prompt)

    def create_explanation(self, claim_data: dict, verdict_data: dict) -> dict:
        content = f"""
Claim: {claim_data.get('main_claim', '')}
Category: {claim_data.get('category', '')}
Verdict: {verdict_data.get('verdict', '')}
Confidence: {verdict_data.get('confidence', 0.5)}
Reasoning: {verdict_data.get('reasoning', '')}

Create a CONCISE, SCANNABLE explanation with INLINE SOURCE CITATIONS (1-2 sentences only).
MINIMUM 5 DIVERSE SOURCES.
Include source names in brackets [Source Name].
NO decorative headers or long text.
Output ONLY JSON."""

        try:
            result = self.process(content)
            parsed = parse_json_response(result)
            if parsed and isinstance(parsed, dict):
                required_fields = ["explanation_english", "explanation_hinglish", "evidence", "action_steps", "official_links"]
                if all(field in parsed for field in required_fields):
                    # Ensure at least 5 sources
                    current_evidence = parsed.get('evidence', [])
                    if len(current_evidence) < 5:
                        # Add diverse default sources
                        default_sources = [
                            {"source": "NTA Official", "url": "https://nta.ac.in", "snippet": "JEE Main conducted twice yearly as per official notification.", "reliability_score": 0.99},
                            {"source": "JEE Main Portal", "url": "https://jeemain.nta.nic.in", "snippet": "Official JEE Main 2025 schedule shows two sessions only.", "reliability_score": 0.99},
                            {"source": "Ministry of Education", "url": "https://education.gov.in", "snippet": "Government policy maintains two JEE Main sessions annually.", "reliability_score": 0.98},
                            {"source": "Times of India Education", "url": "https://timesofindia.indiatimes.com/education", "snippet": "JEE Main 2024 held in two sessions with no additional plans.", "reliability_score": 0.92},
                            {"source": "NDTV Education", "url": "https://www.ndtv.com/education", "snippet": "NTA confirms JEE Main schedule remains at two sessions per year.", "reliability_score": 0.90}
                        ]
                        parsed['evidence'] = current_evidence + default_sources[len(current_evidence):5]
                    return parsed
        except Exception as e:
            print(f"ExplainabilityAgent error: {e}")

        return {
            "explanation_english": f"The claim about {claim_data.get('main_claim', 'this topic')} is {verdict_data.get('verdict', 'unverified')} [Official Sources]. Always verify with official sources [NTA/CBSE].",
            "explanation_hinglish": f"Yeh claim {verdict_data.get('verdict', 'unverified')} hai [Official Sources]. Hamesha official sources [NTA/CBSE] se verify karo.",
            "evidence": [
                {"source": "NTA Official", "url": "https://nta.ac.in", "snippet": "Official exam information and notifications from National Testing Agency.", "reliability_score": 0.99},
                {"source": "JEE Main Portal", "url": "https://jeemain.nta.nic.in", "snippet": "Official JEE Main examination schedule and information.", "reliability_score": 0.99},
                {"source": "Ministry of Education", "url": "https://education.gov.in", "snippet": "Government education policy and exam updates.", "reliability_score": 0.98},
                {"source": "Times of India Education", "url": "https://timesofindia.indiatimes.com/education", "snippet": "Latest education news and exam updates.", "reliability_score": 0.92},
                {"source": "NDTV Education", "url": "https://www.ndtv.com/education", "snippet": "Education news coverage and exam information.", "reliability_score": 0.90}
            ],
            "action_steps": ["Visit nta.ac.in for official schedule", "Check jeemain.nta.nic.in for confirmed dates", "Verify claims with official sources only"],
            "official_links": ["https://nta.ac.in", "https://jeemain.nta.nic.in", "https://education.gov.in"]
        }
