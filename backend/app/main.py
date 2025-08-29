# backend/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import chat
from .db.database import engine, Base

# Δημιουργεί τους πίνακες στη βάση δεδομένων (αν δεν υπάρχουν)
# Σε παραγωγικό περιβάλλον, αυτό γίνεται συνήθως με εργαλεία όπως το Alembic
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ResearchChat-AI API",
    description="API for the AI-powered personalized research assistant.",
    version="0.1.0"
)

# Ρύθμιση CORS για να επιτρέπεται η επικοινωνία από το frontend (React)
origins = [
    "http://localhost:5173", # Η default διεύθυνση του Vite dev server
    "http://localhost:3000", # Η default διεύθυνση του Create React App
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ενσωμάτωση του router για το chat
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])

@app.get("/", tags=["Root"])
def read_root():
    """Ένα απλό endpoint για να ελέγξεις αν ο server λειτουργεί."""
    return {"status": "ResearchChat-AI API is running!"}