"""
ServiceNow Coded Tool for Neuro-SAN.
Handles incident creation, updates, and queries via ServiceNow REST API.
"""

import os
import requests
from typing import Any
from dotenv import load_dotenv

load_dotenv()

SERVICENOW_INSTANCE = os.getenv("SERVICENOW_INSTANCE")
SERVICENOW_USER = os.getenv("SERVICENOW_USER")
SERVICENOW_PASSWORD = os.getenv("SERVICENOW_PASSWORD")


class ServiceNowTool:
    """Coded tool: interacts with ServiceNow REST API for ITSM operations."""

    def async_invoke(self, args: dict[str, Any], sly_data: dict[str, Any]) -> dict[str, Any]:
        action = args.get("action")
        if action == "create":
            return self._create_incident(args)
        elif action == "update":
            return self._update_incident(args)
        elif action == "query":
            return self._query_incident(args)
        return {"error": f"Unknown action: {action}"}

    def _create_incident(self, args: dict) -> dict:
        url = f"{SERVICENOW_INSTANCE}/api/now/table/incident"
        payload = {
            "short_description": args.get("description", ""),
            "urgency": args.get("priority", "3"),
            "impact": args.get("priority", "3"),
        }
        response = requests.post(
            url,
            json=payload,
            auth=(SERVICENOW_USER, SERVICENOW_PASSWORD),
            headers={"Content-Type": "application/json"},
            timeout=30,
        )
        response.raise_for_status()
        result = response.json().get("result", {})
        return {
            "status": "created",
            "ticket_number": result.get("number"),
            "sys_id": result.get("sys_id"),
        }

    def _update_incident(self, args: dict) -> dict:
        ticket_number = args.get("ticket_number")
        url = f"{SERVICENOW_INSTANCE}/api/now/table/incident?sysparm_query=number={ticket_number}"
        response = requests.patch(
            url,
            json={"work_notes": args.get("description", "")},
            auth=(SERVICENOW_USER, SERVICENOW_PASSWORD),
            headers={"Content-Type": "application/json"},
            timeout=30,
        )
        response.raise_for_status()
        return {"status": "updated", "ticket_number": ticket_number}

    def _query_incident(self, args: dict) -> dict:
        ticket_number = args.get("ticket_number")
        url = f"{SERVICENOW_INSTANCE}/api/now/table/incident?sysparm_query=number={ticket_number}&sysparm_fields=number,state,short_description,priority"
        response = requests.get(
            url,
            auth=(SERVICENOW_USER, SERVICENOW_PASSWORD),
            headers={"Accept": "application/json"},
            timeout=30,
        )
        response.raise_for_status()
        results = response.json().get("result", [])
        if not results:
            return {"error": f"No incident found: {ticket_number}"}
        return results[0]
