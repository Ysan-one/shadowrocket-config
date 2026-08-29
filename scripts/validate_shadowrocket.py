#!/usr/bin/env python3
"""Small offline checks for the maintained Shadowrocket V2 files."""

from __future__ import annotations

import ipaddress
from pathlib import Path
import sys


CONFIG = Path("Shadowrocket-v2.conf")
LEGACY_CONFIG = Path("Shadowrocket.conf")
VOICE_RULES = Path("rules/ChatGPT-Voice.list")
PODCAST_RULES = Path("Apple-Podcasts-Direct.list")
WECHAT_RULE_URL = (
    "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/"
    "rule/Clash/WeChat/WeChat.list"
)
ADULT_RULE_URL = (
    "https://raw.githubusercontent.com/ACL4SSR/ACL4SSR/master/"
    "Clash/Ruleset/Porn.list"
)
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
    active_text = "\n".join(line for _, line in lines)
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
        ("DOMAIN", "raw.githubusercontent.com"): "PROXY",
        ("DOMAIN-SUFFIX", "githubusercontent.com"): "PROXY",
        ("DOMAIN-SUFFIX", "openai.com"): "PROXY",
        ("DOMAIN-SUFFIX", "claude.ai"): "PROXY",
        ("DOMAIN-SUFFIX", "google.com"): "PROXY",
        ("DOMAIN-SUFFIX", "onlyfans.com"): "PROXY",
        ("DOMAIN-SUFFIX", "fansly.com"): "PROXY",
        ("DOMAIN-SUFFIX", "fanvue.com"): "PROXY",
        ("DOMAIN-SUFFIX", "manyvids.com"): "PROXY",
        ("DOMAIN-SUFFIX", "justfor.fans"): "PROXY",
        ("DOMAIN-SUFFIX", "clips4sale.com"): "PROXY",
        ("DOMAIN-SUFFIX", "cam4.com"): "PROXY",
        ("DOMAIN-SUFFIX", "stripchat.com"): "PROXY",
        ("DOMAIN-SUFFIX", "myfreecams.com"): "PROXY",
        ("DOMAIN-SUFFIX", "e-hentai.org"): "PROXY",
        ("DOMAIN-SUFFIX", "exhentai.org"): "PROXY",
        ("DOMAIN-SUFFIX", "jable.tv"): "PROXY",
        ("DOMAIN-SUFFIX", "javdb.com"): "PROXY",
        ("DOMAIN-SUFFIX", "javbus.com"): "PROXY",
        ("DOMAIN-SUFFIX", "netflav.com"): "PROXY",
        ("DOMAIN-SUFFIX", "riotcdn.net"): "DIRECT",
        ("DOMAIN-SUFFIX", "pvp.net"): "PROXY",
        ("DOMAIN-SUFFIX", "rgpub.io"): "DIRECT",
        ("DOMAIN-SUFFIX", "rstatic.net"): "DIRECT",
        ("DOMAIN-SUFFIX", "leagueoflegends.com"): "DIRECT",
        ("DOMAIN", "l3cdn.riotgames.com"): "DIRECT",
        ("DOMAIN-SUFFIX", "patcher.riotgames.com"): "DIRECT",
        ("DOMAIN-SUFFIX", "lolm.qq.com"): "DIRECT",
        ("DOMAIN-SUFFIX", "gamedl.qq.com"): "DIRECT",
        ("DOMAIN-SUFFIX", "gcloudcs.com"): "DIRECT",
        ("DOMAIN-SUFFIX", "auth.riotgames.com"): "PROXY",
        ("DOMAIN-SUFFIX", "api.riotgames.com"): "PROXY",
        ("DOMAIN-SUFFIX", "pp.riotgames.com"): "PROXY",
        ("DOMAIN", "guzzoni.apple.com"): "PROXY",
        ("DOMAIN-SUFFIX", "smoot.apple.com"): "PROXY",
        ("DOMAIN-SUFFIX", "apple-relay.apple.com"): "PROXY",
        ("DOMAIN-SUFFIX", "apple-relay.cloudflare.com"): "PROXY",
        ("DOMAIN-SUFFIX", "apple-relay.fastly-edge.com"): "PROXY",
        ("DOMAIN-SUFFIX", "cp4.cloudflare.com"): "PROXY",
        ("DOMAIN-SUFFIX", "siri.apple.com"): "PROXY",
        ("DOMAIN", "mask.icloud.com"): "PROXY",
        ("DOMAIN", "mask-h2.icloud.com"): "PROXY",
        ("DOMAIN", "mask-api.icloud.com"): "PROXY",
        ("DOMAIN", "mask-api.fe2.apple-dns.net"): "PROXY",
        ("DOMAIN", "mask.apple-dns.net"): "PROXY",
        ("DOMAIN", "apple-relay.mask.apple-dns.net"): "PROXY",
        ("DOMAIN", "gspe1-ssl.ls.apple.com"): "PROXY",
        ("DOMAIN-SUFFIX", "maps.apple.com"): "DIRECT",
        ("DOMAIN", "gsp-ssl.ls.apple.com"): "DIRECT",
        ("DOMAIN-SUFFIX", "facetime.apple.com"): "DIRECT",
        ("DOMAIN-SUFFIX", "facetime.net"): "DIRECT",
        ("DOMAIN-SUFFIX", "push.apple.com"): "DIRECT",
        ("DOMAIN-SUFFIX", "applemusic.com"): "DIRECT",
        ("DOMAIN-SUFFIX", "musickit.net"): "DIRECT",
        ("DOMAIN-SUFFIX", "tv.apple.com"): "DIRECT",
        ("DOMAIN-SUFFIX", "mzstatic.com"): "DIRECT",
        ("DOMAIN-SUFFIX", "icloud-content.com"): "DIRECT",
        ("DOMAIN-SUFFIX", "gateway.icloud.com"): "DIRECT",
        ("DOMAIN-SUFFIX", "apple-dns.net"): "DIRECT",
        ("DOMAIN-SUFFIX", "zuche.com"): "DIRECT",
        ("DOMAIN-SUFFIX", "xueqiu.com"): "DIRECT",
        ("DOMAIN-SUFFIX", "imedao.com"): "DIRECT",
        ("DOMAIN-SUFFIX", "icbc.com.cn"): "DIRECT",
        ("DOMAIN-SUFFIX", "unionpay.com"): "DIRECT",
        ("DOMAIN-SUFFIX", "bilibili.com"): "DIRECT",
        ("DOMAIN-SUFFIX", "quark.cn"): "DIRECT",
        ("RULE-SET", WECHAT_RULE_URL.lower()): "DIRECT",
        ("RULE-SET", ADULT_RULE_URL.lower()): "PROXY",
    }
    for key, policy in required.items():
        if key not in seen or seen[key][1] != policy:
            fail(f"missing required route: {key[0]},{key[1]},{policy}")

    config_text = CONFIG.read_text(encoding="utf-8")
    if "main/rules/ChatGPT-Voice.list,PROXY" not in config_text:
        fail("ChatGPT Voice rule set is not routed through PROXY")
    if "main/Shadowrocket-v2.conf" not in config_text:
        fail("V2 update-url is missing")

    ordered_markers = [
        "DOMAIN,raw.githubusercontent.com,PROXY,force-remote-dns",
        "DOMAIN-SUFFIX,githubusercontent.com,PROXY,force-remote-dns",
        "DOMAIN-SUFFIX,riotcdn.net,DIRECT",
        "DOMAIN-SUFFIX,leagueoflegends.com,DIRECT",
        "DOMAIN-SUFFIX,lolm.qq.com,DIRECT",
        "DOMAIN-SUFFIX,auth.riotgames.com,PROXY,force-remote-dns",
        "DOMAIN-SUFFIX,siri.apple.com,PROXY,force-remote-dns",
        "DOMAIN,mask.icloud.com,PROXY,force-remote-dns",
        "DOMAIN,mask-h2.icloud.com,PROXY,force-remote-dns",
        "DOMAIN,mask-api.icloud.com,PROXY,force-remote-dns",
        "DOMAIN,mask-api.fe2.apple-dns.net,PROXY,force-remote-dns",
        "DOMAIN,mask.apple-dns.net,PROXY,force-remote-dns",
        "DOMAIN,apple-relay.mask.apple-dns.net,PROXY,force-remote-dns",
        "DOMAIN,gspe1-ssl.ls.apple.com,PROXY,force-remote-dns",
        "DOMAIN-SUFFIX,maps.apple.com,DIRECT",
        "DOMAIN-SUFFIX,facetime.apple.com,DIRECT",
        "DOMAIN-SUFFIX,applemusic.com,DIRECT",
        "DOMAIN-SUFFIX,musickit.net,DIRECT",
        "DOMAIN-SUFFIX,gateway.icloud.com,DIRECT",
        "DOMAIN-SUFFIX,ls.apple.com,PROXY,force-remote-dns",
        "DOMAIN-SUFFIX,apple.com,DIRECT",
        "DOMAIN-SUFFIX,zuche.com,DIRECT",
        "DOMAIN-SUFFIX,xueqiu.com,DIRECT",
        "DOMAIN-SUFFIX,icbc.com.cn,DIRECT",
        "RULE-SET,https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Shadowrocket/AdvertisingLite/AdvertisingLite.list,REJECT",
        f"RULE-SET,{WECHAT_RULE_URL},DIRECT",
        "DOMAIN-SUFFIX,onlyfans.com,PROXY,force-remote-dns",
        "DOMAIN-SUFFIX,fansly.com,PROXY,force-remote-dns",
        f"RULE-SET,{ADULT_RULE_URL},PROXY",
        "RULE-SET,https://raw.githubusercontent.com/Ysan-one/shadowrocket-config/main/Apple-Podcasts-Direct.list,DIRECT",
    ]
    positions = [config_text.index(marker) for marker in ordered_markers]
    if positions != sorted(positions):
        fail("Apple AI proxy and Apple direct rules are in an unsafe order")

    if "DOMAIN-SUFFIX,ls.apple.com,DIRECT" in config_text:
        fail("broad ls.apple.com direct rule can bypass Apple AI region checks")
    if "DOMAIN-KEYWORD,siri" in active_text:
        fail("broad Siri keyword rule can proxy unrelated third-party domains")
    if "DOMAIN,mask-api.fe.apple-dns.net" in active_text:
        fail("non-resolving mask-api.fe host must use the current fe2 hostname")
    if "DOMAIN,mask-t.apple-dns.net" in active_text:
        fail("non-resolving mask-t host must not be treated as a required route")
    if "DOMAIN-SUFFIX,riotgames.com,PROXY" in config_text:
        fail("broad riotgames.com proxy rule can send mainland game downloads through the proxy")
    if "xpdigital/Apple-Rule" in config_text:
        fail("removed xpdigital Apple AI repository must not remain referenced")
    if "DEST-PORT,3478,DIRECT" in config_text:
        fail("port-wide UDP 3478 direct rule can bypass ChatGPT Voice proxying")
    if "rule/Shadowrocket/WeChat/WeChat.list" in config_text:
        fail("Shadowrocket WeChat list includes broad USER-AGENT routes; use the scoped list")

    first_remote_resource = min(
        config_text.index("RULE-SET,https://raw.githubusercontent.com/"),
        config_text.index("DOMAIN-SET,https://raw.githubusercontent.com/"),
    )
    github_proxy_rule = config_text.index(
        "DOMAIN,raw.githubusercontent.com,PROXY,force-remote-dns"
    )
    if github_proxy_rule > first_remote_resource:
        fail("GitHub Raw proxy rule must precede all remote rule resources")


