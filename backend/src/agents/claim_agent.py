from src.agents.base_agent import BaseAgent
from src.utils.json_parser import parse_json_response


class ClaimAgent(BaseAgent):
    def __init__(self):
        system_prompt = """You are the Claim Extraction Agent for Padhai Check.

Your ONLY job is to extract the main factual claim from text. Output ONLY valid JSON, nothing else.

INPUT: Prepared text with cleaning, summary, entities

OUTPUT: Valid JSON with these exact fields (REQUIRED):
{
  "main_claim": "the extracted main factual claim in neutral language",
  "category": "EXAM_DATES or PAPER_LEAK or RESULT_MANIPULATION or ADMISSION_SCAM or SCHOLARSHIP_FRAUD or OTHER",
  "urgency": "low or medium or high",
  "related_body": "NTA or CBSE or NCERT or UGC or AICTE or UNIVERSITY or UNKNOWN",
  "affected_exams": ["JEE", "NEET", etc],
  "requires_immediate_verification": true or false
}

RULES:
- Output ONLY the JSON object, nothing before or after
- Extract 1 main claim per response
- Restate in neutral, article-ready language
- Ignore opinions, emotions, narrative fluff
- Identify the category accurately
- Mark urgency based on potential harm (exam dates = high, scholarship = medium, etc)

Example:
{"main_claim": "JEE Main 2024 exam dates have been postponed", "category": "EXAM_DATES", "urgency": "high", "related_body": "NTA", "affected_exams": ["JEE"], "requires_immediate_verification": true}
"""
        super().__init__("ClaimAgent", system_prompt)

    def identify_claim(self, prepared_text: dict) -> dict:
        content = f"""
Cleaned Text: {prepared_text.get('cleaned_text', '')}
Summary: {prepared_text.get('summary', '')}
Entities: {', '.join(prepared_text.get('entities', []))}
Dates Mentioned: {', '.join(prepared_text.get('dates_mentioned', []))}

Extract the main claim and categorize it. Output ONLY JSON."""

        try:
            result = self.process(content)
            parsed = parse_json_response(result)
            if parsed and isinstance(parsed, dict):
                required_fields = ["main_claim", "category", "urgency", "related_body", "affected_exams"]
                if all(field in parsed for field in required_fields):
                    return parsed
        except Exception as e:
            print(f"ClaimAgent error: {e}")

        return {
            "main_claim": prepared_text.get('summary', 'Claim extraction failed'),
            "category": "OTHER",
            "urgency": "medium",
            "related_body": "UNKNOWN",
            "affected_exams": [],
            "requires_immediate_verification": False
        }
