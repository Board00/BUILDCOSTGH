# # from datetime import datetime
# #
# # def confidence_score(sources):
# #     if not sources:
# #         return {"level": "Low", "reason": "No sources found"}
# #
# #     # Collect only valid dates
# #     dates = [s.date for s in sources if getattr(s, "date", None)]
# #
# #     if not dates:
# #         return {"level": "Low", "reason": "No valid dates in sources"}
# #
# #     latest_date = max(dates)
# #     # ✅ both sides are datetime now
# #     days_old = (datetime.now() - latest_date).days
# #
# #     if days_old < 90 and len(sources) >= 3:
# #         return {"level": "High", "reason": "Recent data from multiple sources"}
# #     elif days_old < 180:
# #         return {"level": "Medium", "reason": "Data moderately recent"}
# #     else:
# #         return {"level": "Low", "reason": "Data outdated"}
#
#
# from datetime import datetime
# from exceptions import ValidationError
#
# def confidence_score(sources):
#     if not sources:
#         return {"level": "Low", "reason": "No sources found"}
#
#     try:
#         dates = [
#             s.date for s in sources
#             if hasattr(s, "date") and isinstance(s.date, datetime)
#         ]
#     except Exception as e:
#         raise ValidationError(f"Invalid source date format: {e}")
#
#     if not dates:
#         return {"level": "Low", "reason": "No valid dates in sources"}
#
#     latest_date = max(dates)
#
#     try:
#         days_old = (datetime.now() - latest_date).days
#     except Exception:
#         raise ValidationError("Date comparison failed due to timezone mismatch")
#
#     if days_old < 90 and len(sources) >= 3:
#         return {"level": "High", "reason": "Recent data from multiple sources"}
#     elif days_old < 180:
#         return {"level": "Medium", "reason": "Data moderately recent"}
#     else:
#         return {"level": "Low", "reason": "Data outdated"}


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
                dates.append(value)
    except Exception as e:
        raise ValidationError(f"Invalid source date format: {e}")

    if not dates:
        return {"level": "Low", "reason": "No valid dates in sources"}

    latest_date = max(dates)

    try:
        if latest_date.tzinfo is None:
            latest_date = latest_date.replace(tzinfo=timezone.utc)
        days_old = (datetime.now(timezone.utc) - latest_date).days
    except Exception:
        raise ValidationError("Date comparison failed due to timezone mismatch")

    if days_old < 90 and len(sources) >= 3:
        return {"level": "High", "reason": "Recent data from multiple sources"}
    elif days_old < 180:
        return {"level": "Medium", "reason": "Data moderately recent"}
    else:
        return {"level": "Low", "reason": "Data outdated"}
