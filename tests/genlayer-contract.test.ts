import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { describe, it } from "node:test";

const contractPath = new URL("../contracts/proofdrop_governance.py", import.meta.url);

describe("GenLayer Proofdrop contract", () => {
  it("contains the Studio-compatible version pin and contract class", async () => {
    const source = await readFile(contractPath, "utf8");
    assert.match(source, /^# \{ \"Depends\": \"py-genlayer:/);
    assert.match(source, /class ProofdropGovernance\(gl\.Contract\)/);
    assert.match(source, /@gl\.public\.write\n\s+def evaluate_task_evidence/);
    assert.match(source, /@gl\.public\.view\n\s+def get_last_evaluation/);
  });

  it("keeps persistent writes outside nondeterministic blocks", async () => {
    const source = await readFile(contractPath, "utf8");
    const nondetStart = source.indexOf("def read_evidence():");
    const stateWrite = source.indexOf("self.evaluation_count += 1");
    assert.ok(nondetStart >= 0 && stateWrite > nondetStart);
    assert.match(source, /self\.last_judgment = parsed\.get/);
    assert.match(source, /does not transfer tokens|No funds, wallets/);
  });
});
