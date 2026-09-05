from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from universal_coding_agent.product.repository_indexes import RepositoryIndexService
from universal_coding_agent.product.search_service import SearchService
from universal_coding_agent.repository import ecmascript as ecmascript_module
from universal_coding_agent.repository.indexer import (
    RepositoryIndexer,
    RepositoryIndexingError,
)
from universal_coding_agent.storage.artifacts import ArtifactStore


def _git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _write(root: Path, relative: str, content: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _project_file(tmp_path: Path, relative: str, content: str):
    _write(tmp_path, relative, content)
    return RepositoryIndexer().project_file(tmp_path, relative)


def test_extracts_bounded_static_esm_and_typescript_import_equals_references(
    tmp_path: Path,
) -> None:
    project_file = _project_file(
        tmp_path,
        "src/app.ts",
        (
            'import "./startup";\n'
            'import defaultValue, { type Contract, value as renamed } from "./service";\n'
            'import type { Model } from "./models";\n'
            'import legacy = require("./legacy");\n'
            'export { publicValue } from "./public";\n'
            'export type { PublicModel } from "./public-model";\n'
            'export * from "./all";\n'
            'export * as helpers from "./helpers";\n'
        ),
    )

    assert project_file is not None
    assert project_file.language == "typescript"
    assert project_file.imports == (
        "esm-export:./all",
        "esm-export:./helpers",
        "esm-export:./public",
        "esm-export:./public-model",
        "esm-import:./models",
        "esm-import:./service",
        "esm-import:./startup",
        "ts-import-equals:./legacy",
    )


@pytest.mark.parametrize(
    ("relative", "language"),
    (
        ("src/a.ts", "typescript"),
        ("src/a.tsx", "typescript"),
        ("src/a.mts", "typescript"),
        ("src/a.cts", "typescript"),
        ("src/a.js", "javascript"),
        ("src/a.jsx", "javascript"),
        ("src/a.mjs", "javascript"),
        ("src/a.cjs", "javascript"),
    ),
)
def test_recognizes_ecmascript_module_extensions(
    tmp_path: Path,
    relative: str,
    language: str,
) -> None:
    project_file = _project_file(tmp_path, relative, 'import value from "./value";\n')

    assert project_file is not None
    assert project_file.language == language
    assert project_file.imports == ("esm-import:./value",)


@pytest.mark.parametrize(
    "relative",
    (
        "src/a.test.tsx",
        "src/a.spec.mts",
        "src/a.test.cts",
        "src/a.spec.jsx",
        "src/a.test.mjs",
        "src/a.spec.cjs",
    ),
)
def test_recognizes_ecmascript_test_module_suffixes(
    tmp_path: Path,
    relative: str,
) -> None:
    project_file = _project_file(tmp_path, relative, "export const value = true;\n")

    assert project_file is not None
    assert project_file.is_test is True


def test_multiline_declarations_are_canonical_sorted_and_deduplicated(
    tmp_path: Path,
) -> None:
    project_file = _project_file(
        tmp_path,
        "src/app.tsx",
        (
            "import {\n"
            "  Alpha,\n"
            "  type Beta,\n"
            '} from "./shared"\n'
            'import "./shared"\n'
            "export {\n"
            "  Alpha,\n"
            '} from "./shared"\n'
        ),
    )

    assert project_file is not None
    assert project_file.imports == (
        "esm-export:./shared",
        "esm-import:./shared",
    )


def test_ignores_comments_literals_regex_dynamic_import_and_import_meta(
    tmp_path: Path,
) -> None:
    project_file = _project_file(
        tmp_path,
        "src/app.js",
        (
            '// import fake from "./comment";\n'
            '/* export * from "./block-comment"; */\n'
            'const text = "import fake from \'./string\'";\n'
            'const template = `export * from "./template"`;\n'
            'const pattern = /import fake from "\\.\\/regex"/;\n'
            'const lazy = import("./dynamic");\n'
            "const current = import.meta.url;\n"
            'import actual from "./actual";\n'
        ),
    )

    assert project_file is not None
    assert project_file.imports == ("esm-import:./actual",)


def test_ignores_nested_template_content_and_accepts_hashbang_and_bom(
    tmp_path: Path,
) -> None:
    project_file = _project_file(
        tmp_path,
        "src/entry.mjs",
        (
            '\ufeff#!/usr/bin/env node\n'
            "const rendered = `outer ${condition ? `inner\\n"
            'import fake from "./nested-template"` : value} tail`;\n'
            'import actual from "./actual";\n'
        ),
    )

    assert project_file is not None
    assert project_file.imports == ("esm-import:./actual",)


def test_local_exports_and_ordinary_identifiers_do_not_create_references(
    tmp_path: Path,
) -> None:
    project_file = _project_file(
        tmp_path,
        "src/app.ts",
        (
            "const imported = source.import(value);\n"
            "export { imported };\n"
            "export default imported;\n"
            "export const visible = imported;\n"
        ),
    )

    assert project_file is not None
    assert project_file.imports == ()


def test_jsx_text_does_not_create_false_strings_or_module_references(
    tmp_path: Path,
) -> None:
    project_file = _project_file(
        tmp_path,
        "src/App.tsx",
        (
            'import React from "react";\n'
            "export function App() {\n"
            "  return (\n"
            "    <main>UCA's evidence says import fake from &quot;./fake&quot;.</main>\n"
            "  );\n"
            "}\n"
        ),
    )

    assert project_file is not None
    assert project_file.imports == ("esm-import:react",)


@pytest.mark.parametrize(
    "content",
    (
        "import value from target;\n",
        "import value;\n",
        "export * from target;\n",
        "import value = require(target);\n",
    ),
)
def test_malformed_or_unsupported_static_declarations_fail_closed(
    tmp_path: Path,
    content: str,
) -> None:
    _write(tmp_path, "src/app.ts", content)

    with pytest.raises(RepositoryIndexingError, match="unsupported or malformed"):
        RepositoryIndexer().project_file(tmp_path, "src/app.ts")


@pytest.mark.parametrize(
    "content",
    (
        'import value from "./unterminated\n',
        "/* unterminated\n",
        "const value = `unterminated\n",
        "const value = { nested: true;\n",
    ),
)
def test_incomplete_lexical_structures_fail_closed(
    tmp_path: Path,
    content: str,
) -> None:
    _write(tmp_path, "src/app.ts", content)

    with pytest.raises(RepositoryIndexingError):
        RepositoryIndexer().project_file(tmp_path, "src/app.ts")


def test_escaped_and_oversized_module_specifiers_fail_closed(tmp_path: Path) -> None:
    escaped = tmp_path / "escaped"
    escaped.mkdir()
    _write(escaped, "app.ts", 'import value from "./\\u0076alue";\n')
    with pytest.raises(RepositoryIndexingError, match="escaped"):
        RepositoryIndexer().project_file(escaped, "app.ts")

    oversized = tmp_path / "oversized"
    oversized.mkdir()
    _write(oversized, "app.ts", f'import value from "./{"x" * 4096}";\n')
    with pytest.raises(RepositoryIndexingError, match="exceeds"):
        RepositoryIndexer().project_file(oversized, "app.ts")


def test_invalid_utf8_ecmascript_source_fails_closed(tmp_path: Path) -> None:
    path = tmp_path / "app.js"
    path.write_bytes(b'import value from "./value";\n\xff')

    with pytest.raises(RepositoryIndexingError, match="not valid UTF-8"):
        RepositoryIndexer().project_file(tmp_path, "app.js")


def test_token_and_module_reference_limits_fail_closed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    token_root = tmp_path / "tokens"
    token_root.mkdir()
    _write(token_root, "app.js", "const first = 1; const second = 2;\n")
    monkeypatch.setattr(ecmascript_module, "MAX_ECMASCRIPT_TOKENS", 2)
    with pytest.raises(RepositoryIndexingError, match="token limit"):
        RepositoryIndexer().project_file(token_root, "app.js")

    reference_root = tmp_path / "references"
    reference_root.mkdir()
    _write(
        reference_root,
        "app.js",
        'import "./first";\nimport "./second";\n',
    )
    monkeypatch.setattr(ecmascript_module, "MAX_ECMASCRIPT_TOKENS", 250_000)
    monkeypatch.setattr(ecmascript_module, "MAX_ECMASCRIPT_MODULE_REFERENCES", 1)
    with pytest.raises(RepositoryIndexingError, match="module-reference limit"):
        RepositoryIndexer().project_file(reference_root, "app.js")


def test_repository_index_policy_binds_ecmascript_contract_and_limits(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    artifacts = ArtifactStore(tmp_path / "artifacts")
    search = SearchService(tmp_path / "search.sqlite")
    service = RepositoryIndexService(artifacts, search)
    try:
        original = service._policy_sha256()
        monkeypatch.setattr(
            ecmascript_module,
            "MAX_ECMASCRIPT_TOKENS",
            ecmascript_module.MAX_ECMASCRIPT_TOKENS - 1,
        )
        assert service._policy_sha256() != original
    finally:
        search.close()


def test_incremental_snapshot_persists_exact_module_reference_evidence(
    tmp_path: Path,
) -> None:
    root = tmp_path / "source"
    root.mkdir()
    _git(root, "init", "-b", "main")
    _git(root, "config", "user.email", "ecmascript@example.test")
    _git(root, "config", "user.name", "ECMAScript Evidence Test")
    _write(root, "src/app.ts", 'import api from "./api";\n')
    _write(root, "src/api.ts", "export const api = true;\n")
    _git(root, "add", "-A")
    _git(root, "commit", "-m", "initial fixture")
    base_sha = _git(root, "rev-parse", "HEAD")

    artifacts = ArtifactStore(tmp_path / "artifacts")
    search = SearchService(tmp_path / "search.sqlite")
    service = RepositoryIndexService(artifacts, search)
    try:
        result = service.index(
            project_id="project-ecmascript",
            root=root,
            repository_url="https://example.test/project-ecmascript.git",
            base_ref="main",
            base_sha=base_sha,
            expected_previous_snapshot_sha256=None,
        )
        files = {item.path: item.project_file for item in result.snapshot.files}
        assert files["src/app.ts"].imports == ("esm-import:./api",)
        assert files["src/api.ts"].imports == ()
        state = search.repository_index_state(service.namespace("project-ecmascript"))
        assert state is not None
        verified = service.verified_snapshot(
            state.snapshot_ref,
            expected_sha256=state.snapshot_sha256,
        )
        assert verified == result.snapshot
        metadata = service.search_project("project-ecmascript", "import api")[0].metadata
        assert metadata["imports"] == ["esm-import:./api"]
    finally:
        search.close()
