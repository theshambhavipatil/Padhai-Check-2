"""
Output Formatter for Padhai Check
Converts raw agent outputs into clean, well-structured, readable responses
"""
from typing import Dict, List, Any, Optional
import re


class OutputFormatter:
    """
    Formats agent outputs into clean, readable sections
    """

    @staticmethod
    def format_claim_result(result: Dict[str, Any], summary_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Format a claim result into clean sections
        Returns a structured dictionary with organized sections
        """
        formatted = {
            "sections": [],
            "summary": {},
            "metadata": {}
        }

        # ========== SECTION 0: QUICK SUMMARY (NEW!) ==========
        if summary_data:
            formatted["sections"].append({
                "type": "quick_summary",
                "title": "⚡ QUICK SUMMARY",
                "summary": summary_data.get('summary', ''),
                "key_point": summary_data.get('key_point', ''),
                "action": summary_data.get('action', ''),
                "severity": summary_data.get('severity', 'medium')
            })

        # ========== SECTION 1: WELLBEING (if needed) ==========
        if result.get('stress_detected') and result.get('wellbeing_message'):
            formatted["sections"].append({
                "type": "wellbeing",
                "title": "💪 WELLBEING SUPPORT",
                "subtitle": "Priority Message For You",
                "content": result.get('wellbeing_message', ''),
                "icon": "💪"
            })

        # ========== SECTION 2: VERDICT SUMMARY ==========
        verdict = result.get('verdict', 'Unverified')
        confidence = result.get('confidence', 0)

        verdict_colors = {
            "True": "#10b981",
            "False": "#ef4444",
            "Misleading": "#f59e0b",
            "Unverified": "#6b7280"
        }

        verdict_emojis = {
            "True": "✅",
            "False": "❌",
            "Misleading": "⚠️",
            "Unverified": "❓"
        }

        formatted["sections"].append({
            "type": "verdict",
            "title": "📋 VERDICT",
            "content": f"{verdict_emojis.get(verdict, '❓')} {verdict}",
            "confidence": confidence,
            "color": verdict_colors.get(verdict, "#6b7280")
        })

        # ========== SECTION 3: CLAIM ==========
        claim_text = result.get('claim', '')
        if claim_text and claim_text != "Wellbeing Support":
            formatted["sections"].append({
                "type": "claim",
                "title": "🎯 THE CLAIM",
                "content": claim_text
            })

        # ========== SECTION 4: EXPLANATION - PARSE INTO PARAGRAPHS ==========
        explanation = result.get('explanation_english', '')
        if explanation:
            # Parse the explanation into clean sections
            parsed_sections = OutputFormatter._parse_explanation_into_sections(explanation)
            formatted["sections"].extend(parsed_sections)

        # ========== SECTION 5: EVIDENCE ==========
        evidence = result.get('evidence', [])
        if evidence:
            formatted["sections"].append({
                "type": "evidence",
                "title": "📚 EVIDENCE FROM TRUSTED SOURCES",
                "items": [
                    {
                        "source": ev.get('source', 'Unknown'),
                        "url": ev.get('url'),
                        "snippet": ev.get('snippet', ''),
                        "reliability": ev.get('reliability_score', 0.8)
                    }
                    for ev in evidence
                ]
            })

        # ========== SECTION 6: HINGLISH EXPLANATION ==========
        hinglish = result.get('explanation_hinglish', '').strip()
        if hinglish and hinglish != result.get('wellbeing_message', ''):
            # Extract just the hinglish content, remove header markers
            hinglish_content = OutputFormatter._extract_hinglish_content(hinglish)
            if hinglish_content:
                formatted["sections"].append({
                    "type": "hinglish",
                    "title": "🇮🇳 हिंदी में / Hinglish में",
                    "content": hinglish_content
                })

        # ========== SUMMARY ==========
        formatted["summary"] = {
            "verdict": verdict,
            "confidence": confidence,
            "claim": claim_text,
            "hasStress": result.get('stress_detected', False),
            "evidenceCount": len(evidence),
            "category": result.get('category', 'Other')
        }

        # ========== METADATA ==========
        formatted["metadata"] = {
            "id": result.get('id'),
            "created_at": result.get('created_at'),
            "original_content": result.get('original_content', '')[:200]  # First 200 chars
        }

        return formatted

    @staticmethod
    def _parse_explanation_into_sections(explanation: str) -> List[Dict[str, Any]]:
        """
        Parse multi-section explanation into clean, organized sections
        Handles the FactCheckAgent output format
        """
        sections = []
        lines = explanation.split('\n')

        # Remove header lines with "=" symbols
        cleaned_lines = [line for line in lines if not line.startswith('=')]
        explanation_text = '\n'.join(cleaned_lines).strip()

        # Split by section headers (Official Stance, Media Analysis, etc.)
        patterns = [
            (r'Official\s+Stance[:\s]*(.*?)(?=Media\s+Analysis|Evidence\s+Evaluation|Implications|Context|$)', 'Official Stance'),
            (r'Media\s+Analysis[:\s]*(.*?)(?=Evidence\s+Evaluation|Implications|Context|$)', 'Media & Source Analysis'),
            (r'Evidence\s+Evaluation[:\s]*(.*?)(?=Implications|Context|$)', 'Evidence Evaluation'),
            (r'Implications[:\s]*(.*?)(?=Context|$)', 'Student Implications'),
            (r'Context[:\s]*(.*?)$', 'Context & Patterns'),
        ]

        found_sections = False
        for pattern, section_title in patterns:
            match = re.search(pattern, explanation_text, re.DOTALL | re.IGNORECASE)
            if match:
                found_sections = True
                content = match.group(1).strip()
                if content:
                    sections.append({
                        "type": "fact_check_subsection",
                        "title": f"📝 {section_title.upper()}",
                        "content": content
                    })

        # If structured parsing didn't work, treat as single fact-check section
        if not found_sections:
            sections.append({
                "type": "fact_check",
                "title": "📋 FACT-CHECK VERIFICATION",
                "content": explanation_text
            })
        else:
            # Wrap all subsections as part of fact-check
            if sections:
                sections.insert(0, {
                    "type": "fact_check",
                    "title": "📋 FACT-CHECK VERIFICATION",
                    "subsections": [s for s in sections]
                })
                sections = [sections[0]]

        return sections

    @staticmethod
    def _extract_hinglish_content(hinglish: str) -> str:
        """
        Extract clean hinglish content, removing headers and metadata
        """
        # Remove lines with equals signs and metadata
        lines = hinglish.split('\n')
        cleaned = [line.strip() for line in lines
                   if line.strip()
                   and not line.startswith('=')
                   and not 'हिंदी में' in line
                   and not 'Hinglish' in line]

        content = '\n'.join(cleaned).strip()
        return content if content else None

    @staticmethod
    def format_for_json(formatted_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ensure formatted result is JSON-serializable
        """
        return formatted_result

    @staticmethod
    def format_error(error_message: str, error_type: str = "error") -> Dict[str, Any]:
        """
        Format an error response
        """
        return {
            "sections": [
                {
                    "type": "error",
                    "title": "⚠️ ERROR",
                    "content": error_message,
                    "icon": "⚠️"
                }
            ],
            "summary": {
                "verdict": "Error",
                "error_type": error_type
            },
            "metadata": {}
        }
