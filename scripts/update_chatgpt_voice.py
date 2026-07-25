#!/usr/bin/env python3
"""Generate a Shadowrocket rule set from OpenAI's ChatGPT Voice IP feed."""

from __future__ import annotations

import argparse
import ipaddress
import json
import os
from pathlib import Path
import tempfile
import urllib.request


DEFAULT_SOURCE = "https://openai.com/chatgpt-voice.json"
DEFAULT_OUTPUT = Path("rules/ChatGPT-Voice.list")


def fetch_json(url: str) -> dict:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "shadowrocket-config-updater/1.0"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def extract_networks(payload: dict) -> list[ipaddress._BaseNetwork]:
    networks: set[ipaddress._BaseNetwork] = set()
    for item in payload.get("prefixes", []):
        value = item.get("ipv4Prefix") or item.get("ipv6Prefix")
        if not value:
            continue
        networks.add(ipaddress.ip_network(value, strict=True))

    if not 1 <= len(networks) <= 512:
        raise ValueError(f"unexpected prefix count: {len(networks)}")
    return sorted(networks, key=lambda network: (network.version, int(network.network_address), network.prefixlen))


def render(payload: dict, source: str) -> str:
    networks = extract_networks(payload)
    creation_time = payload.get("creationTime", "unknown")
    lines = [
        "# NAME: ChatGPT Voice",
        f"# SOURCE: {source}",
        f"# SOURCE-CREATION-TIME: {creation_time}",
        "# MANAGED-BY: scripts/update_chatgpt_voice.py",
        f"# TOTAL: {len(networks)}",
    ]
    for network in networks:
        rule_type = "IP-CIDR" if network.version == 4 else "IP-CIDR6"
        lines.append(f"{rule_type},{network},no-resolve")
    return "\n".join(lines) + "\n"


def write_if_changed(path: Path, content: str) -> bool:
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return False

    path.parent.mkdir(parents=True, exist_ok=True)
    file_descriptor, temporary_name = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.")
    try:
        with os.fdopen(file_descriptor, "w", encoding="utf-8") as output:
            output.write(content)
        os.replace(temporary_name, path)
    finally:
        if os.path.exists(temporary_name):
            os.unlink(temporary_name)
    return True


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()

    payload = fetch_json(arguments.source)
    changed = write_if_changed(arguments.output, render(payload, arguments.source))
    print(f"{'updated' if changed else 'unchanged'}: {arguments.output}")


if __name__ == "__main__":
    main()
