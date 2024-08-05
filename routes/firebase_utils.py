import random
from datetime import datetime 
import firebase_admin
import os
import json
from firebase_admin import credentials, firestore


field_id = str(random.randint(10000, 99999))





def initialize_firebase():
    """Initializes Firebase app with credentials."""
    cred = credentials.Certificate(os.environ.get("credentials.json"))
    firebase_admin.initialize_app(cred)


def get_user_data(user_id):
    """Retrieves user data from Firestore, excluding sensitive 'houseData'."""
    db = firestore.client()
    doc_ref = db.collection("personalize_info").document(user_id)
    doc = doc_ref.get()
    if doc.exists:
        data = doc.to_dict()
        if "houseData" in data:
            del data["houseData"]
        return data
    else:
        return None


def save_quiz_to_firebase(user_id, quiz_id, quiz, question_type):
    """Saves generated quiz to Firestore."""
    print('start....')
    db = firestore.client()
    user_ref = db.collection("users").document(user_id).collection("quizzes").document(quiz_id)
    print('Loaded db')
    questions_collection = user_ref.collection("questions")
    print('accessing doc....')

    for q in quiz:
        # Create a new document for each question
        doc_ref = questions_collection.document()
        doc_ref.set(q)

initialize_firebase()
