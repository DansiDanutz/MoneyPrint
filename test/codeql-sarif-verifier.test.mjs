import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
import test from "node:test";

const verifier = path.resolve("scripts/verify-codeql-sarif.mjs");

function runWith(result) {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), "moneyprint-codeql-"));
  fs.writeFileSync(
    path.join(directory, "results.sarif"),
    JSON.stringify({ runs: [{ results: result ? [result] : [] }] })
  );
  return spawnSync(process.execPath, [verifier, directory], { encoding: "utf8" });
}

test("accepts an empty result set", () => {
  assert.equal(runWith(null).status, 0);
});

test("accepts only an exact reviewed finding", () => {
  const result = {
    ruleId: "py/path-injection",
    locations: [{ physicalLocation: {
      artifactLocation: { uri: "app/utils/file_security.py" },
      region: { startLine: 35 },
    } }],
  };
  assert.equal(runWith(result).status, 0);
});

test("rejects a finding when its location drifts", () => {
  const result = {
    ruleId: "py/path-injection",
    locations: [{ physicalLocation: {
      artifactLocation: { uri: "app/utils/file_security.py" },
      region: { startLine: 36 },
    } }],
  };
  const run = runWith(result);
  assert.equal(run.status, 1);
  assert.match(run.stderr, /Unexpected CodeQL findings/);
});
