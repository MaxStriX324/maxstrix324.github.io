#!/usr/bin/env python3
"""Render public laboratory tool cards from data/lab-tools.json.

The website repository is the source of truth. Optionally pass the locally
checked-out profile README to keep github.com/MaxStriX324/MaxStriX324 aligned.
No network access or third-party libraries are required.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
START = "<!-- LAB_TOOLS_GENERATED_START -->"
END = "<!-- LAB_TOOLS_GENERATED_END -->"


def escape(value: str) -> str:
    return html.escape(value, quote=True)


def markdown(value: str) -> str:
    return value.replace("|", r"\|").replace("\n", " ")


def load_tools() -> list[dict[str, str]]:
    catalog = json.loads((ROOT / "data/lab-tools.json").read_text(encoding="utf-8"))
    if catalog.get("schema_version") != 1:
        raise ValueError("Unsupported catalog version")
    tools = catalog["tools"]
    if not isinstance(tools, list) or not tools:
        raise ValueError("tools must be a nonempty list")
    seen: set[str] = set()
    fields = (
        "slug", "title", "repository", "page", "meta", "description",
        "profile_task", "profile_result", "input", "output",
        "workflow", "warning",
    )
    for tool in tools:
        if any(not isinstance(tool.get(k), str) for k in fields):
            raise ValueError("Invalid or missing catalog field")
        if not isinstance(tool.get("tags"), list) or any(
            not isinstance(tag, str) for tag in tool["tags"]
        ):
            raise ValueError("tags must be a string list")
        slug = tool["slug"]
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug) or slug in seen:
            raise ValueError(f"Invalid or duplicate slug: {slug!r}")
        seen.add(slug)
        url = urlparse(tool["repository"])
        if url.scheme != "https" or url.netloc != "github.com":
            raise ValueError(f"Repository link must be HTTPS GitHub: {slug}")
        if tool["page"] and not re.fullmatch(r"/project/[a-z0-9-]+/", tool["page"]):
            raise ValueError(f"Invalid local page: {slug}")
    return tools


def tags(tool: dict) -> str:
    return "".join(f"<span>{escape(tag)}</span>" for tag in tool["tags"])


def href(tool: dict) -> str:
    return tool["page"] or tool["repository"]


def profile(tools: list[dict]) -> str:
    rows = [
        "## Автоматизация лаборатории — open source",
        "",
        f"{len(tools)} открытых утилит для работы с печатными платами, STM32 и лабораторными измерениями. "
        "Технические инструкции и ограничения поддерживаются в репозиториях.",
        "",
        "| Проект | Задача | Результат |",
        "| --- | --- | --- |",
    ]
    for tool in tools:
        rows.append(
            f"| **[{markdown(tool['title'])}]({tool['repository']})** "
            f"| {markdown(tool['profile_task'])} | {markdown(tool['profile_result'])} |"
        )
    rows.extend([
        "",
        "**Рабочий процесс:** " + " → ".join(t["workflow"] for t in tools) + ".",
        "",
        "**Ограничения:** " + " ".join(t["warning"] for t in tools),
        "",
        "[Описание лабораторной автоматизации на сайте →]"
        "(https://maxstrix324.github.io/project/lab-automation/)",
    ])
    return "\n".join(rows)


def homepage(tools: list[dict]) -> str:
    number = len(tools)
    summary = ", ".join(t["workflow"] for t in tools)
    return (
        '<a class="showcase-card" href="/project/lab-automation/">'
        '<p class="project-meta">KICAD · STM32 · CNC3018 · RIGOL</p>'
        '<h3>Автоматизация лаборатории</h3>'
        f'<p>{number} открытых инструментов: {escape(summary)}.</p>'
        '<div class="tags"><span>KiCad</span><span>ST-Link</span>'
        '<span>GRBL</span><span>Rigol</span></div>'
        '<span class="text-link">Инструменты и исходники →</span></a>'
    )


def catalog_cards(tools: list[dict]) -> str:
    result = []
    for tool in tools:
        link_text = "Описание проекта →" if tool["page"] else "GitHub ↗"
        result.append(
            f'<a class="detail-card" href="{escape(href(tool))}">'
            f'<div><p class="project-meta">{escape(tool["meta"])}</p>'
            f'<h3>{escape(tool["title"])}</h3>'
            f'<p>{escape(tool["description"])}</p>'
            f'<div class="tags">{tags(tool)}</div>'
            f'<span class="text-link">{link_text}</span></div></a>'
        )
    return "\n".join(result)


def lab_cards(tools: list[dict]) -> str:
    result = []
    for index, tool in enumerate(tools, start=1):
        cls = "detail-card featured-detail" if index == 1 else "detail-card"
        link_text = "Описание и исходники →" if tool["page"] else "Исходный код и инструкция ↗"
        result.append(
            f'<a class="{cls}" href="{escape(href(tool))}">'
            f'<div><p class="project-meta">{escape(tool["meta"])}</p>'
            f'<h3>{index:02d} · {escape(tool["title"])}</h3>'
            f'<p>{escape(tool["description"])}</p>'
            f'<p><strong>Вход:</strong> {escape(tool["input"])} '
            f'<strong>Выход:</strong> {escape(tool["output"])}</p>'
            f'<div class="tags">{tags(tool)}</div></div>'
            f'<span class="text-link">{link_text}</span></a>'
        )
    return "\n".join(result)


def apply_region(content: str, generated: str, target: str) -> str:
    if content.count(START) != 1 or content.count(END) != 1:
        raise ValueError(f"{target}: expected exactly one marker pair")
    a = content.index(START) + len(START)
    b = content.index(END)
    if b <= a:
        raise ValueError(f"{target}: marker order invalid")
    return content[:a] + "\n" + generated + "\n" + content[b:]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true", help="Update marked regions")
    mode.add_argument("--check", action="store_true", help="Report out-of-sync regions (default)")
    parser.add_argument(
        "--profile-readme", type=Path,
        help="README.md of a local checkout of MaxStriX324/MaxStriX324",
    )
    args = parser.parse_args()
    tools = load_tools()
    targets = {
        ROOT / "index.html": homepage(tools),
        ROOT / "project/index.html": catalog_cards(tools),
        ROOT / "project/lab-automation/index.html": lab_cards(tools),
    }
    if args.profile_readme:
        targets[args.profile_readme.resolve()] = profile(tools)
    drift = 0
    for path, generated in targets.items():
        original = path.read_text(encoding="utf-8")
        expected = apply_region(original, generated, str(path))
        if original != expected:
            drift += 1
            if args.write:
                path.write_text(expected, encoding="utf-8")
                print("UPDATED", path)
            else:
                print("OUT OF SYNC", path)
        else:
            print("OK", path)
    if drift and not args.write:
        print(f"{drift} file(s) need regeneration. Run with --write.")
        return 1
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(2)
