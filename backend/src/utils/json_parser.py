import json
import re
from typing import Any, Dict


def parse_json_response(text: str) -> Dict[str, Any]:
    """
    Parse JSON from AI response, handling common formatting issues like
    markdown code blocks, extra whitespace, etc.
    """
    if not text:
        return {}
    
    cleaned = text.strip()
    
    patterns = [
        r'```json\s*([\s\S]*?)\s*```',
        r'```\s*([\s\S]*?)\s*```',
        r'`([\s\S]*?)`',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, cleaned)
        if match:
            cleaned = match.group(1).strip()
            break
    
    start_idx = cleaned.find('{')
    end_idx = cleaned.rfind('}')
    
    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        cleaned = cleaned[start_idx:end_idx + 1]
    
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
    
    try:
        cleaned = re.sub(r',\s*}', '}', cleaned)
        cleaned = re.sub(r',\s*]', ']', cleaned)
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
    
    return {}
