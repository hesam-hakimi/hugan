from __future__ import annotations

from dataclasses import dataclass

ECMASCRIPT_MODULE_REFERENCE_POLICY_VERSION = "1"
MAX_ECMASCRIPT_TOKENS = 250_000
MAX_ECMASCRIPT_MODULE_REFERENCES = 10_000
MAX_ECMASCRIPT_MODULE_SPECIFIER_CHARS = 4_096

_REGEX_PREFIX_IDENTIFIERS = frozenset(
    {
        "await",
        "case",
        "delete",
        "do",
        "else",
        "in",
        "instanceof",
        "new",
        "of",
        "return",
        "throw",
        "typeof",
        "void",
        "yield",
    }
)
_REGEX_PREFIX_PUNCTUATION = frozenset("([{=,:;!?&|+-*%^~")


class ECMAScriptModuleEvidenceError(ValueError):
    """ECMAScript source cannot produce bounded static module-reference evidence."""


@dataclass(frozen=True)
class _Token:
    kind: str
    value: str
    line: int
    end_line: int
    escaped: bool = False


def extract_module_references(data: bytes, *, path: str) -> tuple[str, ...]:
    try:
        text = data.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise ECMAScriptModuleEvidenceError(
            f"JavaScript/TypeScript source is not valid UTF-8: {path}"
        ) from exc
    tokens = _tokenize(text, path=path)
    references = _extract_module_references(tokens, path=path)
    if len(references) > MAX_ECMASCRIPT_MODULE_REFERENCES:
        raise ECMAScriptModuleEvidenceError(
            f"JavaScript/TypeScript module-reference limit exceeded: {path}"
        )
    return tuple(sorted(set(references)))


def _tokenize(text: str, *, path: str) -> tuple[_Token, ...]:
    tokens: list[_Token] = []
    index = 0
    line = 1
    previous: _Token | None = None
    while index < len(text):
        char = text[index]
        if (index == 0 or (index == 1 and text[0] == "\ufeff")) and text.startswith(
            "#!", index
        ):
            newline = text.find("\n", index + 2)
            if newline < 0:
                break
            index = newline
            continue
        if char in " \t\r\n\ufeff":
            if char == "\n":
                line += 1
            index += 1
            continue
        if text.startswith("//", index):
            newline = text.find("\n", index + 2)
            if newline < 0:
                break
            index = newline
            continue
        if text.startswith("/*", index):
            end = text.find("*/", index + 2)
            if end < 0:
                raise ECMAScriptModuleEvidenceError(
                    f"unterminated JavaScript/TypeScript block comment: {path}"
                )
            line += text.count("\n", index, end + 2)
            index = end + 2
            continue
        if _is_word_apostrophe(text, index):
            token = _Token("punctuation", char, line, line)
            index += 1
        elif char in {"'", '"'}:
            token, index, line = _read_string(
                text,
                index=index,
                line=line,
                path=path,
            )
        elif char == "`":
            start_line = line
            index, line = _skip_template(
                text,
                index=index,
                line=line,
                path=path,
            )
            token = _Token("template", "", start_line, line)
        elif char == "/" and _slash_starts_regex(previous):
            start_line = line
            index, line = _skip_regex(
                text,
                index=index,
                line=line,
                path=path,
            )
            token = _Token("regex", "", start_line, line)
        elif char.isalpha() or char in {"_", "$"}:
            end = index + 1
            while end < len(text) and (
                text[end].isalnum() or text[end] in {"_", "$"}
            ):
                end += 1
            token = _Token("identifier", text[index:end], line, line)
            index = end
        elif char.isdigit():
            end = index + 1
            while end < len(text) and (
                text[end].isalnum() or text[end] in {"_", "."}
            ):
                end += 1
            token = _Token("number", text[index:end], line, line)
            index = end
        else:
            value = text[index : index + 2]
            if value not in {"=>", "++", "--", "?.", "??", "&&", "||"}:
                value = char
            token = _Token("punctuation", value, line, line)
            index += len(value)
        tokens.append(token)
        if len(tokens) > MAX_ECMASCRIPT_TOKENS:
            raise ECMAScriptModuleEvidenceError(
                f"JavaScript/TypeScript token limit exceeded: {path}"
            )
        previous = token
    return tuple(tokens)


