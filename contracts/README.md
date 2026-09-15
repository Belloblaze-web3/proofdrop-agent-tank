# Proofdrop Governance Intelligent Contract

`proofdrop_governance.py` is the on-chain decision layer for the Agent Tank build. It evaluates a public evidence URL through GenLayer validator consensus, stores the agreed score and eligibility decision, and exposes read-only state for the frontend.

## What the contract actually does

The contract maintains persistent state for the last evaluation and an indexed task history. `evaluate_task_evidence` first fetches the public evidence page through a strict-equivalence block, then asks validators to judge the evidence against the submitted task claim. State is written only after the consensus-backed result is available.

It deliberately does **not** transfer tokens, access wallets, disburse grants, or execute investment trades. It records a proposal-grade decision so a community can inspect and approve a later settlement step.

## Studio Next deployment

Use the release-candidate CLI/SDK that matches Studio Next. The Portal notice specifies:

- RPC alias: `https://studio-next.genlayer.com/api`
- Canonical Studio-dev RPC: `https://studio-dev.genlayer.com/api`
- Chain ID: `61997`
- Explorer: `https://explorer-studio-dev.genlayer.com/`

The canonical SDK network should use the Studio-dev RPC, even when the browser is opened through the Studio Next alias.

```bash
# Install the matching GenLayer CLI/RC in your local environment.
genlayer network set studio-dev
genlayer network info
# Deploy from the repository root after funding the connected account.
genlayer deploy --contract contracts/proofdrop_governance.py
```

Record the finalized transaction ID and contract address in a private deployment note, then add the public address to the Agent Tank form only after confirming the explorer shows a successful execution.

## Manual Studio flow

1. Open the Studio Next UI.
2. Create a new Intelligent Contract and paste `proofdrop_governance.py`.
3. Deploy with the default constructor (no arguments).
4. Call `get_policy` and confirm the public policy JSON is returned.
5. Call `evaluate_task_evidence` with an HTTPS evidence page, participant, task ID, and claim.
6. Wait for consensus finalization.
7. Call `get_last_evaluation` and `get_task_evaluation(task_id)`.
8. Confirm the explorer shows the finalized transaction and the contract state matches the returned judgment.

## Frontend verification payload

The demo should show this path before asking a reviewer to inspect the contract:

```json
{
  "task_id": "demo-so101-seed-7",
  "participant": "demo-reviewer",
  "evidence_url": "https://proofdrop-rfj6pbtq.manus.space/",
  "task_claim": "The Proofdrop benchmark and governance policy are publicly documented."
}
```

Do not claim a live contract address or transaction until the deployment has been finalized and verified in the Studio-dev explorer.
