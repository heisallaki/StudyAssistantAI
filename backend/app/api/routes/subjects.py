import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.exceptions import SubjectNotFoundError, TopicNotFoundError
from app.db.session import get_db
from app.models.user import User
from app.schemas.subject import (
    SubjectCreate,
    SubjectDetail,
    SubjectRead,
    SubjectUpdate,
    TopicCreate,
    TopicRead,
    TopicUpdate,
)
from app.services import subject_service

router = APIRouter()


@router.get("", response_model=list[SubjectRead])
def list_subjects(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return subject_service.list_subjects(db, current_user.id)


@router.post("", response_model=SubjectRead, status_code=status.HTTP_201_CREATED)
def create_subject(
    data: SubjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return subject_service.create_subject(db, current_user.id, data)


@router.get("/{subject_id}", response_model=SubjectDetail)
def get_subject(
    subject_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return subject_service.get_subject(db, subject_id, current_user.id)
    except SubjectNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")


@router.put("/{subject_id}", response_model=SubjectRead)
def update_subject(
    subject_id: uuid.UUID,
    data: SubjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return subject_service.update_subject(db, subject_id, current_user.id, data)
    except SubjectNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")


@router.delete("/{subject_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_subject(
    subject_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        subject_service.delete_subject(db, subject_id, current_user.id)
    except SubjectNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")


@router.post("/{subject_id}/topics", response_model=TopicRead, status_code=status.HTTP_201_CREATED)
def create_topic(
    subject_id: uuid.UUID,
    data: TopicCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return subject_service.create_topic(db, subject_id, current_user.id, data)
    except SubjectNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")


@router.put("/{subject_id}/topics/{topic_id}", response_model=TopicRead)
def update_topic(
    subject_id: uuid.UUID,
    topic_id: uuid.UUID,
    data: TopicUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return subject_service.update_topic(db, subject_id, topic_id, current_user.id, data)
    except SubjectNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")
    except TopicNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found")


@router.delete("/{subject_id}/topics/{topic_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_topic(
    subject_id: uuid.UUID,
    topic_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        subject_service.delete_topic(db, subject_id, topic_id, current_user.id)
    except SubjectNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")
    except TopicNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found")