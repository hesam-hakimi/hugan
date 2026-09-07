"""Exact private execution checkout construction, with no Git writes or helpers.

Only trusted canonical source snapshots reach this module. Loose objects and a
v2 index are encoded directly, then independently read and attested by real Git.
The detached root commit deliberately has no parent or invented upstream.
"""

from __future__ import annotations

import hashlib
import struct
import zlib
from dataclasses import dataclass

from universal_coding_agent.product.program_source_transitions import (
    ProgramSourceSnapshot,
    ProgramSourceTransitionService,
    _require,
)
from universal_coding_agent.sandbox.owned_source import OwnedSourceTree


@dataclass(frozen=True)
class _GitFile:
    content: bytes
    mode: str = "100644"


@dataclass(frozen=True)
class ExecutionLayout:
    tree: dict
    commit_sha: str
    tree_sha: str
    object_format: str


class OwnedExecutionTree(OwnedSourceTree):
    content_directory = "repo"

    def execution_layout(self, snapshot: ProgramSourceSnapshot,
                         source: ProgramSourceTransitionService) -> ExecutionLayout:
        """Bound all source, object, index and directory bytes before allocation.

        Git metadata is host-created, never admitted as a ProgramSourceFile. The
        existing source path contract continues to prohibit every .git component.
        """
        source_sha = source.snapshot_hash(snapshot)
        tree = self.layout(snapshot)
        object_format = "sha1" if len(snapshot.identity.origin_base_sha) == 40 else "sha256"

        def digest(raw):
            return hashlib.new(object_format, raw, usedforsecurity=False).digest()

        objects = {}
        object_bytes = 0

        def put(kind, content):
            nonlocal object_bytes
            raw = kind.encode() + b" " + str(len(content)).encode() + b"\0" + content
            oid = digest(raw)
            hex_oid = oid.hex()
            if hex_oid not in objects:
                packed = zlib.compress(raw)
                object_bytes += len(packed)
                _require(object_bytes <= source.policy.max_total_bytes
                         + self.policy.max_metadata_bytes, "execution object byte budget exceeded")
                objects[hex_oid] = packed
            return oid

        blobs = {item.path: put("blob", item.content) for item in snapshot.files}

        def make_tree(node, prefix=""):
            entries = []
            for name in sorted(node, key=lambda k: k.encode() +
                               (b"/" if isinstance(node[k], dict) else b"\0")):
                value = node[name]
                if isinstance(value, dict):
                    mode, oid = "40000", make_tree(value, prefix + name + "/")
                else:
                    mode, oid = value.mode, blobs[prefix + name]
                entries.append(mode.encode() + b" " + name.encode() + b"\0" + oid)
            return put("tree", b"".join(entries))

        tree_sha = make_tree(tree).hex()
        commit = (f"tree {tree_sha}\n"
                  "author UCA Execution <execution@uca.invalid> 0 +0000\n"
                  "committer UCA Execution <execution@uca.invalid> 0 +0000\n\n"
                  f"UCA accepted source execution base\nSource-SHA256: {source_sha}\n").encode()
        commit_sha = put("commit", commit).hex()
        entries = []
        for item in snapshot.files:
            path = item.path.encode("ascii")
            entry = (struct.pack("!10I", 0, 0, 0, 0, 0, 0, int(item.mode, 8), 0, 0,
                                 len(item.content)) + blobs[item.path]
                     + struct.pack("!H", len(path)) + path + b"\0")
            entries.append(entry + b"\0" * (-len(entry) % 8))
        index = struct.pack("!4sII", b"DIRC", 2, len(entries)) + b"".join(entries)
        index += digest(index)
        config = ("[core]\n\trepositoryformatversion = "
                  + ("1" if object_format == "sha256" else "0")
                  + "\n\tbare = false\n\tfilemode = true\n\tautocrlf = false\n"
                  "\thooksPath = /dev/null\n\tfsmonitor = false\n"
                  "\tattributesfile = /dev/null\n\texcludesfile = /dev/null\n"
                  "[protocol]\n\tallow = never\n[credential]\n\thelper =\n"
                  "\tinteractive = never\n[gc]\n\tauto = 0\n"
                  "[maintenance]\n\tauto = false\n[commit]\n\tgpgsign = false\n")
        if object_format == "sha256":
            config += "[extensions]\n\tobjectformat = sha256\n"
        git = {"HEAD": _GitFile((commit_sha + "\n").encode()),
               "config": _GitFile(config.encode()), "index": _GitFile(index),
               "refs": {}, "objects": {}}
        for oid, packed in objects.items():
            git["objects"].setdefault(oid[:2], {})[oid[2:]] = _GitFile(packed)
        tree[".git"] = git
        count, metadata = 0, 0

        def bound(node, prefix=""):
            nonlocal count, metadata
            for name, child in node.items():
                count += 1
                path = prefix + name
                metadata += len(path) + 256
                _require(count <= self.policy.max_entries
                         and metadata <= self.policy.max_metadata_bytes,
                         "execution directory or metadata budget exceeded")
                if isinstance(child, dict):
                    bound(child, path + "/")

        bound(tree)
        _require(len(index) <= self.policy.max_metadata_bytes,
                 "execution index byte budget exceeded")
        return ExecutionLayout(tree, commit_sha, tree_sha, object_format)
