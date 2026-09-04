from exceptions import ValidationError, DatabaseError
from models import Estimate, Feedback

def submit_feedback(db_session, estimate_id, actual_cost, notes=""):
    if not isinstance(estimate_id, int):
        raise ValidationError("estimate_id must be an integer")

    if not isinstance(actual_cost, (int, float)):
        raise ValidationError("actual_cost must be numeric")
    if actual_cost <= 0:
        raise ValidationError("actual_cost must be greater than zero")

    estimate = db_session.query(Estimate).filter(Estimate.id == estimate_id).first()
    if estimate is None:
        raise ValidationError("Estimate not found")

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