def validate_legacy_config() -> None:
    text = LEGACY_CONFIG.read_text(encoding="utf-8")
    active_text = "\n".join(line for _, line in active_lines(LEGACY_CONFIG))
    ordered_markers = [
        "DOMAIN-SUFFIX,riotcdn.net,DIRECT",
        "DOMAIN-SUFFIX,leagueoflegends.com,DIRECT",
        "DOMAIN-SUFFIX,lolm.qq.com,DIRECT",
        "DOMAIN-SUFFIX,auth.riotgames.com,PROXY,force-remote-dns",
        "DOMAIN-SUFFIX,siri.apple.com,PROXY,force-remote-dns",
        "DOMAIN,mask.icloud.com,PROXY,force-remote-dns",
        "DOMAIN,mask-api.fe2.apple-dns.net,PROXY,force-remote-dns",
        "DOMAIN,mask.apple-dns.net,PROXY,force-remote-dns",
        "DOMAIN,apple-relay.mask.apple-dns.net,PROXY,force-remote-dns",
        "DOMAIN,gspe1-ssl.ls.apple.com,PROXY,force-remote-dns",
        "DOMAIN-SUFFIX,maps.apple.com,DIRECT",
        "DOMAIN-SUFFIX,applemusic.com,DIRECT",
        "DOMAIN-SUFFIX,musickit.net,DIRECT",
        "DOMAIN-SUFFIX,gateway.icloud.com,DIRECT",
        "DOMAIN-SUFFIX,ls.apple.com,PROXY,force-remote-dns",
        "DOMAIN-SUFFIX,apple.com,DIRECT",
        "RULE-SET,https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Shadowrocket/AdvertisingLite/AdvertisingLite.list,REJECT",
        f"RULE-SET,{WECHAT_RULE_URL},DIRECT",
        "DOMAIN-SUFFIX,onlyfans.com,PROXY,force-remote-dns",
        "DOMAIN-SUFFIX,fansly.com,PROXY,force-remote-dns",
        f"RULE-SET,{ADULT_RULE_URL},PROXY",
        "RULE-SET,https://raw.githubusercontent.com/Ysan-one/shadowrocket-config/main/Apple-Podcasts-Direct.list,DIRECT",
    ]
    try:
        positions = [text.index(marker) for marker in ordered_markers]
    except ValueError as error:
        fail(f"{LEGACY_CONFIG}: missing protected Apple route: {error}")
    if positions != sorted(positions):
        fail(f"{LEGACY_CONFIG}: Apple AI, Maps and Podcasts rules are in an unsafe order")
    if "xpdigital/Apple-Rule" in text:
        fail(f"{LEGACY_CONFIG}: removed xpdigital repository must not remain referenced")
    if "DOMAIN-KEYWORD,siri" in active_text:
        fail(f"{LEGACY_CONFIG}: broad Siri keyword rule must not be used")
    if "DOMAIN,mask-api.fe.apple-dns.net" in active_text or "DOMAIN,mask-t.apple-dns.net" in active_text:
        fail(f"{LEGACY_CONFIG}: non-resolving Apple DNS aliases must not be used")
    if "rule/Shadowrocket/WeChat/WeChat.list" in text:
        fail(f"{LEGACY_CONFIG}: broad WeChat USER-AGENT routes must not be used")


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


