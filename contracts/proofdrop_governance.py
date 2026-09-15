# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
"""Proofdrop Governance — Studio Next Intelligent Contract.

The contract evaluates a public task-evidence URL with GenLayer validators,
then stores the agreed judgment and a deterministic audit record. It never
transfers tokens or executes treasury actions; it records a decision proposal
that a community can inspect before a separate settlement contract is added.
"""

import json
from genlayer import *


class ProofdropGovernance(gl.Contract):
    # Persistent audit state. These fields are intentionally small and easy to
    # inspect in Studio Next's state panel.
    evaluation_count: u256
    last_task_id: str
    last_participant: str
    last_evidence_url: str
    last_score: u256
    last_eligible: bool
    last_judgment: str
    recorded_scores: TreeMap[str, u256]
    recorded_eligibility: TreeMap[str, bool]

    def __init__(self):
        self.evaluation_count = 0
        self.last_task_id = ""
        self.last_participant = ""
        self.last_evidence_url = ""
        self.last_score = 0
        self.last_eligible = False
        self.last_judgment = "not_evaluated"
        self.recorded_scores = TreeMap[str, u256]()
        self.recorded_eligibility = TreeMap[str, bool]()

    @gl.public.view
    def get_policy(self) -> str:
        return json.dumps(
            {
                "quality_weight": 60,
                "completion_weight": 30,
                "speed_weight": 10,
                "eligibility_threshold": 60,
                "max_token_proposal": 100,
                "settlement": "proposal_only",
            },
            sort_keys=True,
        )

    @gl.public.view
    def get_last_evaluation(self) -> str:
        return json.dumps(
            {
                "task_id": self.last_task_id,
                "participant": self.last_participant,
                "evidence_url": self.last_evidence_url,
                "score": self.last_score,
                "eligible": self.last_eligible,
                "judgment": self.last_judgment,
                "evaluation_count": self.evaluation_count,
            },
            sort_keys=True,
        )

    @gl.public.view
    def get_task_evaluation(self, task_id: str) -> str:
        if task_id not in self.recorded_scores:
            return json.dumps({"task_id": task_id, "found": False}, sort_keys=True)
        return json.dumps(
            {
                "task_id": task_id,
                "found": True,
                "score": self.recorded_scores[task_id],
                "eligible": self.recorded_eligibility[task_id],
            },
            sort_keys=True,
        )

    @gl.public.write
    def evaluate_task_evidence(
        self,
        task_id: str,
        participant: str,
        evidence_url: str,
        task_claim: str,
    ) -> str:
        """Reach validator consensus on public evidence, then persist the result."""
        if not task_id or not participant or not evidence_url or not task_claim:
            raise ValueError("task_id, participant, evidence_url, and task_claim are required")
        if not evidence_url.startswith("https://"):
            raise ValueError("evidence_url must use https://")

        def read_evidence():
            page = gl.nondet.web.render(evidence_url, mode="html")
            return page[:12000]

        # All validators must agree on the fetched public evidence before the
        # judgment is formed. This prevents a single validator from evaluating
        # a different page snapshot.
        evidence_html = gl.eq_principle.strict_eq(read_evidence)

        prompt = f"""
You are evaluating a task submission for Proofdrop's public governance policy.
Return JSON only with integer fields score (0-100), eligible (boolean), and a
short reason string. A submission is eligible only when the evidence visibly
supports the task claim and the score is at least 60.
Task claim: {task_claim}
Public evidence HTML:
{evidence_html}
"""

        judgment = gl.eq_principle.prompt_non_comparative(
            input=prompt,
            task="Evaluate whether the evidence supports the claim.",
            criteria="Return valid JSON with score, eligible, and reason. Score must be 0-100.",
        )
        parsed = json.loads(judgment)
        score = int(parsed["score"])
        eligible = bool(parsed["eligible"]) and score >= 60
        if score < 0 or score > 100:
            raise ValueError("validator score must be between 0 and 100")

        # Persistent writes happen only after the consensus-backed result is
        # available. No funds, wallets, or external contracts are touched.
        self.evaluation_count += 1
        self.last_task_id = task_id
        self.last_participant = participant
        self.last_evidence_url = evidence_url
        self.last_score = score
        self.last_eligible = eligible
        self.last_judgment = parsed.get("reason", "consensus judgment recorded")
        self.recorded_scores[task_id] = score
        self.recorded_eligibility[task_id] = eligible
        return self.get_last_evaluation()
