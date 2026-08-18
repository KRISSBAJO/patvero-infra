#!/usr/bin/env node
// Verifies, restores, or refreshes the subproject commits recorded in
// workspace.lock.json. The three application repositories are versioned
// independently, so this file is the only record of which commits form a
// working set.
import { execFileSync } from "node:child_process";
import { readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const lockPath = join(root, "workspace.lock.json");
const command = process.argv[2] ?? "check";

function git(repository, ...args) {
  return execFileSync("git", ["-C", join(root, repository), ...args], {
    encoding: "utf8",
  }).trim();
}

const lock = JSON.parse(readFileSync(lockPath, "utf8"));
const entries = Object.entries(lock.repositories);

if (command === "check") {
  let drifted = 0;
  for (const [name, pin] of entries) {
    const commit = git(name, "rev-parse", "HEAD");
    const branch = git(name, "rev-parse", "--abbrev-ref", "HEAD");
    const dirty = git(name, "status", "--porcelain").length > 0;

    if (commit === pin.commit && !dirty) {
      console.log(`  ok      ${name}  ${commit.slice(0, 7)}  ${branch}`);
      continue;
    }
    drifted += 1;
    console.log(`  DRIFT   ${name}`);
    console.log(`            pinned  ${pin.commit.slice(0, 7)}  ${pin.branch}`);
    console.log(`            actual  ${commit.slice(0, 7)}  ${branch}${dirty ? "  (uncommitted changes)" : ""}`);
  }
  if (drifted > 0) {
    console.error(
      `\n${drifted} repository(ies) differ from workspace.lock.json.` +
        `\nRun "npm run pin:sync" to restore the pinned set, or "npm run pin:update" to record the current one.`,
    );
    process.exit(1);
  }
  console.log("\nAll subprojects match workspace.lock.json.");
} else if (command === "sync") {
  for (const [name, pin] of entries) {
    if (git(name, "status", "--porcelain").length > 0) {
      console.error(`  SKIP    ${name} has uncommitted changes; refusing to check out.`);
      process.exitCode = 1;
      continue;
    }
    git(name, "fetch", "origin", pin.branch);
    git(name, "checkout", pin.commit);
    console.log(`  synced  ${name}  ${pin.commit.slice(0, 7)}  ${pin.branch}`);
  }
} else if (command === "update") {
  for (const [name, pin] of entries) {
    pin.commit = git(name, "rev-parse", "HEAD");
    pin.branch = git(name, "rev-parse", "--abbrev-ref", "HEAD");
    pin.subject = git(name, "log", "-1", "--format=%s");
    console.log(`  pinned  ${name}  ${pin.commit.slice(0, 7)}  ${pin.branch}`);
  }
  lock.pinnedAt = new Date().toISOString().slice(0, 10);
  writeFileSync(lockPath, `${JSON.stringify(lock, null, 2)}\n`);
  console.log("\nworkspace.lock.json updated. Review the note field before committing.");
} else {
  console.error(`Unknown command "${command}". Use check, sync, or update.`);
  process.exit(1);
}
