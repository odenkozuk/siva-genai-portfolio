"""
SEAT Coded Tool for Neuro-SAN.
Manages employee seat/asset allocation requests.
"""

from typing import Any


SEAT_ALLOCATIONS: dict[str, dict] = {}


class SEATTool:
    """Coded tool: handles seat and asset allocation for employees."""

    def async_invoke(self, args: dict[str, Any], sly_data: dict[str, Any]) -> dict[str, Any]:
        action = args.get("action")
        employee_id = args.get("employee_id")

        if action == "allocate":
            location = args.get("location", "Floor 3 - Open Bay")
            SEAT_ALLOCATIONS[employee_id] = {"location": location, "status": "allocated"}
            return {
                "status": "allocated",
                "employee_id": employee_id,
                "location": location,
                "message": f"Seat allocated at {location} for employee {employee_id}.",
            }
        elif action == "release":
            if employee_id in SEAT_ALLOCATIONS:
                del SEAT_ALLOCATIONS[employee_id]
            return {"status": "released", "employee_id": employee_id}
        elif action == "query":
            allocation = SEAT_ALLOCATIONS.get(employee_id)
            if allocation:
                return {"employee_id": employee_id, **allocation}
            return {"employee_id": employee_id, "status": "not_allocated"}

        return {"error": f"Unknown action: {action}"}
