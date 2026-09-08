

from datetime import datetime, timezone
from exceptions import ValidationError

def confidence_score(sources):
    if not sources:
        return {"level": "Low", "reason": "No sources found"}

    try:
        dates = []
        for source in sources:
            value = source.get("date") if isinstance(source, dict) else getattr(source, "date", None)
            if isinstance(value, str):
                value = datetime.fromisoformat(value.replace("Z", "+00:00"))
            if isinstance(value, datetime):
                if value.tzinfo is None:
                    value = value.replace(tzinfo=timezone.utc)
                dates.append(value)
    except Exception as e:
        raise ValidationError(f"Invalid source date format: {e}")

    categories = {source.get("category") for source in sources if isinstance(source, dict)}
    baseline_count = sum(
        1 for source in sources
        if isinstance(source, dict) and source.get("source") == "Built-in planning baseline"
    )

    if not dates:
        return {
            "level": "Low",
            "reason": "Planning baselines are being used; add dated local records for a stronger estimate",
            "source_coverage": len(categories),
            "baseline_records": baseline_count,
        }

    latest_date = max(dates)

    try:
        days_old = (datetime.now(timezone.utc) - latest_date).days
    except Exception:
        raise ValidationError("Date comparison failed due to timezone mismatch")

    if days_old < 90 and len(sources) >= 3:
        level = "High"
        reason = "Recent data from multiple source categories"
    elif days_old < 180:
        level = "Medium"
        reason = "Data is moderately recent"
    else:
        level = "Low"
        reason = "Source data is outdated"
    return {
        "level": level,
        "reason": reason,
        "source_coverage": len(categories),
        "baseline_records": baseline_count,
        "latest_source_date": latest_date.date().isoformat(),
    }
