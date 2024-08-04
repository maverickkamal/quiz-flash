from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import random
from firebase_admin import firestore
from routes.firebase_utils import initialize_firebase
from datetime import datetime

router = FastAPI()

# Initialize Firestore 

db = firestore.client()

# ML model weights
weights = {
    "correct": 0.5,
    "confidence": 0.3,
    "time_to_answer": -0.2
}

class QuizAnswer(BaseModel):
    question_id: str
    is_correct: bool
    confidence_level: int
    time_to_answer: float

@router.post("/users/{user_id}/quizzes/{quiz_id}/next-question")
async def get_next_question(user_id: str, quiz_id: str, answer: QuizAnswer):
    # Validate user and quiz
    user_ref = db.collection("users").document(user_id)
    quiz_ref = user_ref.collection("quizzes").document(quiz_id)
    
    if not quiz_ref.get().exists:
        raise HTTPException(status_code=404, detail="Quiz not found")

    # Normalize inputs
    normalized_confidence = answer.confidence_level / 5
    normalized_time = min(answer.time_to_answer / 60, 1)

    # Calculate difficulty score
    difficulty_score = (
        weights["correct"] * int(answer.is_correct) +
        weights["confidence"] * normalized_confidence +
        weights["time_to_answer"] * normalized_time
    )

    # Determine next difficulty
    if difficulty_score > 0.6:
        next_difficulty = "Hard"
    elif difficulty_score > 0.3:
        next_difficulty = "Medium"
    else:
        next_difficulty = "Easy"

    
    progress_ref = quiz_ref.collection('progress')
    progress_query = progress_ref.order_by('last_updated', direction=firestore.Query.DESCENDING).limit(1)
    progress_docs = progress_query.get()
    
    if progress_docs:
        progress_doc = progress_docs[0]
        progress_data = progress_doc.to_dict()
        completed_questions = progress_data.get('completed_questions', [])
        completed_questions.append(answer.question_id)
        progress_doc.reference.update({
            'completed_questions': completed_questions,
            'current_difficulty': next_difficulty,
            'score': firestore.Increment(1 if answer.is_correct else 0),
            'last_updated': firestore.SERVER_TIMESTAMP
        })
    else:
        progress_ref.add({
            'completed_questions': [answer.question_id],
            'current_difficulty': next_difficulty,
            'score': 1 if answer.is_correct else 0,
            'last_updated': firestore.SERVER_TIMESTAMP
        })
    completed_questions = progress_data.get('completed_questions', [])
    # Get next question from Firestore
    questions_ref = quiz_ref.collection('questions')
    questions = questions_ref.where('difficulty', '==', next_difficulty).stream()

    # Convert to list and filter out completed questions
    available_questions = [q.to_dict() | {"id": q.id} for q in questions if q.id not in completed_questions]

    if not available_questions:
        raise HTTPException(status_code=404, detail="No more questions available")

    # Randomly select next question
    next_question = random.choice(available_questions)

    # Update ML model weights (simple gradient descent)
    learning_rate = 0.01
    target = 1 if next_difficulty == "Hard" else 0.5 if next_difficulty == "Medium" else 0
    error = target - difficulty_score

    weights["correct"] += learning_rate * error * int(answer.is_correct)
    weights["confidence"] += learning_rate * error * normalized_confidence
    weights["time_to_answer"] += learning_rate * error * normalized_time

    return {"next_question": next_question, "next_difficulty": next_difficulty}

