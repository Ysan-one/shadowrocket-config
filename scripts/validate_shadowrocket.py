#!/usr/bin/env python3
"""Small offline checks for the maintained Shadowrocket V2 files."""

from __future__ import annotations

import ipaddress
from pathlib import Path
import sys


CONFIG = Path("Shadowrocket-v2.conf")
VOICE_RULES = Path("rules/ChatGPT-Voice.list")
RULE_TYPES = {
    "DOMAIN",
    "DOMAIN-KEYWORD",
    "DOMAIN-SET",
    "DOMAIN-SUFFIX",
    "FINAL",
    "GEOIP",
    "IP-CIDR",
    "IP-CIDR6",
    "RULE-SET",
    "USER-AGENT",
}
POLICIES = {"DIRECT", "PROXY", "REJECT"}


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def active_lines(path: Path) -> list[tuple[int, str]]:
    if not path.exists():
        fail(f"missing file: {path}")
    return [
        (number, stripped)
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1)
        if (stripped := line.strip()) and not stripped.startswith("#")
    ]


def validate_config() -> None:
    lines = active_lines(CONFIG)
    if ("[General]" not in [line for _, line in lines]) or ("[Rule]" not in [line for _, line in lines]):
        fail("configuration must contain [General] and [Rule]")

    rule_index = next(index for index, (_, line) in enumerate(lines) if line == "[Rule]")
    rules = [(number, line) for number, line in lines[rule_index + 1 :] if not line.startswith("[")]
    if not rules or rules[-1][1] != "FINAL,DIRECT":
        fail("FINAL,DIRECT must be the last rule")

    seen: dict[tuple[str, str], tuple[int, str]] = {}
    for number, line in rules:
        fields = [field.strip() for field in line.split(",")]
        rule_type = fields[0]
        if rule_type not in RULE_TYPES:
            fail(f"{CONFIG}:{number}: unsupported rule type {rule_type}")
        if rule_type == "FINAL":
            if fields != ["FINAL", "DIRECT"]:
                fail(f"{CONFIG}:{number}: invalid FINAL rule")
            continue
        if len(fields) < 3:
            fail(f"{CONFIG}:{number}: incomplete rule")
        if fields[2] not in POLICIES:
            fail(f"{CONFIG}:{number}: unsupported policy {fields[2]}")

        key = (rule_type, fields[1].lower())
        if key in seen:
            previous_number, previous_policy = seen[key]
            fail(
                f"{CONFIG}:{number}: duplicate matcher from line {previous_number} "
                f"({previous_policy} then {fields[2]})"
            )
        seen[key] = (number, fields[2])

    required = {
        ("DOMAIN-SUFFIX", "openai.com"): "PROXY",
        ("DOMAIN-SUFFIX", "claude.ai"): "PROXY",
        ("DOMAIN-SUFFIX", "google.com"): "PROXY",
        ("DOMAIN-SUFFIX", "tv.apple.com"): "DIRECT",
        ("DOMAIN-SUFFIX", "icloud-content.com"): "DIRECT",
        ("DOMAIN-SUFFIX", "bilibili.com"): "DIRECT",
        ("DOMAIN-SUFFIX", "quark.cn"): "DIRECT",
    }
    for key, policy in required.items():
        if key not in seen or seen[key][1] != policy:
            fail(f"missing required route: {key[0]},{key[1]},{policy}")

    config_text = CONFIG.read_text(encoding="utf-8")
    if "main/rules/ChatGPT-Voice.list,PROXY" not in config_text:
        fail("ChatGPT Voice rule set is not routed through PROXY")
    if "main/Shadowrocket-v2.conf" not in config_text:
        fail("V2 update-url is missing")


def validate_voice_rules() -> None:
    networks = []
    for number, line in active_lines(VOICE_RULES):
        fields = [field.strip() for field in line.split(",")]
        if len(fields) != 3 or fields[2] != "no-resolve":
            fail(f"{VOICE_RULES}:{number}: invalid voice rule")
        expected_type = "IP-CIDR6" if ":" in fields[1] else "IP-CIDR"
        if fields[0] != expected_type:
            fail(f"{VOICE_RULES}:{number}: wrong rule type")
        networks.append(ipaddress.ip_network(fields[1], strict=True))

    if not 1 <= len(networks) <= 512:
        fail(f"unexpected ChatGPT Voice rule count: {len(networks)}")
    if len(networks) != len(set(networks)):
        fail("ChatGPT Voice list contains duplicates")


def main() -> None:
    validate_config()
    validate_voice_rules()
    print("Shadowrocket V2 validation passed")


if __name__ == "__main__":
    main()
