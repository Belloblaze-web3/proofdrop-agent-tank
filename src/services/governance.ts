export type TaskEvidence = {
  participant: string;
  taskId: string;
  completed: boolean;
  qualityScore: number;
  durationSeconds: number;
  evidenceUrl?: string;
};

export type GrantProposal = {
  proposalId: string;
  applicant: string;
  requestedAmount: number;
  impact: number;
  feasibility: number;
  openness: number;
  communityBenefit: number;
  evidenceUrl?: string;
};

export type DaoMember = { address: string; votingPower: number };
export type DaoProposal = {
  proposalId: string;
  strategy: string;
  requestedCapital: number;
  expectedReturnBps: number;
  riskBps: number;
  rationale: string;
};

export const PUBLIC_CRITERIA = {
  taskAirdrop: {
    qualityWeight: 0.6,
    completionWeight: 0.3,
    speedWeight: 0.1,
    maxTokensPerTask: 100,
  },
  grants: {
    impactWeight: 0.35,
    feasibilityWeight: 0.25,
    opennessWeight: 0.2,
    communityBenefitWeight: 0.2,
    minimumScore: 70,
  },
  investmentDao: {
    quorumBps: 5000,
    maxRiskBps: 2500,
    maxCapitalPerProposalBps: 2000,
  },
} as const;

function boundedScore(value: number, field: string): number {
  if (!Number.isFinite(value) || value < 0 || value > 100) {
    throw new Error(`${field} must be a number from 0 to 100`);
  }
  return value;
}

function positiveAmount(value: number, field: string): number {
  if (!Number.isFinite(value) || value <= 0) throw new Error(`${field} must be greater than zero`);
  return value;
}

export function evaluateTask(evidence: TaskEvidence): {
  participant: string;
  taskId: string;
  eligible: boolean;
  score: number;
  tokenAmount: number;
  reason: string;
} {
  if (!evidence.participant || !evidence.taskId) throw new Error("participant and taskId are required");
  const quality = boundedScore(evidence.qualityScore, "qualityScore");
  if (!Number.isFinite(evidence.durationSeconds) || evidence.durationSeconds <= 0) throw new Error("durationSeconds must be greater than zero");
  const completion = evidence.completed ? 100 : 0;
  const speed = Math.max(0, Math.min(100, 100 - Math.log10(evidence.durationSeconds + 1) * 25));
  const score = quality * PUBLIC_CRITERIA.taskAirdrop.qualityWeight + completion * PUBLIC_CRITERIA.taskAirdrop.completionWeight + speed * PUBLIC_CRITERIA.taskAirdrop.speedWeight;
  const eligible = evidence.completed && score >= 60;
  return {
    participant: evidence.participant,
    taskId: evidence.taskId,
    eligible,
    score: Number(score.toFixed(2)),
    tokenAmount: eligible ? Number((PUBLIC_CRITERIA.taskAirdrop.maxTokensPerTask * score / 100).toFixed(2)) : 0,
    reason: eligible ? "Completed task met the public quality threshold" : "Task was incomplete or below the public quality threshold",
  };
}

export function scoreGrant(proposal: GrantProposal) {
  if (!proposal.proposalId || !proposal.applicant) throw new Error("proposalId and applicant are required");
  const impact = boundedScore(proposal.impact, "impact");
  const feasibility = boundedScore(proposal.feasibility, "feasibility");
  const openness = boundedScore(proposal.openness, "openness");
  const communityBenefit = boundedScore(proposal.communityBenefit, "communityBenefit");
  const requestedAmount = positiveAmount(proposal.requestedAmount, "requestedAmount");
  const score = impact * PUBLIC_CRITERIA.grants.impactWeight + feasibility * PUBLIC_CRITERIA.grants.feasibilityWeight + openness * PUBLIC_CRITERIA.grants.opennessWeight + communityBenefit * PUBLIC_CRITERIA.grants.communityBenefitWeight;
  const approved = score >= PUBLIC_CRITERIA.grants.minimumScore;
  return {
    proposalId: proposal.proposalId,
    applicant: proposal.applicant,
    score: Number(score.toFixed(2)),
    approved,
    disbursementPlan: approved ? { requestedAmount, status: "proposed_unsubmitted", requiresCommunityApproval: true } : { requestedAmount: 0, status: "rejected_by_public_criteria", requiresCommunityApproval: false },
  };
}

export function simulateInvestmentDao(proposal: DaoProposal, members: DaoMember[], votes: Record<string, boolean>, treasuryBalance: number) {
  if (!proposal.proposalId || !proposal.strategy || !proposal.rationale) throw new Error("proposalId, strategy, and rationale are required");
  const requestedCapital = positiveAmount(proposal.requestedCapital, "requestedCapital");
  if (!Number.isFinite(treasuryBalance) || treasuryBalance < 0) throw new Error("treasuryBalance must be non-negative");
  if (!Number.isFinite(proposal.expectedReturnBps) || !Number.isFinite(proposal.riskBps)) throw new Error("expectedReturnBps and riskBps must be numbers");
  const totalPower = members.reduce((sum, member) => sum + positiveAmount(member.votingPower, "votingPower"), 0);
  const participatingPower = members.filter((member) => member.address in votes).reduce((sum, member) => sum + member.votingPower, 0);
  const yesPower = members.filter((member) => votes[member.address] === true).reduce((sum, member) => sum + member.votingPower, 0);
  const quorumMet = participatingPower * 10000 >= totalPower * PUBLIC_CRITERIA.investmentDao.quorumBps;
  const riskAllowed = proposal.riskBps <= PUBLIC_CRITERIA.investmentDao.maxRiskBps;
  const sizeAllowed = requestedCapital * 10000 <= treasuryBalance * PUBLIC_CRITERIA.investmentDao.maxCapitalPerProposalBps;
  const approved = quorumMet && yesPower * 2 > participatingPower && riskAllowed && sizeAllowed;
  return {
    proposalId: proposal.proposalId,
    strategy: proposal.strategy,
    votes: { totalPower, participatingPower, yesPower, quorumMet },
    policyChecks: { riskAllowed, sizeAllowed },
    decision: approved ? "approved_for_manual_execution" : "rejected",
    transactionStatus: "proposed_unsubmitted",
    note: "Simulation only: no wallet, broker, exchange, or smart-contract action was performed.",
  };
}
