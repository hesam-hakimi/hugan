import { normalizeRepoPath } from "./util.mjs";

function escapeRegex(character) {
  return /[\\^$+?.()|{}\[\]]/.test(character) ? `\\${character}` : character;
}

export function globToRegex(pattern) {
  const normalized = normalizeRepoPath(pattern);
  let expression = "^";
  for (let index = 0; index < normalized.length; index += 1) {
    const character = normalized[index];
    if (character === "*") {
      if (normalized[index + 1] === "*") {
        index += 1;
        if (normalized[index + 1] === "/") {
          index += 1;
          expression += "(?:.*/)?";
        } else {
          expression += ".*";
        }
      } else {
        expression += "[^/]*";
      }
    } else if (character === "?") {
      expression += "[^/]";
    } else {
      expression += escapeRegex(character);
    }
  }
  expression += "$";
  return new RegExp(expression);
}

export function matchesPattern(filePath, pattern) {
  return globToRegex(pattern).test(normalizeRepoPath(filePath));
}

export function matchesAny(filePath, patterns) {
  return patterns.some((pattern) => matchesPattern(filePath, pattern));
}

function fixedPrefix(pattern) {
  const normalized = normalizeRepoPath(pattern);
  const wildcard = normalized.search(/[?*]/);
  return wildcard === -1 ? normalized : normalized.slice(0, wildcard);
}

export function patternWithin(childPattern, parentPattern) {
  const child = normalizeRepoPath(childPattern);
  const parent = normalizeRepoPath(parentPattern);
  if (child === parent) return true;
  if (parent === "**" || parent === "**/*") return true;
  if (!/[?*]/.test(parent)) return false;
  const parentPrefix = fixedPrefix(parent);
  const childPrefix = fixedPrefix(child);
  if (!childPrefix.startsWith(parentPrefix)) return false;
  if (parent.endsWith("/**")) return true;
  return !/[?*]/.test(child) && matchesPattern(child, parent);
}
