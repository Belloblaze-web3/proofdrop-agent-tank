import { z } from "zod";

export const taskEvidenceInputShape = {
  participant: z.string().min(1), taskId: z.string().min(1), completed: z.boolean(), qualityScore: z.number(), durationSeconds: z.number().positive(), evidenceUrl: z.string().url().optional(),
};
export const grantProposalInputShape = {
  proposalId: z.string().min(1), applicant: z.string().min(1), requestedAmount: z.number().positive(), impact: z.number(), feasibility: z.number(), openness: z.number(), communityBenefit: z.number(), evidenceUrl: z.string().url().optional(),
};
export const daoProposalInputShape = {
  proposalId: z.string().min(1), strategy: z.string().min(1), requestedCapital: z.number().positive(), expectedReturnBps: z.number(), riskBps: z.number(), rationale: z.string().min(1), members: z.array(z.object({ address: z.string().min(1), votingPower: z.number().positive() })), votes: z.record(z.string(), z.boolean()), treasuryBalance: z.number().nonnegative(),
};
