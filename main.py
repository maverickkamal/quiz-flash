from fastapi import FastAPI
from routes.firebase_utils import initialize_firebase
from routes import flashcards, decks, study_sessions
# from quiz_routes import quizzes, algorithm



app = FastAPI()


# app.include_router(algorithm.router)
# app.include_router(quizzes.router)
app.include_router(flashcards.router)
app.include_router(decks.router)
app.include_router(study_sessions.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=4000)