def _read_string(
    text: str,
    *,
    index: int,
    line: int,
    path: str,
) -> tuple[_Token, int, int]:
    quote = text[index]
    start_line = line
    index += 1
    start = index
    escaped = False
    chunks: list[str] = []
    while index < len(text):
        char = text[index]
        if char == quote:
            chunks.append(text[start:index])
            return (
                _Token(
                    "string",
                    "".join(chunks),
                    start_line,
                    line,
                    escaped=escaped,
                ),
                index + 1,
                line,
            )
        if char == "\\":
            escaped = True
            chunks.append(text[start:index])
            if index + 1 >= len(text):
                break
            if text[index + 1] == "\n":
                line += 1
            chunks.append(text[index : index + 2])
            index += 2
            start = index
            continue
        if char in "\r\n":
            raise ECMAScriptModuleEvidenceError(
                f"unterminated JavaScript/TypeScript string literal: {path}"
            )
        index += 1
    raise ECMAScriptModuleEvidenceError(
        f"unterminated JavaScript/TypeScript string literal: {path}"
    )


def _skip_template(
    text: str,
    *,
    index: int,
    line: int,
    path: str,
) -> tuple[int, int]:
    index += 1
    while index < len(text):
        char = text[index]
        if char == "\\":
            if index + 1 >= len(text):
                break
            if text[index + 1] == "\n":
                line += 1
            index += 2
            continue
        if char == "`":
            return index + 1, line
        if text.startswith("${", index):
            index, line = _skip_template_expression(
                text,
                index=index + 2,
                line=line,
                path=path,
            )
            continue
        if char == "\n":
            line += 1
        index += 1
    raise ECMAScriptModuleEvidenceError(
        f"unterminated JavaScript/TypeScript template literal: {path}"
    )


def _skip_template_expression(
    text: str,
    *,
    index: int,
    line: int,
    path: str,
) -> tuple[int, int]:
    depth = 1
    previous: _Token | None = None
    while index < len(text):
        char = text[index]
        if char in " \t\r\n":
            if char == "\n":
                line += 1
            index += 1
            continue
        if text.startswith("//", index):
            newline = text.find("\n", index + 2)
            if newline < 0:
                raise ECMAScriptModuleEvidenceError(
                    f"unterminated JavaScript/TypeScript template expression: {path}"
                )
            index = newline
            continue
        if text.startswith("/*", index):
            end = text.find("*/", index + 2)
            if end < 0:
                raise ECMAScriptModuleEvidenceError(
                    f"unterminated JavaScript/TypeScript block comment: {path}"
                )
            line += text.count("\n", index, end + 2)
            index = end + 2
            continue
        if _is_word_apostrophe(text, index):
            previous = _Token("punctuation", char, line, line)
            index += 1
            continue
        if char in {"'", '"'}:
            previous, index, line = _read_string(
                text,
                index=index,
                line=line,
                path=path,
            )
            continue
        if char == "`":
            start_line = line
            index, line = _skip_template(
                text,
                index=index,
                line=line,
                path=path,
            )
            previous = _Token("template", "", start_line, line)
            continue
        if char == "/" and _slash_starts_regex(previous):
            start_line = line
            index, line = _skip_regex(
                text,
                index=index,
                line=line,
                path=path,
            )
            previous = _Token("regex", "", start_line, line)
            continue
        if char == "{":
            depth += 1
            previous = _Token("punctuation", char, line, line)
            index += 1
            continue
        if char == "}":
            depth -= 1
            if depth == 0:
                return index + 1, line
            previous = _Token("punctuation", char, line, line)
            index += 1
            continue
        if char.isalpha() or char in {"_", "$"}:
            end = index + 1
            while end < len(text) and (
                text[end].isalnum() or text[end] in {"_", "$"}
            ):
                end += 1
            previous = _Token("identifier", text[index:end], line, line)
            index = end
            continue
        value = text[index : index + 2]
        if value not in {"=>", "++", "--", "?.", "??", "&&", "||"}:
            value = char
        previous = _Token("punctuation", value, line, line)
        index += len(value)
    raise ECMAScriptModuleEvidenceError(
        f"unterminated JavaScript/TypeScript template expression: {path}"
    )


