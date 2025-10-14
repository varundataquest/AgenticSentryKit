"""Deterministic extraction helpers used by checkers."""

from __future__ import annotations

import re
from html.parser import HTMLParser
from typing import Any, Callable, Dict, List

from ..errors import ParseError

__all__ = ["extract_css", "extract_xpath", "extract_regex"]


class _Collector(HTMLParser):
    def __init__(self, matcher: Callable[[str, Dict[str, str]], bool]) -> None:
        super().__init__(convert_charrefs=True)
        self._matcher = matcher
        self._stack: List[Dict[str, Any]] = []
        self.matches: List[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = {name: (value or "") for name, value in attrs}
        node = {"tag": tag, "attrs": attr_map, "text": [], "match": self._matcher(tag, attr_map)}
        self._stack.append(node)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_data(self, data: str) -> None:
        if self._stack:
            self._stack[-1]["text"].append(data)

    def handle_endtag(self, tag: str) -> None:
        if not self._stack:
            return
        node = self._stack.pop()
        text = " ".join(part.strip() for part in node["text"] if part.strip())
        if node["match"] and text:
            self.matches.append(text.strip())
        if self._stack and text:
            self._stack[-1]["text"].append(text)


def _normalize(selector: str) -> str:
    return selector.strip()


def _css_matcher(selector: str) -> Callable[[str, Dict[str, str]], bool]:
    tokens = re.findall(r"([#.])?([a-zA-Z0-9_-]+)", _normalize(selector))
    tag: str | None = None
    classes: set[str] = set()
    element_id: str | None = None
    for prefix, value in tokens:
        if not prefix and not tag:
            tag = value.lower()
        elif prefix == ".":
            classes.add(value.lower())
        elif prefix == "#":
            element_id = value.lower()
        elif not prefix and tag:
            classes.add(value.lower())
    if not tokens and selector:
        tag = selector.lower()

    def matcher(tag_name: str, attrs: Dict[str, str]) -> bool:
        if tag and tag_name.lower() != tag:
            return False
        if element_id and attrs.get("id", "").lower() != element_id:
            return False
        if classes:
            attr_classes = {part.lower() for part in attrs.get("class", "").split()}
            if not classes.issubset(attr_classes):
                return False
        return True

    return matcher


def _xpath_matcher(expression: str) -> Callable[[str, Dict[str, str]], bool]:
    xp = _normalize(expression)
    match = re.fullmatch(r"//([a-zA-Z0-9_-]+)(?:\[@([a-zA-Z0-9_-]+)='([^']*)'\])?", xp)
    if not match:
        raise ParseError(f"Unsupported XPath expression: {expression}")
    tag = match.group(1).lower()
    attr_name = match.group(2)
    attr_value = match.group(3)

    def matcher(tag_name: str, attrs: Dict[str, str]) -> bool:
        if tag_name.lower() != tag:
            return False
        if attr_name:
            return attrs.get(attr_name, "") == (attr_value or "")
        return True

    return matcher


def _collect(document: str, matcher: Callable[[str, Dict[str, str]], bool], must_include: str | None) -> str:
    parser = _Collector(matcher)
    parser.feed(document)
    parser.close()
    if not parser.matches:
        raise ParseError("No elements matched selector")
    text = " ".join(parser.matches).strip()
    if not text:
        raise ParseError("Matched elements contained no text")
    if must_include and must_include.lower() not in text.lower():
        raise ParseError("Required text missing from extraction result")
    return text


def extract_css(html: str, selector: str, must_include: str | None = None) -> str:
    """Extract text content from HTML using a limited CSS selector."""

    return _collect(html, _css_matcher(selector), must_include)


def extract_xpath(html: str, xp: str, must_include: str | None = None) -> str:
    """Extract text content from HTML using a limited XPath expression."""

    return _collect(html, _xpath_matcher(xp), must_include)


def extract_regex(text: str, pattern: str, flags: int = re.IGNORECASE) -> str:
    """Extract a substring using a compiled regular expression."""

    try:
        compiled = re.compile(pattern, flags)
    except re.error as exc:  # pragma: no cover - invalid pattern handled defensively
        raise ParseError(f"Invalid regular expression '{pattern}': {exc}") from exc
    match = compiled.search(text)
    if not match:
        raise ParseError(f"Regex '{pattern}' not found in corpus")
    return re.sub(r"\s+", " ", match.group(0)).strip()
