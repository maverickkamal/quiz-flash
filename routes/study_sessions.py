from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from firebase_admin import firestore
from datetime import datetime


router = APIRouter()
db = firestore.client()

class StudySessionStart(BaseModel):
    deck_id: str

class StudySessionUpdate(BaseModel):
    cards_reviewed: int
    correct_answers: int

class StudySessionEnd(BaseModel):
    cards_reviewed: int
    correct_answers: int

@router.post("/users/{user_id}/study-sessions/start")
async def start_study_session(user_id: str, session_start: StudySessionStart):
    doc_ref = db.collection("users").document(user_id).collection("study_sessions").document()
    session_data = {
        "start_time": datetime.now(),
        "deck_id": session_start.deck_id,
        "cards_reviewed": 0,
        "correct_answers": 0,
        "performance_rate": 0,
        "status": "in_progress"
    }
    doc_ref.set(session_data)
    return {"session_id": doc_ref.id, "message": "Study session started"}

@router.put("/users/{user_id}/study-sessions/{session_id}/update")
async def update_study_session(user_id: str, session_id: str, session_update: StudySessionUpdate):
    doc_ref = db.collection("users").document(user_id).collection("study_sessions").document(session_id)
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Study session not found")
    
    performance_rate = session_update.correct_answers / session_update.cards_reviewed if session_update.cards_reviewed > 0 else 0
    doc_ref.update({
        "cards_reviewed": session_update.cards_reviewed,
        "correct_answers": session_update.correct_answers,
        "performance_rate": performance_rate
    })
    return {"message": "Study session updated"}

@router.put("/users/{user_id}/study-sessions/{session_id}/end")
async def end_study_session(user_id: str, session_id: str, session_end: StudySessionEnd):
    doc_ref = db.collection("users").document(user_id).collection("study_sessions").document(session_id)
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Study session not found")
    
    session_data = doc.to_dict()
    end_time = datetime.now()
    duration = (end_time - session_data["start_time"]).total_seconds()
    performance_rate = session_end.correct_answers / session_end.cards_reviewed if session_end.cards_reviewed > 0 else 0
    
    doc_ref.update({
        "end_time": end_time,
        "duration": duration,
        "cards_reviewed": session_end.cards_reviewed,
        "correct_answers": session_end.correct_answers,
        "performance_rate": performance_rate,
        "status": "completed"
    })
    return {"message": "Study session ended"}

@router.get("/users/{user_id}/study-sessions")
async def get_study_sessions(user_id: str, limit: int = 10):
    docs = db.collection("users").document(user_id).collection("study_sessions").order_by("start_time", direction=firestore.Query.DESCENDING).limit(limit).stream()
    return [{"id": doc.id, **doc.to_dict()} for doc in docs]