def _skip_regex(
    text: str,
    *,
    index: int,
    line: int,
    path: str,
) -> tuple[int, int]:
    index += 1
    in_character_class = False
    while index < len(text):
        char = text[index]
        if char == "\\":
            index += 2
            continue
        if char in "\r\n":
            raise ECMAScriptModuleEvidenceError(
                f"unterminated JavaScript/TypeScript regular expression: {path}"
            )
        if char == "[":
            in_character_class = True
        elif char == "]":
            in_character_class = False
        elif char == "/" and not in_character_class:
            index += 1
            while index < len(text) and text[index].isalpha():
                index += 1
            return index, line
        index += 1
    raise ECMAScriptModuleEvidenceError(
        f"unterminated JavaScript/TypeScript regular expression: {path}"
    )


def _slash_starts_regex(previous: _Token | None) -> bool:
    if previous is None:
        return True
    if previous.kind == "identifier":
        return previous.value in _REGEX_PREFIX_IDENTIFIERS
    return (
        previous.kind == "punctuation"
        and previous.value
        and previous.value[0] in _REGEX_PREFIX_PUNCTUATION
    )


def _is_word_apostrophe(text: str, index: int) -> bool:
    return (
        text[index] == "'"
        and index > 0
        and index + 1 < len(text)
        and text[index - 1].isalnum()
        and text[index + 1].isalpha()
    )


def _extract_module_references(tokens: tuple[_Token, ...], *, path: str) -> list[str]:
    references: list[str] = []
    brace_depth = 0
    paren_depth = 0
    bracket_depth = 0
    previous: _Token | None = None
    index = 0
    while index < len(tokens):
        token = tokens[index]
        at_top_level = brace_depth == paren_depth == bracket_depth == 0
        if (
            at_top_level
            and token.kind == "identifier"
            and token.value in {"import", "export"}
            and _is_statement_start(previous, token)
        ):
            reference, consumed = _parse_module_declaration(
                tokens,
                index=index,
                path=path,
            )
            if reference is not None:
                references.append(reference)
            if consumed > index:
                previous = tokens[consumed]
                index = consumed + 1
                continue
        if token.kind == "punctuation":
            if token.value == "{":
                brace_depth += 1
            elif token.value == "}":
                brace_depth -= 1
            elif token.value == "(":
                paren_depth += 1
            elif token.value == ")":
                paren_depth -= 1
            elif token.value == "[":
                bracket_depth += 1
            elif token.value == "]":
                bracket_depth -= 1
            if min(brace_depth, paren_depth, bracket_depth) < 0:
                raise ECMAScriptModuleEvidenceError(
                    f"unbalanced JavaScript/TypeScript lexical structure: {path}"
                )
        previous = token
        index += 1
    if brace_depth or paren_depth or bracket_depth:
        raise ECMAScriptModuleEvidenceError(
            f"unbalanced JavaScript/TypeScript lexical structure: {path}"
        )
    return references


def _is_statement_start(previous: _Token | None, current: _Token) -> bool:
    if previous is None or previous.value in {";", "}"}:
        return True
    if current.line <= previous.end_line:
        return False
    return previous.kind in {"identifier", "number", "string", "template", "regex"} or (
        previous.kind == "punctuation" and previous.value in {")", "]", "++", "--"}
    )


