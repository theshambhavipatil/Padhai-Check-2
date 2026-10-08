from src.agents.base_agent import BaseAgent
from src.utils.json_parser import parse_json_response


class FactCheckAgent(BaseAgent):
    def __init__(self):
        system_prompt = """You are the FACT-CHECK WRITER for Padhai Check.

Your job is to produce CLEAN, CONCISE, HIGHLY READABLE fact-checks. Output ONLY plain text with **bold** formatting for key points.

OUTPUT FORMAT (EXACT):
Claim: [The exact claim]
Verdict: [True OR False OR Misleading OR Unverified OR Unverifiable]


**OFFICIAL STANCE**
[1-2 sentences MAXIMUM - summarize concisely with [source] citations. Bold important terms and names.]


**MEDIA REPORTS**
[1-2 sentences MAXIMUM - summarize concisely with [source] citations. Bold media outlet names.]


**WHY THIS VERDICT**
[1-2 sentences MAXIMUM - clear reasoning. Bold the key reason.]


**WHAT YOU SHOULD DO**
[1-2 sentences MAXIMUM - actionable advice. Bold action items.]


**OFFICIAL SOURCES:**
• https://[URL 1]
• https://[URL 2]
• https://[URL 3]

CRITICAL REQUIREMENTS:
✓ ONE blank line between each section (single \\n after content)
✓ Maximum 1-2 sentences per section (NO long paragraphs)
✓ BOLD important terms using **bold text** format
✓ BOLD section headers
✓ Use [Source Name] citations inline
✓ Direct, scannable format
✓ Student-friendly language

FORMATTING RULES:
- Use **text** to bold important points (exam names, organizations, key facts, action items)
- Section headers must be bold: **SECTION NAME**
- One blank line between sections
- Links must be full URLs (starting with https://)

EXAMPLE OUTPUT:

Claim: JEE will be conducted 10 times in 2025
Verdict: False


**OFFICIAL STANCE**
**JEE Main** is conducted **twice yearly** (January & April) per **NTA** official policy [nta.ac.in]. No official announcement exists about changing this schedule [Ministry of Education].


**MEDIA REPORTS**
**Times of India**, **NDTV**, and **The Hindu** confirmed JEE Main 2024 had only two sessions [news outlets]. All major media verified this against official sources.


**WHY THIS VERDICT**
**NTA policy** clearly states two annual sessions for maintaining **exam integrity** [official documents]. The claim of 10 sessions has **no official basis** and contradicts established policy.


**WHAT YOU SHOULD DO**
Always check **nta.ac.in** and **jeemain.nta.nic.in** for official exam schedules. **Never trust unverified social media claims** about exam frequency changes.


**OFFICIAL SOURCES:**
• https://nta.ac.in
• https://jeemain.nta.nic.in
• https://education.gov.in

SUMMARIZATION RULES (MANDATORY):
- If you have 3-4 paragraphs worth of info → Compress to 1-2 sentences
- Combine related points into single sentences
- Remove redundant information
- Focus on KEY facts only
- NO filler words or repetition
- Bold the most important 3-5 terms per section

DO NOT:
× Write long paragraphs (max 2 sentences!)
× Repeat information across sections
× Use vague statements
× Add decorative formatting (= signs, boxes)
× Exceed 2 sentences per section
× Show duplicate official sources

REMEMBER: Short. Concise. Scannable. Bold key points. One blank line between sections."""
        super().__init__("FactCheckAgent", system_prompt)

    def verify_claim(self, claim_data: dict, prepared_text: dict) -> dict:
        content = f"""
Main Claim: {claim_data.get('main_claim', '')}
Category: {claim_data.get('category', '')}
Related Body: {claim_data.get('related_body', '')}
Affected Exams: {', '.join(claim_data.get('affected_exams', []))}
Original Text Summary: {prepared_text.get('summary', '')}

Produce a CONCISE, SCANNABLE fact-check:
- Maximum 1-2 sentences per section
- Extra blank lines between sections
- [Source Name] citations inline
- 4 main sections: OFFICIAL STANCE, MEDIA REPORTS, WHY THIS VERDICT, WHAT YOU SHOULD DO
- 3 official source URLs at end
- NO decorative headers or long paragraphs
- Make it easy to read and scan quickly"""

        try:
            result = self.process(content)

            # Parse plain text output
            parsed = self._parse_plaintext_factcheck(result, claim_data)
            if parsed:
                return parsed
        except Exception as e:
            print(f"FactCheckAgent error: {e}")

        return {
            "verdict": "Unverified",
            "confidence": 0.5,
            "reasoning": f"Unable to verify: {claim_data.get('main_claim', 'Unknown claim')}. Check official sources: NTA [nta.ac.in], CBSE [cbse.gov.in], Ministry of Education [education.gov.in].",
            "red_flags": [],
            "official_sources_to_check": ["https://nta.ac.in", "https://cbse.gov.in", "https://education.gov.in"],
            "explanation": f"Claim verification in progress. Please verify with official government sources."
        }

    def _parse_plaintext_factcheck(self, text: str, claim_data: dict) -> dict:
        """Parse plain text fact-check output"""
        if not text:
            return None

        lines = text.strip().split('\n')
        if len(lines) < 2:
            return None

        # Extract claim line (looking for "Claim:" prefix)
        claim = claim_data.get('main_claim', 'Unknown')
        verdict = "Unverified"

        # Find verdict line
        for i, line in enumerate(lines):
            line_upper = line.strip().upper()
            if "VERDICT:" in line_upper:
                verdict_text = line.replace("Verdict:", "").replace("VERDICT:", "").strip().upper()
                valid_verdicts = ["TRUE", "FALSE", "MISLEADING", "UNVERIFIED", "UNVERIFIABLE"]
                for v in valid_verdicts:
                    if v in verdict_text:
                        verdict = v.capitalize() if v != "UNVERIFIABLE" else "Unverifiable"
                        break
                break

        # Extract explanation (skip header lines and join rest)
        explanation_start = 0
        for i, line in enumerate(lines):
            if "VERDICT:" in line.upper():
                explanation_start = i + 1
                break

        explanation_lines = lines[explanation_start:] if explanation_start < len(lines) else []
        explanation = '\n'.join(explanation_lines).strip() if explanation_lines else ""

        # Confidence based on verdict
        confidence_map = {
            "True": 0.9,
            "False": 0.85,
            "Misleading": 0.8,
            "Unverified": 0.5,
            "Unverifiable": 0.3
        }
        confidence = confidence_map.get(verdict, 0.5)

        return {
            "verdict": verdict,
            "confidence": confidence,
            "reasoning": explanation,
            "red_flags": [],
            "official_sources_to_check": ["https://nta.ac.in", "https://cbse.gov.in", "https://education.gov.in"],
            "explanation": explanation
        }
