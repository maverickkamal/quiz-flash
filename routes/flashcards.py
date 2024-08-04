from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from firebase_admin import firestore
from datetime import datetime, timedelta
from dotenv import load_dotenv
from routes.ai_flashcard import generate_flashcards
from typing import List, Optional
import math

load_dotenv()

router = APIRouter()

db = firestore.client()

class Flashcard(BaseModel):
    front: str
    back: str
    deck_id: str

class AIFlashcardRequest(BaseModel):
    message: str
    deck_id: str
    file_name: Optional[str] = None

class FlashcardUpdate(BaseModel):
    quality: int

class FlashcardCreate(BaseModel):
    front: str
    back: str
    deck_id: str

@router.post("/users/{user_id}/flashcards")
async def create_flashcard(user_id: str, flashcard: Flashcard):
    doc_ref = db.collection("users").document(user_id).collection("flashcards").document()
    doc_ref.set({
        "front": flashcard.front,
        "back": flashcard.back,
        "deck_id": flashcard.deck_id,
        "created_at": datetime.now(),
        "last_reviewed": None,
        "next_review": datetime.now(),
        "ease_factor": 2.5,
        "interval": 0,
        "repetition": 0
    })
    return {"id": doc_ref.id, "message": "Flashcard created successfully"}

@router.post("/users/{user_id}/quizzes/{quiz_id}/result/{result_id}/create-flashcards")
async def create_flashcards_from_quiz(user_id: str, quiz_id: str, result_id: str):
    quiz_ref = db.collection("users").document(user_id).collection("quizzes").document(quiz_id).collection("results")
    quiz_refs = quiz_ref.document(result_id)
    quiz_doc = quiz_ref.get()
    
    if not quiz_doc.exists:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    quiz_data = quiz_doc.to_dict()
    flashcards_created = 0
    
    for question in quiz_data["questions"]:
        if not question["is_correct"]:
            flashcard_ref = db.collection("users").document(user_id).collection("flashcards").document()
            flashcard_ref.set({
                "front": question["question"],
                "back": question["correct_answer"],
                "created_at": datetime.now(),
                "last_reviewed": None,
                "next_review": datetime.now(),
                "ease_factor": 2.5,
                "interval": 0,
                "repetition": 0,
                "deck_id": quiz_data.get("deck_id", "quiz_fails"),
                "source": "quiz_fail",
                "associated_quiz_id": quiz_id
            })
            flashcards_created += 1
    
    return {"message": f"Created {flashcards_created} flashcards from failed quiz questions"}

@router.post("/users/{user_id}/flashcards/bulk")
async def create_bulk_flashcards(user_id: str, flashcards: List[FlashcardCreate]):
    batch = db.batch()
    created_count = 0

    for flashcard in flashcards:
        doc_ref = db.collection("users").document(user_id).collection("flashcards").document()
        batch.set(doc_ref, {
            "front": flashcard["front"],
            "back": flashcard["back"],
            "created_at": datetime.now(),
            "last_reviewed": None,
            "next_review": datetime.now(),
            "ease_factor": 2.5,
            "interval": 0,
            "repetition": 0,
            "deck_id": flashcard["deck_id"],
            "source": "bulk_create"
        })
        created_count += 1

    batch.commit()
    return {"message": f"Created {created_count} flashcards"}

@router.post("/users/{user_id}/flashcards/generate")
async def generate_ai_flashcards(user_id: str, request: AIFlashcardRequest):
    try:
        # Generate flashcards
        print("I am working on it....")
        flashcards = generate_flashcards(request.message, request.deck_id, request.file_name)
        print("ready to generate....")
        # Create the flashcards in bulk
        created_flashcards = await create_bulk_flashcards(user_id, flashcards)
        print("bulk create")
        
        return {"message": "AI-generated flashcards created successfully", "flashcards": created_flashcards}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users/{user_id}/flashcards/due")
async def get_due_flashcards(user_id: str, deck_id: str = None):
    query = db.collection("users").document(user_id).collection("flashcards")
    if deck_id:
        query = query.where("deck_id", "==", deck_id)
    query = query.where("next_review", "<=", datetime.now()).order_by("next_review")
    docs = query.stream()
    return [{"id": doc.id, **doc.to_dict()} for doc in docs]

@router.put("/users/{user_id}/flashcards/{flashcard_id}")
async def update_flashcard(user_id: str, flashcard_id: str, update: FlashcardUpdate):
    doc_ref = db.collection("users").document(user_id).collection("flashcards").document(flashcard_id)
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Flashcard not found")
    
    flashcard_data = doc.to_dict()
    new_data = calculate_next_review(update.quality, flashcard_data)
    doc_ref.update(new_data)
    return {"message": "Flashcard updated successfully"}

def calculate_next_review(quality: int, flashcard_data: dict) -> dict:
    ease_factor = flashcard_data["ease_factor"]
    interval = flashcard_data["interval"]
    repetition = flashcard_data["repetition"]

    if quality >= 3:
        if repetition == 0:
            interval = 1
        elif repetition == 1:
            interval = 6
        else:
            interval = math.ceil(interval * ease_factor)
        
        repetition += 1
        ease_factor += 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)
    else:
        repetition = 0
        interval = 1
        ease_factor -= 0.2
    
    ease_factor = max(1.3, ease_factor)
    next_review = datetime.now() + timedelta(days=interval)
    
    return {
        "next_review": next_review,
        "ease_factor": ease_factor,
        "interval": interval,
        "repetition": repetition,
        "last_reviewed": datetime.now()
    }