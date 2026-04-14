"""
FAQ Coded Tool for Neuro-SAN.
Answers frequently asked questions using a local knowledge base.
"""

from typing import Any


FAQ_KNOWLEDGE_BASE = {
    "vpn": "To connect to VPN, download the Cisco AnyConnect client from the IT portal and use your corporate credentials.",
    "password reset": "Visit the self-service portal at https://selfservice.company.com to reset your password without IT involvement.",
    "laptop request": "Submit a laptop request through ServiceNow under 'Hardware Request'. Approval takes 3-5 business days.",
    "onboarding": "New employee onboarding kits are issued on Day 1. IT will set up your accounts within 2 hours of joining.",
    "software install": "Submit a software installation request via ServiceNow. Licensed software will be deployed via SCCM within 24 hours.",
}


class FAQTool:
    """Coded tool: retrieves answers from the IT FAQ knowledge base."""

    def async_invoke(self, args: dict[str, Any], sly_data: dict[str, Any]) -> dict[str, Any]:
        question = args.get("question", "").lower()
        for keyword, answer in FAQ_KNOWLEDGE_BASE.items():
            if keyword in question:
                return {"answer": answer, "matched_keyword": keyword, "confidence": "high"}
        return {
            "answer": "I could not find a direct answer. Please contact the IT helpdesk or raise a ServiceNow ticket.",
            "matched_keyword": None,
            "confidence": "low",
        }
