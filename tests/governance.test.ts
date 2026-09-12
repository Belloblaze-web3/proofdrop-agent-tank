import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { evaluateTask, scoreGrant, simulateInvestmentDao } from "../src/services/governance.js";

describe("governance simulations", () => {
  it("allocates tokens only to completed quality tasks", () => {
    const result = evaluateTask({ participant: "alice", taskId: "task-1", completed: true, qualityScore: 90, durationSeconds: 30 });
    assert.equal(result.eligible, true);
    assert.ok(result.tokenAmount > 0);
    assert.equal(evaluateTask({ participant: "bob", taskId: "task-2", completed: false, qualityScore: 100, durationSeconds: 1 }).tokenAmount, 0);
  });

  it("scores grants against public criteria and creates a proposed plan", () => {
    const result = scoreGrant({ proposalId: "grant-1", applicant: "team", requestedAmount: 500, impact: 90, feasibility: 80, openness: 90, communityBenefit: 85 });
    assert.equal(result.approved, true);
    assert.equal(result.disbursementPlan.status, "proposed_unsubmitted");
  });

  it("requires quorum and policy checks for paper DAO approval", () => {
    const result = simulateInvestmentDao({ proposalId: "dao-1", strategy: "paper treasury basket", requestedCapital: 100, expectedReturnBps: 500, riskBps: 1000, rationale: "Diversification simulation" }, [{ address: "a", votingPower: 60 }, { address: "b", votingPower: 40 }], { a: true, b: true }, 10000);
    assert.equal(result.decision, "approved_for_manual_execution");
    assert.equal(result.transactionStatus, "proposed_unsubmitted");
  });
});
