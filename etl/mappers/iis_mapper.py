from datetime import datetime, timezone


def _normalize_timestamp(date_value: str, time_value: str) -> str:
    if date_value and time_value:
        raw = f"{date_value}T{time_value}+00:00"
        try:
            return datetime.fromisoformat(raw).astimezone(timezone.utc).isoformat()
        except ValueError:
            pass
    return datetime.now(tz=timezone.utc).isoformat()


def map_iis_record(record: dict) -> dict:
    return {
        "lane": "iis",
        "timestamp": _normalize_timestamp(record.get("date", ""), record.get("time", "")),
        "host": record.get("cs-host", ""),
        "source_ip": record.get("c-ip", ""),
        "method": record.get("cs-method", ""),
        "uri_stem": record.get("cs-uri-stem", ""),
        "uri_query": record.get("cs-uri-query", ""),
        "status": record.get("sc-status", ""),
        "user_agent": record.get("cs(User-Agent)", ""),
        "raw": record,
    }
