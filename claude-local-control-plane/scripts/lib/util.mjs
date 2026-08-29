import { createHash } from "node:crypto";
import { spawn } from "node:child_process";
import { mkdir, open, readFile, realpath, rename, stat, unlink, writeFile } from "node:fs/promises";
import path from "node:path";

export function stableStringify(value) {
  if (Array.isArray(value)) {
    return `[${value.map((item) => stableStringify(item)).join(",")}]`;
  }
  if (value && typeof value === "object") {
    return `{${Object.keys(value)
      .sort()
      .map((key) => `${JSON.stringify(key)}:${stableStringify(value[key])}`)
      .join(",")}}`;
  }
  return JSON.stringify(value);
}

export function sha256(value) {
  return createHash("sha256").update(value).digest("hex");
}

export function digestJson(value) {
  return sha256(stableStringify(value));
}

export async function readJson(filePath) {
  let text;
  try {
    text = await readFile(filePath, "utf8");
  } catch (error) {
    throw new Error(`Cannot read JSON file ${filePath}: ${error.message}`);
  }
  try {
    return JSON.parse(text);
  } catch (error) {
    throw new Error(`Invalid JSON in ${filePath}: ${error.message}`);
  }
}

export async function writeJsonAtomic(filePath, value) {
  await mkdir(path.dirname(filePath), { recursive: true });
  const temporary = `${filePath}.${process.pid}.${Date.now()}.tmp`;
  await writeFile(temporary, `${JSON.stringify(value, null, 2)}\n`, { encoding: "utf8", mode: 0o600 });
  await rename(temporary, filePath);
}

export function normalizeRepoPath(input) {
  if (typeof input !== "string" || input.trim() === "") {
    throw new Error("Repository path must be a non-empty string");
  }
  const slashPath = input.replaceAll("\\", "/");
  if (slashPath.startsWith("/") || /^[A-Za-z]:\//.test(slashPath)) {
    throw new Error(`Repository path must be relative: ${input}`);
  }
  const normalized = path.posix.normalize(slashPath).replace(/^\.\//, "");
  if (normalized === "." || normalized === ".." || normalized.startsWith("../") || normalized.includes("/../")) {
    throw new Error(`Repository path escapes the project: ${input}`);
  }
  return normalized;
}

export function toRepoRelative(projectRoot, inputPath) {
  const absolute = path.isAbsolute(inputPath) ? path.resolve(inputPath) : path.resolve(projectRoot, inputPath);
  const relative = path.relative(projectRoot, absolute);
  if (relative === "" || relative === ".") return ".";
  if (relative === ".." || relative.startsWith(`..${path.sep}`) || path.isAbsolute(relative)) {
    throw new Error(`Path is outside the project: ${inputPath}`);
  }
  return normalizeRepoPath(relative);
}

export async function assertResolvedInside(projectRoot, inputPath) {
  const rootReal = await realpath(projectRoot);
  let candidate = path.isAbsolute(inputPath) ? path.resolve(inputPath) : path.resolve(projectRoot, inputPath);
  let existing = candidate;
  for (;;) {
    try {
      await stat(existing);
      break;
    } catch {
      const parent = path.dirname(existing);
      if (parent === existing) throw new Error(`Cannot resolve an existing parent for ${inputPath}`);
      existing = parent;
    }
  }
  const existingReal = await realpath(existing);
  const relative = path.relative(rootReal, existingReal);
  if (relative === ".." || relative.startsWith(`..${path.sep}`) || path.isAbsolute(relative)) {
    throw new Error(`Path resolves outside the project through a symlink: ${inputPath}`);
  }
  return candidate;
}

export async function spawnCapture(command, args, options = {}) {
  const {
    cwd,
    env = process.env,
    timeoutMs = 600_000,
    maxOutputBytes = 2_000_000,
    input = null,
  } = options;
  return await new Promise((resolve, reject) => {
    const child = spawn(command, args, {
      cwd,
      env,
      shell: false,
      windowsHide: true,
      stdio: ["pipe", "pipe", "pipe"],
    });
    const stdout = [];
    const stderr = [];
    let stdoutBytes = 0;
    let stderrBytes = 0;
    let timedOut = false;
    const timer = setTimeout(() => {
      timedOut = true;
      child.kill("SIGTERM");
      setTimeout(() => child.kill("SIGKILL"), 2_000).unref();
    }, timeoutMs);

    child.stdout.on("data", (chunk) => {
      stdoutBytes += chunk.length;
      if (stdoutBytes <= maxOutputBytes) stdout.push(chunk);
    });
    child.stderr.on("data", (chunk) => {
      stderrBytes += chunk.length;
      if (stderrBytes <= maxOutputBytes) stderr.push(chunk);
    });
    child.on("error", (error) => {
      clearTimeout(timer);
      reject(error);
    });
    child.on("close", (code, signal) => {
      clearTimeout(timer);
      resolve({
        code: code ?? -1,
        signal,
        timedOut,
        stdout: Buffer.concat(stdout).toString("utf8"),
        stderr: Buffer.concat(stderr).toString("utf8"),
        stdoutTruncated: stdoutBytes > maxOutputBytes,
        stderrTruncated: stderrBytes > maxOutputBytes,
      });
    });
    if (input !== null) child.stdin.write(input);
    child.stdin.end();
  });
}

export function parseCliArgs(argv) {
  const positional = [];
  const flags = {};
  for (let index = 0; index < argv.length; index += 1) {
    const value = argv[index];
    if (!value.startsWith("--")) {
      positional.push(value);
      continue;
    }
    const name = value.slice(2);
    const next = argv[index + 1];
    if (next === undefined || next.startsWith("--")) {
      flags[name] = true;
    } else {
      flags[name] = next;
      index += 1;
    }
  }
  return { positional, flags };
}

export function requiredFlag(flags, name) {
  const value = flags[name];
  if (typeof value !== "string" || value.length === 0) {
    throw new Error(`Missing required flag --${name}`);
  }
  return value;
}

export async function acquireLock(lockPath, metadata) {
  await mkdir(path.dirname(lockPath), { recursive: true });
  let handle;
  try {
    handle = await open(lockPath, "wx", 0o600);
  } catch (error) {
    if (error.code === "EEXIST") {
      let existing = "unknown";
      try {
        existing = await readFile(lockPath, "utf8");
      } catch {}
      throw new Error(`Another control-plane run owns ${lockPath}: ${existing.trim()}`);
    }
    throw error;
  }
  await handle.writeFile(`${JSON.stringify(metadata)}\n`, "utf8");
  await handle.close();
  let released = false;
  return async () => {
    if (released) return;
    released = true;
    try {
      await unlink(lockPath);
    } catch (error) {
      if (error.code !== "ENOENT") throw error;
    }
  };
}

export function truncateUtf8(text, maxBytes) {
  const buffer = Buffer.from(text, "utf8");
  if (buffer.length <= maxBytes) return text;
  return `${buffer.subarray(0, maxBytes).toString("utf8")}\n[TRUNCATED_BY_ORCHESTRATOR]`;
}