def validate_podcast_rules() -> None:
    allowed_types = {"DOMAIN", "DOMAIN-SUFFIX", "USER-AGENT"}
    seen: set[tuple[str, str]] = set()
    for number, line in active_lines(PODCAST_RULES):
        fields = [field.strip() for field in line.split(",")]
        if len(fields) != 2 or fields[0] not in allowed_types:
            fail(f"{PODCAST_RULES}:{number}: invalid podcast rule")
        key = (fields[0], fields[1].lower())
        if key in seen:
            fail(f"{PODCAST_RULES}:{number}: duplicate podcast matcher")
        seen.add(key)

    required = {
        ("DOMAIN-SUFFIX", "podcasts.apple.com"),
        ("DOMAIN-SUFFIX", "acast.com"),
        ("DOMAIN-SUFFIX", "buzzsprout.com"),
        ("DOMAIN-SUFFIX", "libsyn.com"),
        ("DOMAIN-SUFFIX", "podbean.com"),
        ("DOMAIN-SUFFIX", "spreaker.com"),
        ("USER-AGENT", "*podcasts*"),
    }
    missing = sorted(required - seen)
    if missing:
        fail(f"missing required Apple Podcasts routes: {missing}")

    forbidden = {"amazonaws.com", "cloudfront.net", "spotifycdn.com"}
    for rule_type, value in seen:
        if rule_type == "DOMAIN-SUFFIX" and value in forbidden:
            fail(f"podcast list contains overly broad shared CDN: {value}")


def main() -> None:
    validate_config()
    validate_legacy_config()
    validate_voice_rules()
    validate_podcast_rules()
    print("Shadowrocket V2 validation passed")


if __name__ == "__main__":
    main()
