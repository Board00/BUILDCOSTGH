from exceptions import ValidationError, DatabaseError
from models import Feedback

def submit_feedback(db_session, estimate_id, actual_cost, notes=""):
    if not isinstance(estimate_id, int):
        raise ValidationError("estimate_id must be an integer")

    if not isinstance(actual_cost, (int, float)):
        raise ValidationError("actual_cost must be numeric")

    try:
        feedback = Feedback(
            estimate_id=estimate_id,
            actual_cost=actual_cost,
            notes=notes
        )
        db_session.add(feedback)
        db_session.commit()
        db_session.refresh(feedback)
    except Exception as e:
        db_session.rollback()
        raise DatabaseError(f"Failed to submit feedback: {e}")

    return {
        "status": "Feedback submitted",
        "id": feedback.id,
        "submitted_at": feedback.submitted_at.isoformat()
    }
