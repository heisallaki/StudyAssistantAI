import uuid

from sqlalchemy.orm import Session

from app.models.study_goal import StudyGoal


def list_for_user(db: Session, user_id: uuid.UUID, status: str | None = None) -> list[StudyGoal]:
    query = db.query(StudyGoal).filter(StudyGoal.user_id == user_id)
    if status is not None:
        query = query.filter(StudyGoal.status == status)
    return query.order_by(StudyGoal.target_date.is_(None), StudyGoal.target_date).all()


def get_by_id_for_user(db: Session, goal_id: uuid.UUID, user_id: uuid.UUID) -> StudyGoal | None:
    return db.query(StudyGoal).filter(StudyGoal.id == goal_id, StudyGoal.user_id == user_id).first()


def create(db: Session, user_id: uuid.UUID, data: dict) -> StudyGoal:
    goal = StudyGoal(user_id=user_id, **data)
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return goal


def update(db: Session, goal: StudyGoal, data: dict) -> StudyGoal:
    for field, value in data.items():
        setattr(goal, field, value)
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return goal


def delete(db: Session, goal: StudyGoal) -> None:
    db.delete(goal)
    db.commit()