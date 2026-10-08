from typing import Dict, List, Optional
from datetime import datetime
from collections import defaultdict
import uuid
from src.models.schemas import ClaimResult, TrendingClaim, Verdict


class InMemoryStorage:
    def __init__(self):
        self.claims: Dict[str, ClaimResult] = {}
        self.uploaded_files: Dict[str, dict] = {}
        self.claim_counts: Dict[str, int] = defaultdict(int)
        self.claim_first_seen: Dict[str, datetime] = {}
        self.claim_last_seen: Dict[str, datetime] = {}
        self.claim_verdicts: Dict[str, Verdict] = {}
        self.claim_categories: Dict[str, str] = {}
        self.history: List[dict] = []  # NEW: Track verification history
        self.total_claims = 0
    
    def store_claim(self, claim_result: ClaimResult) -> str:
        self.claims[claim_result.id] = claim_result
        
        claim_key = claim_result.claim.lower().strip()
        self.claim_counts[claim_key] += 1
        self.claim_last_seen[claim_key] = datetime.utcnow()
        self.claim_verdicts[claim_key] = claim_result.verdict
        
        if claim_key not in self.claim_first_seen:
            self.claim_first_seen[claim_key] = datetime.utcnow()
        
        if claim_result.category:
            self.claim_categories[claim_key] = claim_result.category
        
        self.total_claims += 1
        
        # NEW: Add to history
        history_item = {
            "id": claim_result.id,
            "query": claim_result.claim,
            "verdict": claim_result.verdict,
            "timestamp": claim_result.created_at.isoformat(),
            "hasImage": claim_result.extracted_text is not None and len(claim_result.extracted_text) > 0
        }
        self.history.insert(0, history_item)  # Add to front (most recent first)

        # Keep only last 100 items
        if len(self.history) > 100:
            self.history = self.history[:100]

        return claim_result.id
    
    def get_claim(self, claim_id: str) -> Optional[ClaimResult]:
        return self.claims.get(claim_id)
    
    def store_file(self, file_id: str, filename: str, content_type: str, extracted_text: str) -> None:
        self.uploaded_files[file_id] = {
            "filename": filename,
            "content_type": content_type,
            "extracted_text": extracted_text,
            "uploaded_at": datetime.utcnow()
        }
    
    def get_file(self, file_id: str) -> Optional[dict]:
        return self.uploaded_files.get(file_id)
    
    # NEW: Get verification history
    def get_history(self, limit: int = 50) -> List[dict]:
        """Returns recent verification history"""
        return self.history[:limit]

    def get_trending_claims(self, limit: int = 10) -> List[TrendingClaim]:
        sorted_claims = sorted(
            self.claim_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]
        
        trending = []
        for claim_key, count in sorted_claims:
            if count >= 1:
                trending.append(TrendingClaim(
                    claim=claim_key,
                    verdict=self.claim_verdicts.get(claim_key, Verdict.UNVERIFIED),
                    count=count,
                    first_seen=self.claim_first_seen.get(claim_key, datetime.utcnow()),
                    last_seen=self.claim_last_seen.get(claim_key, datetime.utcnow()),
                    category=self.claim_categories.get(claim_key)
                ))
        
        return trending
    
    def get_most_common_category(self) -> Optional[str]:
        if not self.claim_categories:
            return None
        
        category_counts = defaultdict(int)
        for category in self.claim_categories.values():
            category_counts[category] += 1
        
        if category_counts:
            return max(category_counts.items(), key=lambda x: x[1])[0]
        return None


storage = InMemoryStorage()
