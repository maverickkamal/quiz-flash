from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from firebase_admin import firestore
from routes.firebase_utils import initialize_firebase, get_user_data, save_quiz_to_firebase
from quiz_document import generate_quiz_document
from quiz_link import generate_quiz_link
from quiz_topic import generate_quiz_topic
from quiz_image import generate_quiz_image

router = APIRouter()


# Define Pydantic models
class QuizText(BaseModel):
    content: str
    number_of_questions: int
    question_type: str

class QuizLink(BaseModel):
    link: str
    number_of_questions: int
    question_type: str

class QuizFile(BaseModel):
    file_name: str
    number_of_questions: int
    question_type: str

class QuizTopic(BaseModel):
    topic: str
    subject: str
    number_of_questions: int
    question_type: str

class QuizFolder(BaseModel):
    title: str
    description: str
    category: str
    total_questions: Optional[int] = None

class QuizUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    total_questions: Optional[int] = None

# Helper function to get Firestore client
def get_db():
    return firestore.client()

# Routes
@router.post("/users/{user_id}/quizzes/{quiz_id}/generate_quiz")
async def create_quiz(quiz_input: QuizText, user_id: str, quiz_id: str):
    try:
        user_data = get_user_data(user_id)
        if user_data is None:
            raise HTTPException(status_code=404, detail="User not found")
        
        quiz = generate_quiz_document(
            quiz_input.content,
            quiz_input.number_of_questions,
            quiz_input.question_type,
            user_data
        )
        save_quiz_to_firebase(user_id, quiz_id, quiz, quiz_input.question_type)
        return {"message": "Quiz generated and saved successfully", "quiz": quiz}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/users/{user_id}/quizzes/{quiz_id}/generate_quiz_link")
async def create_quiz_link(quiz_input: QuizLink, user_id: str, quiz_id: str):
    try:
        user_data = get_user_data(user_id)
        if user_data is None:
            raise HTTPException(status_code=404, detail="User not found")
        
        quiz = generate_quiz_link(
            quiz_input.link,
            quiz_input.number_of_questions,
            quiz_input.question_type,
            user_data
        )
        save_quiz_to_firebase(user_id, quiz_id, quiz, quiz_input.question_type)
        return {"message": "Quiz generated and saved successfully", "quiz": quiz}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/users/{user_id}/quizzes/{quiz_id}/generate_quiz_topic")
async def create_quiz_topic(quiz_input: QuizTopic, user_id: str, quiz_id: str):
    try:
        user_data = get_user_data(user_id)
        if user_data is None:
            raise HTTPException(status_code=404, detail="User not found")
        
        quiz = generate_quiz_topic(
            quiz_input.topic,
            quiz_input.subject,
            quiz_input.question_type,
            quiz_input.number_of_questions,
            user_data
        )
        print(type(quiz))
        save_quiz_to_firebase(user_id, quiz_id, quiz, quiz_input.question_type)
        return {"message": "Quiz generated and saved successfully", "quiz": quiz}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/users/{user_id}/quizzes/{quiz_id}/generate_quiz_image")
async def create_quiz_image(quiz_input: QuizFile, user_id: str, quiz_id: str):
    try:
        user_data = get_user_data(user_id)
        if user_data is None:
            raise HTTPException(status_code=404, detail="User not found")
        
        quiz = generate_quiz_image(
            quiz_input.file_name,
            quiz_input.number_of_questions,
            quiz_input.question_type,
            user_data
        )
        save_quiz_to_firebase(user_id, quiz_id, quiz, quiz_input.question_type)
        return {"message": "Quiz generated and saved successfully", "quiz": quiz}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/users/{user_id}/quizzes/{quiz_id}/generate_quiz_document")
async def create_quiz_document(quiz_input: QuizFile, user_id: str, quiz_id: str):
    try:
        user_data = get_user_data(user_id)
        if user_data is None:
            raise HTTPException(status_code=404, detail="User not found")
        
        quiz = generate_quiz_image(
            quiz_input.file_name,
            quiz_input.number_of_questions,
            quiz_input.question_type,
            user_data
        )
        save_quiz_to_firebase(user_id, quiz_id, quiz, quiz_input.question_type)
        return {"message": "Quiz generated and saved successfully", "quiz": quiz}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/users/{user_id}/quizzes")
async def create_quiz_folder(folder: QuizFolder, user_id: str, db: firestore.Client = Depends(get_db)):
    try:
        doc_ref = db.collection("users").document(user_id).collection("quizzes").document()
        doc_ref.set(folder.dict())
        return {"message": "Quiz folder created successfully", "quiz_id": doc_ref.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/users/{user_id}/quizzes/{quiz_id}")
async def update_quiz_folder(quiz_id: str, folder_update: QuizUpdate, user_id: str, db: firestore.Client = Depends(get_db)):
    try:
        folder_ref = db.collection("users").document(user_id).collection("quizzes").document(quiz_id)
        folder_ref.update(folder_update.dict(exclude_unset=True))
        return {"message": "Quiz folder updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/users/{user_id}/quizzes/{quiz_id}")
async def delete_quiz_folder(quiz_id: str, user_id: str, db: firestore.Client = Depends(get_db)):
    try:
        folder_ref = db.collection("users").document(user_id).collection("quizzes").document(quiz_id)
        folder_ref.delete()
        return {"message": "Quiz folder deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/users/{user_id}/quizzes/{quiz_id}")
async def delete_quiz(quiz_id: str, user_id: str, db: firestore.Client = Depends(get_db)):
    try:
        quiz_ref = db.collection("users").document(user_id).collection("quizzes").document(quiz_id)
        quiz_ref.delete()
        return {"message": "Quiz deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

