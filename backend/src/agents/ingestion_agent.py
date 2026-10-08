from src.agents.base_agent import BaseAgent
from src.utils.json_parser import parse_json_response
import json


class IngestionAgent(BaseAgent):
    def __init__(self):
        system_prompt = """You are an Ingestion Agent for Padhai Check, an Indian exam misinformation detection system.

Your ONLY job is to clean and prepare text. Output ONLY valid JSON, nothing else.

INPUT: Raw user text (may be Hindi, English, or Hinglish)

OUTPUT: Valid JSON with these exact fields (REQUIRED):
{
  "cleaned_text": "normalized text without extra spaces",
  "language": "English or Hindi or Hinglish or Mixed",
  "translated_text": "English version of text",
  "entities": ["JEE", "NEET", "NTA", "exam names", "important terms"],
  "dates_mentioned": ["any dates or deadlines"],
  "summary": "1-2 sentence summary"
}

RULES:
- Output ONLY the JSON object, nothing before or after
- No markdown, no code blocks, no explanation
- If Hindi/Hinglish, translate to English
- Extract education entities (JEE, NEET, CBSE, NTA, etc.)
- Remove extra spaces and normalize text

Example:
{"cleaned_text": "JEE Main 2024 exam dates announced", "language": "English", "translated_text": "JEE Main 2024 exam dates announced", "entities": ["JEE", "2024"], "dates_mentioned": [], "summary": "Information about JEE Main 2024 exam dates"}
"""
        super().__init__("IngestionAgent", system_prompt)

    def prepare_text(self, raw_text: str) -> dict:
        try:
            result = self.process(raw_text)
            parsed = parse_json_response(result)
            if parsed and isinstance(parsed, dict):
                # Validate required fields
                required_fields = ["cleaned_text", "language", "translated_text", "entities", "dates_mentioned", "summary"]
                if all(field in parsed for field in required_fields):
                    return parsed
        except Exception as e:
            print(f"IngestionAgent error: {e}")

        # Fallback: at least provide cleaned text
        return {
            "cleaned_text": raw_text.strip(),
            "language": "English",
            "translated_text": raw_text.strip(),
            "entities": [],
            "dates_mentioned": [],
            "summary": raw_text[:200]
        }
