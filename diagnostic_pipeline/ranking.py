from collections import defaultdict
from typing import Dict, List

from .models import BugCandidate, EvidenceInstance, RuleHit


SOURCE_WEIGHT = {
    'SanitizerRunner': 1.00,
    'ClangStaticAnalyzer': 0.94,
    'clang-tidy': 0.82,
    'ClangAST': 0.76,
    'LocalSandboxRunner': 0.72,
}


class BugRankingEngine:
    def rank(self, rule_hits: List[RuleHit], evidence: List[EvidenceInstance]) -> List[BugCandidate]:
        evidence_by_id: Dict[str, List[EvidenceInstance]] = defaultdict(list)
        for item in evidence:
            evidence_by_id[item.evidence_id].append(item)
        bug_hits: Dict[str, List[RuleHit]] = defaultdict(list)
        for hit in rule_hits:
            for bug_id in hit.bug_ids:
                bug_hits[bug_id].append(hit)
        candidates: List[BugCandidate] = []
        for bug_id, hits in bug_hits.items():
            collected: List[EvidenceInstance] = []
            evidence_strength = 0.0
            for hit in hits:
                for eid in hit.matched_evidence_ids:
                    instances = evidence_by_id.get(eid, [])
                    collected.extend(instances)
                    for item in instances:
                        evidence_strength += item.confidence * SOURCE_WEIGHT.get(item.source, 0.65)
            evidence_strength = min(1.0, evidence_strength)
            rule_score = max((h.confidence for h in hits), default=0.0)
            concept_bonus = 0.04 if any(h.matched_concept_ids for h in hits) else 0.0
            multi_source_bonus = 0.04 if len({e.source for e in collected}) > 1 else 0.0
            score = min(1.0, 0.50 * rule_score + 0.42 * evidence_strength + concept_bonus + multi_source_bonus)
            candidates.append(BugCandidate(bug_id, round(score, 4), hits, collected))
        return sorted(candidates, key=lambda x: x.score, reverse=True)