def _parse_module_declaration(
    tokens: tuple[_Token, ...],
    *,
    index: int,
    path: str,
) -> tuple[str | None, int]:
    keyword = tokens[index].value
    if index + 1 >= len(tokens):
        if keyword == "import":
            raise ECMAScriptModuleEvidenceError(
                f"incomplete JavaScript/TypeScript import declaration: {path}"
            )
        return None, index
    next_token = tokens[index + 1]
    if keyword == "import":
        if next_token.value in {"(", "."}:
            return None, index
        if next_token.kind == "string":
            return _module_reference("esm-import", next_token, path=path), index + 1
        return _parse_import_from(tokens, index=index, path=path)
    return _parse_export_from(tokens, index=index, path=path)


def _parse_import_from(
    tokens: tuple[_Token, ...],
    *,
    index: int,
    path: str,
) -> tuple[str, int]:
    local_depth = 0
    cursor = index + 1
    while cursor < len(tokens):
        token = tokens[cursor]
        if token.value in {"{", "(", "["}:
            local_depth += 1
        elif token.value in {"}", ")", "]"}:
            local_depth -= 1
            if local_depth < 0:
                break
        elif local_depth == 0 and token.value == ";":
            break
        elif local_depth == 0 and token.kind == "identifier" and token.value == "from":
            if cursor + 1 < len(tokens) and tokens[cursor + 1].kind == "string":
                module = tokens[cursor + 1]
                return _module_reference("esm-import", module, path=path), cursor + 1
            break
        elif (
            local_depth == 0
            and token.value == "="
            and cursor + 3 < len(tokens)
            and tokens[cursor + 1].value == "require"
            and tokens[cursor + 2].value == "("
            and tokens[cursor + 3].kind == "string"
        ):
            module = tokens[cursor + 3]
            if cursor + 4 >= len(tokens) or tokens[cursor + 4].value != ")":
                break
            return _module_reference("ts-import-equals", module, path=path), cursor + 4
        cursor += 1
    raise ECMAScriptModuleEvidenceError(
        f"unsupported or malformed JavaScript/TypeScript import declaration: {path}"
    )


def _parse_export_from(
    tokens: tuple[_Token, ...],
    *,
    index: int,
    path: str,
) -> tuple[str | None, int]:
    cursor = index + 1
    if tokens[cursor].value == "type" and cursor + 1 < len(tokens):
        cursor += 1
    if tokens[cursor].value == "*":
        cursor += 1
        if cursor + 1 < len(tokens) and tokens[cursor].value == "as":
            cursor += 2
        if (
            cursor + 1 < len(tokens)
            and tokens[cursor].value == "from"
            and tokens[cursor + 1].kind == "string"
        ):
            return _module_reference("esm-export", tokens[cursor + 1], path=path), cursor + 1
        raise ECMAScriptModuleEvidenceError(
            f"unsupported or malformed JavaScript/TypeScript export declaration: {path}"
        )
    if tokens[cursor].value != "{":
        return None, index
    depth = 1
    cursor += 1
    while cursor < len(tokens) and depth:
        if tokens[cursor].value == "{":
            depth += 1
        elif tokens[cursor].value == "}":
            depth -= 1
        cursor += 1
    if depth:
        raise ECMAScriptModuleEvidenceError(
            f"unsupported or malformed JavaScript/TypeScript export declaration: {path}"
        )
    if (
        cursor + 1 < len(tokens)
        and tokens[cursor].value == "from"
        and tokens[cursor + 1].kind == "string"
    ):
        return _module_reference("esm-export", tokens[cursor + 1], path=path), cursor + 1
    return None, cursor - 1


def _module_reference(kind: str, token: _Token, *, path: str) -> str:
    if token.escaped:
        raise ECMAScriptModuleEvidenceError(
            f"escaped JavaScript/TypeScript module specifier is unsupported: {path}"
        )
    if len(token.value) > MAX_ECMASCRIPT_MODULE_SPECIFIER_CHARS:
        raise ECMAScriptModuleEvidenceError(
            f"JavaScript/TypeScript module specifier exceeds its limit: {path}"
        )
    if any(ord(char) < 32 or ord(char) == 127 for char in token.value):
        raise ECMAScriptModuleEvidenceError(
            f"JavaScript/TypeScript module specifier contains a control character: {path}"
        )
    return f"{kind}:{token.value}"
