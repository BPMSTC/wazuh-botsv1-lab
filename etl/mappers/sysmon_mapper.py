from datetime import datetime, timezone


def _normalize_timestamp(raw: str) -> str:
    if not raw:
        return datetime.now(tz=timezone.utc).isoformat()
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00")).astimezone(timezone.utc).isoformat()
    except ValueError:
        return datetime.now(tz=timezone.utc).isoformat()


def map_sysmon_record(record: dict) -> dict:
    event_data = record.get("EventData", {})
    system = record.get("System", {})
    computer = system.get("Computer") or record.get("host") or "unknown-host"

    return {
        "lane": "sysmon",
        "timestamp": _normalize_timestamp(system.get("TimeCreated")),
        "computer": computer,
        "event_id": str(system.get("EventID", "")),
        "channel": system.get("Channel", "Microsoft-Windows-Sysmon/Operational"),
        "process_image": event_data.get("Image", ""),
        "command_line": event_data.get("CommandLine", ""),
        "parent_image": event_data.get("ParentImage", ""),
        "user": event_data.get("User", ""),
        "raw": record,
    }
