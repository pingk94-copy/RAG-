from __future__ import annotations

from dataclasses import dataclass
import ipaddress
import re
from urllib.parse import urlparse


SAFETY_REFUSAL = "出于安全原因，无法回答该问题。"


@dataclass(frozen=True)
class SafetyDecision:
    allowed: bool
    reason: str | None = None
    message: str = ""

    @classmethod
    def allowed_decision(cls) -> "SafetyDecision":
        return cls(allowed=True)

    @classmethod
    def blocked(cls, reason: str) -> "SafetyDecision":
        return cls(allowed=False, reason=reason, message=SAFETY_REFUSAL)


class SafetyChecker:
    def check_question(self, question: str) -> SafetyDecision:
        normalized = question.lower()
        if _contains_prompt_injection(normalized):
            return SafetyDecision.blocked("prompt_injection")
        if _contains_dangerous_url(normalized):
            return SafetyDecision.blocked("dangerous_url")
        return SafetyDecision.allowed_decision()


def _contains_prompt_injection(text: str) -> bool:
    patterns = [
        "忽略以上",
        "忽略所有",
        "ignore previous",
        "ignore all previous",
        "system prompt",
        "系统提示词",
        "开发者消息",
        "泄露",
        "越狱",
        "jailbreak",
    ]
    return any(pattern in text for pattern in patterns)


def _contains_dangerous_url(text: str) -> bool:
    for match in re.finditer(r"https?://[^\s]+", text):
        parsed = urlparse(match.group(0))
        hostname = parsed.hostname
        if not hostname:
            continue
        if hostname in {"localhost", "127.0.0.1", "0.0.0.0"}:
            return True
        try:
            address = ipaddress.ip_address(hostname)
        except ValueError:
            continue
        if address.is_private or address.is_loopback or address.is_link_local:
            return True
    return False
