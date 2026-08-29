import { lstat, readFile, readdir, readlink } from "node:fs/promises";
import path from "node:path";
import { assertResolvedInside, digestJson, normalizeRepoPath, sha256, spawnCapture, stableStringify, truncateUtf8 } from "./util.mjs";

export async function runGit(projectRoot, args, { allowFailure = false, timeoutMs = 120_000 } = {}) {
  const result = await spawnCapture("git", args, { cwd: projectRoot, timeoutMs, maxOutputBytes: 10_000_000 });
  if (!allowFailure && result.code !== 0) {
    throw new Error(`git ${args.join(" ")} failed (${result.code}): ${result.stderr.trim()}`);
  }
  return result;
}

export async function repositoryIdentity(projectRoot) {
  const [top, head, branch, tree] = await Promise.all([
    runGit(projectRoot, ["rev-parse", "--show-toplevel"]),
    runGit(projectRoot, ["rev-parse", "HEAD"]),
    runGit(projectRoot, ["branch", "--show-current"]),
    runGit(projectRoot, ["rev-parse", "HEAD^{tree}"]),
  ]);
  const resolvedTop = path.resolve(top.stdout.trim());
  if (resolvedTop !== path.resolve(projectRoot)) {
    throw new Error(`Project root must be the Git top level: expected ${resolvedTop}, received ${projectRoot}`);
  }
  return {
    projectRoot: resolvedTop,
    headSha: head.stdout.trim(),
    branch: branch.stdout.trim(),
    treeSha: tree.stdout.trim(),
  };
}

function parseNameStatus(bufferText) {
  const tokens = bufferText.split("\0").filter((item) => item !== "");
  const paths = [];
  for (let index = 0; index < tokens.length; index += 1) {
    const status = tokens[index];
    if (/^[RC]/.test(status)) {
      const oldPath = tokens[index + 1];
      const newPath = tokens[index + 2];
      if (oldPath) paths.push(oldPath);
      if (newPath) paths.push(newPath);
      index += 2;
    } else {
      const filePath = tokens[index + 1];
      if (filePath) paths.push(filePath);
      index += 1;
    }
  }
  return paths;
}

export async function changedPaths(projectRoot) {
  const [unstaged, staged, untracked] = await Promise.all([
    runGit(projectRoot, ["diff", "--name-status", "-z"]),
    runGit(projectRoot, ["diff", "--cached", "--name-status", "-z"]),
    runGit(projectRoot, ["ls-files", "--others", "--exclude-standard", "-z"]),
  ]);
  const paths = [
    ...parseNameStatus(unstaged.stdout),
    ...parseNameStatus(staged.stdout),
    ...untracked.stdout.split("\0").filter(Boolean),
  ].map((item) => normalizeRepoPath(item));
  return [...new Set(paths)].sort();
}

export async function assertCleanWorktree(projectRoot) {
  const paths = await changedPaths(projectRoot);
  if (paths.length > 0) throw new Error(`A new run requires a clean worktree; found: ${paths.join(", ")}`);
}

export async function captureWorkspaceSnapshot(projectRoot) {
  const entries = {};
  async function visit(absoluteDirectory, relativeDirectory = "") {
    const children = await readdir(absoluteDirectory, { withFileTypes: true });
    children.sort((left, right) => left.name.localeCompare(right.name));
    for (const child of children) {
      if (child.name === ".git") continue;
      const relative = relativeDirectory ? `${relativeDirectory}/${child.name}` : child.name;
      const normalized = normalizeRepoPath(relative);
      const absolute = path.join(absoluteDirectory, child.name);
      const metadata = await lstat(absolute);
      const mode = metadata.mode & 0o777;
      if (metadata.isSymbolicLink()) {
        const target = await readlink(absolute);
        entries[normalized] = { kind: "symlink", mode, size: Buffer.byteLength(target), sha256: sha256(target) };
      } else if (metadata.isDirectory()) {
        await visit(absolute, normalized);
      } else if (metadata.isFile()) {
        const content = await readFile(absolute);
        entries[normalized] = { kind: "file", mode, size: content.length, sha256: sha256(content) };
      } else {
        entries[normalized] = { kind: "other", mode, size: metadata.size, sha256: null };
      }
    }
  }
  await visit(projectRoot);
  return { schemaVersion: "1.0", entries };
}

export function compareWorkspaceSnapshots(baseline, current) {
  const paths = [...new Set([...Object.keys(baseline.entries), ...Object.keys(current.entries)])].sort();
  return paths.filter((filePath) => stableStringify(baseline.entries[filePath] ?? null) !== stableStringify(current.entries[filePath] ?? null));
}

async function baseBlobSha(projectRoot, filePath) {
  const result = await runGit(projectRoot, ["rev-parse", `HEAD:${filePath}`], { allowFailure: true });
  return result.code === 0 ? result.stdout.trim() : null;
}

async function currentFileEvidence(projectRoot, filePath) {
  const absolute = path.resolve(projectRoot, filePath);
  await assertResolvedInside(projectRoot, absolute);
  try {
    const metadata = await lstat(absolute);
    if (metadata.isSymbolicLink()) {
      return { kind: "symlink", size: metadata.size, sha256: null };
    }
    if (!metadata.isFile()) {
      return { kind: "non-file", size: metadata.size, sha256: null };
    }
    const content = await readFile(absolute);
    return { kind: "file", size: content.length, sha256: sha256(content) };
  } catch (error) {
    if (error.code === "ENOENT") return { kind: "deleted", size: 0, sha256: null };
    throw error;
  }
}

export async function diffEvidence(projectRoot, maxDiffBytes = 300_000, observedPaths = null, baselineSnapshot = null) {
  const paths = observedPaths ?? await changedPaths(projectRoot);
  const records = [];
  for (const filePath of paths) {
    records.push({
      path: filePath,
      baseBlobSha: await baseBlobSha(projectRoot, filePath),
      baseline: baselineSnapshot?.entries?.[filePath] ?? null,
      current: await currentFileEvidence(projectRoot, filePath),
    });
  }
  const trackedPatch = await runGit(projectRoot, ["diff", "--binary", "HEAD", "--"]);
  const patchSections = [trackedPatch.stdout];
  for (const record of records.filter((item) => item.baseBlobSha === null && item.current.kind === "file")) {
    const absolute = path.resolve(projectRoot, record.path);
    const content = await readFile(absolute);
    const text = content.includes(0) ? `[binary file: ${record.current.size} bytes]` : content.toString("utf8");
    patchSections.push(`\n--- /dev/null\n+++ b/${record.path}\n${text}`);
  }
  const canonical = { records };
  return {
    changedPaths: paths,
    records,
    digest: digestJson(canonical),
    patch: truncateUtf8(patchSections.join("\n"), maxDiffBytes),
    patchTruncated: Buffer.byteLength(patchSections.join("\n"), "utf8") > maxDiffBytes,
    canonicalJson: stableStringify(canonical),
  };
}

export async function gitMetadataDirectory(projectRoot) {
  const result = await runGit(projectRoot, ["rev-parse", "--git-path", "lcac"]);
  return path.resolve(projectRoot, result.stdout.trim());
}
