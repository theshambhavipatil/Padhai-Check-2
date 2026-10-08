"""
Summarization Agent for Padhai Check
Creates concise, one-line summaries of claims and verdicts
"""
from src.agents.base_agent import BaseAgent
from src.utils.json_parser import parse_json_response


class SummarizationAgent(BaseAgent):
    def __init__(self):
        system_prompt = """You are the Summarization Agent for Padhai Check.

Your ONLY job is to create SHORT, CONCISE, ONE-LINE summaries of claims and their verdicts.

INPUT: Claim, verdict, and brief context

OUTPUT: Valid JSON with these exact fields (REQUIRED):
{
  "summary": "One clear sentence summarizing the claim and verdict (15-20 words max)",
  "key_point": "One key fact to remember (10-15 words max)",
  "action": "One actionable item for students (10-15 words max)",
  "severity": "low or medium or high - how urgent/important is this"
}

RULES:
- Output ONLY the JSON object, nothing else
- Make summaries SHORT and PUNCHY
- Use simple language
- Include the verdict implicitly (True=correct, False=incorrect, Misleading=partially true)
- Make it memorable and shareable
- NO decorative headers or emoji lines
- NO formatting characters or special symbols

IMPORTANT:
- Keep all text fields CLEAN and SIMPLE
- No decorative separators or lines
- No emoji or special symbols
- Professional but student-friendly tone
- Direct and clear language

Examples of CORRECT output:

Input: Claim="JEE exam conducted 7 times per year", Verdict="False"
Output: {"summary": "JEE Main is held twice yearly (January & April), not seven times.", "key_point": "Official NTA schedule shows only 2 sessions per academic year.", "action": "Check jeemain.nta.nic.in for official exam dates before planning.", "severity": "medium"}

Input: Claim="JEE can be attempted 7 times", Verdict="False"
Output: {"summary": "Maximum 6 attempts allowed: 2 per year over 3 consecutive years.", "key_point": "After 12th, students get 3 years to attempt JEE twice yearly.", "action": "Plan your preparation knowing you have exactly 6 official attempts.", "severity": "high"}

Input: Claim="NTA changed JEE attempt rules", Verdict="Unverified"
Output: {"summary": "No official confirmation yet. Always verify with NTA before believing.", "key_point": "Rumors about rule changes are common during exam season.", "action": "Subscribe to official NTA notifications for real updates.", "severity": "medium"}
"""
        super().__init__("SummarizationAgent", system_prompt)

    def create_summary(self, claim_data: dict, verdict_data: dict) -> dict:
        """
        Create a concise summary of the claim and verdict
        """
        content = f"""
Claim: {claim_data.get('main_claim', '')}
Verdict: {verdict_data.get('verdict', 'Unverified')}
Category: {claim_data.get('category', '')}
Related Body: {claim_data.get('related_body', '')}

Create a SHORT, one-line summary with key point and action.
NO decorative headers or special symbols.
Output ONLY JSON."""

        try:
            result = self.process(content)
            parsed = parse_json_response(result)
            if parsed and isinstance(parsed, dict):
                required_fields = ["summary", "key_point", "action", "severity"]
                if all(field in parsed for field in required_fields):
                    return parsed
        except Exception as e:
            print(f"SummarizationAgent error: {e}")

        return {
            "summary": f"Claim about {claim_data.get('main_claim', 'this topic')} is {verdict_data.get('verdict', 'unverified')}.",
            "key_point": "Always verify claims with official sources before sharing.",
            "action": "Check official government/examination board websites for accurate information.",
            "severity": "medium"
        }
