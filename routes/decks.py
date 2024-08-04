from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from firebase_admin import firestore
from datetime import datetime


router = APIRouter()

db = firestore.client()

class Deck(BaseModel):
    name: str
    description: str

@router.post("/users/{user_id}/decks")
async def create_deck(user_id: str, deck: Deck):
    doc_ref = db.collection("users").document(user_id).collection("decks").document()
    doc_ref.set({
        "name": deck.name,
        "description": deck.description,
        "created_at": datetime.now(),
        "last_studied": None
    })
    return {"id": doc_ref.id, "message": "Deck created successfully"}

@router.get("/users/{user_id}/decks")
async def get_decks(user_id: str):
    docs = db.collection("users").document(user_id).collection("decks").stream()
    return [{"id": doc.id, **doc.to_dict()} for doc in docs]

@router.put("/users/{user_id}/decks/{deck_id}")
async def update_deck(user_id: str, deck_id: str, deck: Deck):
    doc_ref = db.collection("users").document(user_id).collection("decks").document(deck_id)
    if not doc_ref.get().exists:
        raise HTTPException(status_code=404, detail="Deck not found")
    doc_ref.update({
        "name": deck.name,
        "description": deck.description
    })
    return {"message": "Deck updated successfully"}

@router.delete("/users/{user_id}/decks/{deck_id}")
async def delete_deck(user_id: str, deck_id: str):
    doc_ref = db.collection("users").document(user_id).collection("decks").document(deck_id)
    if not doc_ref.get().exists:
        raise HTTPException(status_code=404, detail="Deck not found")
    doc_ref.delete()
    return {"message": "Deck deleted successfully"}