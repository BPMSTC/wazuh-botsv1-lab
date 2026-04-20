from datetime import datetime, timezone


def _normalize_timestamp(raw: str) -> str:
    if not raw:
        return datetime.now(tz=timezone.utc).isoformat()
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00")).astimezone(timezone.utc).isoformat()
    except ValueError:
        return datetime.now(tz=timezone.utc).isoformat()


def map_winevent_record(record: dict) -> dict:
    system = record.get("System", {})
    event_data = record.get("EventData", {})

    return {
        "lane": "winevent",
        "timestamp": _normalize_timestamp(system.get("TimeCreated")),
        "computer": system.get("Computer") or record.get("host") or "unknown-host",
        "channel": system.get("Channel", ""),
        "event_id": str(system.get("EventID", "")),
        "level": str(system.get("Level", "")),
        "keywords": system.get("Keywords", ""),
        "subject_user": event_data.get("SubjectUserName", ""),
        "target_user": event_data.get("TargetUserName", ""),
        "logon_type": event_data.get("LogonType", ""),
        "raw": record,
    }
