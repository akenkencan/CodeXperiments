#!/usr/bin/env python3
"""Convert a saved ChatGPT HTML conversation to Markdown."""

import argparse
import os
import re
from html.parser import HTMLParser
from typing import List, Tuple


class ConversationParser(HTMLParser):
    """HTML parser that extracts user and assistant messages."""

    def __init__(self):
        super().__init__()
        self.messages: List[Tuple[str, str]] = []
        self._current_role: str | None = None
        self._buffer: List[str] = []

    def handle_starttag(self, tag: str, attrs: List[tuple]) -> None:
        attr_dict = {k: v for k, v in attrs}
        classes = attr_dict.get("class", "")
        role = None
        if re.search(r"user", classes, re.IGNORECASE):
            role = "PROMPTER"
        elif re.search(r"assistant|bot|chatgpt", classes, re.IGNORECASE):
            role = "CHAT"
        if role:
            self._close_message()
            self._current_role = role

    def handle_data(self, data: str) -> None:
        if self._current_role:
            self._buffer.append(data)

    def handle_endtag(self, tag: str) -> None:
        if self._current_role and tag in {"div", "p", "span"}:
            # Attempt to close message when common containers end
            self._close_message()

    def _close_message(self) -> None:
        if self._current_role and self._buffer:
            text = "".join(self._buffer).strip()
            if text:
                self.messages.append((self._current_role, text))
        self._buffer = []
        self._current_role = None


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert a ChatGPT HTML conversation to Markdown.")
    parser.add_argument("input_file", help="HTML file from ChatGPT")
    parser.add_argument("output_file", nargs="?", help="Output Markdown file")
    return parser.parse_args()


def convert_html_to_markdown(path: str) -> List[Tuple[str, str]]:
    parser = ConversationParser()
    with open(path, "r", encoding="utf-8") as f:
        parser.feed(f.read())
    parser.close()
    return parser.messages


def write_markdown(messages: List[Tuple[str, str]], path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for role, text in messages:
            f.write(f"{role}:\n{text}\n\n")


def main() -> None:
    args = parse_arguments()
    if not os.path.isfile(args.input_file):
        raise SystemExit("Input file not found")
    output = args.output_file or os.path.splitext(args.input_file)[0] + ".md"
    messages = convert_html_to_markdown(args.input_file)
    write_markdown(messages, output)
    print(f"Wrote {len(messages)} messages to {output}")


if __name__ == "__main__":
    main()
"""
Usage:
  python html_chat_to_md.py chat.html output.md
"""
