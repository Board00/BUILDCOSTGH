def submit_feedback(db_session, estimate_id, actual_cost, notes=""):
    db_session.execute(
        "INSERT INTO feedback (estimate_id, actual_cost, notes) VALUES (%s, %s, %s)",
        (estimate_id, actual_cost, notes)
    )
    db_session.commit()
    return {"status": "Feedback submitted"}
