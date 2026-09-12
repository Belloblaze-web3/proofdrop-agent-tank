import type { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { daoProposalInputShape, grantProposalInputShape, taskEvidenceInputShape } from "../schemas/governance.js";
import { evaluateTask, scoreGrant, simulateInvestmentDao } from "../services/governance.js";
import { callTool } from "../utils/tool-response.js";

export function registerGovernanceTools(server: McpServer): void {
  server.registerTool("evaluate_task_airdrop", { title: "Evaluate task for airdrop", description: "Score verifiable task evidence against public criteria and return a deterministic token allocation. This tool does not transfer tokens.", inputSchema: taskEvidenceInputShape }, async (input) => callTool(async () => evaluateTask(input)));
  server.registerTool("score_open_grant", { title: "Score grant proposal", description: "Score a grant proposal against public criteria and return a proposed disbursement plan. This tool does not transfer funds.", inputSchema: grantProposalInputShape }, async (input) => callTool(async () => scoreGrant(input)));
  server.registerTool("simulate_investment_dao", { title: "Simulate investment DAO vote", description: "Evaluate a paper DAO proposal for quorum, majority, risk, and position-size policy. This tool never accesses a wallet, broker, exchange, or smart contract.", inputSchema: daoProposalInputShape }, async (input) => callTool(async () => simulateInvestmentDao(input, input.members, input.votes, input.treasuryBalance)));
}
