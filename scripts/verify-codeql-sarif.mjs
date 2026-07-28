import fs from "node:fs";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const acceptedPath = path.join(root, ".github", "codeql-accepted-findings.json");
const resultsDir = path.resolve(process.argv[2] || "../results");
const accepted = new Set(
  JSON.parse(fs.readFileSync(acceptedPath, "utf8")).map(finding =>
    `${finding.ruleId}\t${finding.path}\t${finding.startLine}`
  )
);

const sarifFiles = fs.readdirSync(resultsDir).filter(name => name.endsWith(".sarif"));
if (sarifFiles.length === 0) {
  throw new Error(`no SARIF files found in ${resultsDir}`);
}

const unexpected = [];
for (const name of sarifFiles) {
  const sarif = JSON.parse(fs.readFileSync(path.join(resultsDir, name), "utf8"));
  for (const run of sarif.runs || []) {
    for (const result of run.results || []) {
      const location = result.locations?.[0]?.physicalLocation;
      const finding = {
        ruleId: result.ruleId,
        path: location?.artifactLocation?.uri,
        startLine: location?.region?.startLine,
      };
      const key = `${finding.ruleId}\t${finding.path}\t${finding.startLine}`;
      if (!accepted.has(key)) unexpected.push(finding);
    }
  }
}

if (unexpected.length > 0) {
  console.error("Unexpected CodeQL findings:");
  console.error(JSON.stringify(unexpected, null, 2));
  process.exit(1);
}

console.log("CodeQL contains no findings outside the reviewed exact-location allowlist.");
