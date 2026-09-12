# Proofdrop Governance Concepts

Proofdrop now includes a simulation-first governance layer for three related ideas: intelligent airdrops, open-criteria grants, and an investment DAO. The primitives are deterministic, inspectable, and exposed as MCP tools. They create scores, allocations, votes, and proposed plans; they do not transfer tokens, disburse funds, access wallets, submit trades, or call smart contracts.

## Intelligent airdrop

`evaluate_task_airdrop` scores a participant's submitted evidence using completion, quality, and a bounded speed component. The public weights are visible in `src/services/governance.ts`. A completed task that clears the threshold receives a deterministic token amount capped at 100 tokens per task. Incomplete or low-quality work receives zero. Production deployment should add signed attestations, duplicate-submission prevention, Sybil resistance, an appeal process, and an on-chain distributor operated by a separately reviewed contract.

## Grants by open criteria

`score_open_grant` evaluates impact, feasibility, openness, and community benefit. The score threshold and weights are public. Approved proposals receive a `proposed_unsubmitted` disbursement plan that still requires community approval. A production grants system should add identity and conflict-of-interest controls, immutable proposal snapshots, reviewer calibration, a treasury budget, milestone verification, and a multisig or audited contract for any real disbursement.

## Investment DAO

`simulate_investment_dao` evaluates a paper proposal against quorum, majority, maximum risk, and maximum capital-per-proposal rules. Its output is deliberately marked `approved_for_manual_execution` rather than executed. The implementation never accesses a wallet, broker, exchange, custody account, or trading venue. A production version would require legal review, token-holder governance, treasury custody, audited execution contracts, oracle policy, emergency controls, and a clear separation between proposal analysis and transaction signing.

## MCP tools

| Tool | Purpose | Side effect |
|---|---|---|
| `evaluate_task_airdrop` | Score real task evidence and calculate a capped allocation | None |
| `score_open_grant` | Apply public grant criteria and produce a proposed plan | None |
| `simulate_investment_dao` | Run a quorum, majority, risk, and concentration simulation | None |

## Example inputs

```json
{
  "participant": "alice",
  "taskId": "review-001",
  "completed": true,
  "qualityScore": 92,
  "durationSeconds": 180
}
```

```json
{
  "proposalId": "grant-001",
  "applicant": "open-source-team",
  "requestedAmount": 5000,
  "impact": 90,
  "feasibility": 80,
  "openness": 95,
  "communityBenefit": 88
}
```

All numeric inputs are validated and all outputs are deterministic for the same inputs. This makes the layer suitable for public criteria pages, challenge demos, and later replacement with audited on-chain components.
