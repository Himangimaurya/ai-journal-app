from fastapi import FastAPI
from pydantic import BaseModel
import sqlite3
from transformers import pipeline
from collections import Counter
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

emotion_model = pipeline(
    "text-classification",
    model="j-hartmann/emotion-english-distilroberta-base"
)

conn = sqlite3.connect("journal.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS journal (
id INTEGER PRIMARY KEY AUTOINCREMENT,
userId TEXT,
ambience TEXT,
text TEXT,
emotion TEXT
)
""")
conn.commit()


class Journal(BaseModel):
    userId: str
    ambience: str
    text: str


class TextInput(BaseModel):
    text: str


@app.post("/api/journal")
def add_journal(entry: Journal):

    result = emotion_model(entry.text)[0]
    emotion = result["label"]

    cursor.execute(
        "INSERT INTO journal (userId, ambience, text, emotion) VALUES (?, ?, ?, ?)",
        (entry.userId, entry.ambience, entry.text, emotion)
    )

    conn.commit()

    return {
        "message": "Entry saved",
        "emotion": emotion
    }


@app.get("/api/journal/{userId}")
def get_journal(userId: str):

    rows = cursor.execute(
        "SELECT ambience, text, emotion FROM journal WHERE userId=?",
        (userId,)
    ).fetchall()

    return rows


@app.post("/api/journal/analyze")
def analyze_text(data: TextInput):

    result = emotion_model(data.text)[0]

    emotion = result["label"]

    keywords = data.text.split()[:3]

    summary = f"User expressed {emotion} feelings."

    mood_score = len(data.text) % 10

    suggestion = "Try meditation or nature walk" if emotion == "sadness" else "Keep journaling!"

    return {
        "emotion": emotion,
        "keywords": keywords,
        "summary": summary,
        "mood_score": mood_score,
        "suggestion": suggestion
    }


@app.get("/api/journal/insights/{userId}")
def get_insights(userId: str):

    rows = cursor.execute(
        "SELECT emotion, ambience FROM journal WHERE userId=?",
        (userId,)
    ).fetchall()

    if not rows:
        return {"message": "No data found"}

    emotions = [r[0] for r in rows]
    ambiences = [r[1] for r in rows]

    top_emotion = Counter(emotions).most_common(1)[0][0]
    top_ambience = Counter(ambiences).most_common(1)[0][0]

    return {
        "totalEntries": len(rows),
        "topEmotion": top_emotion,
        "mostUsedAmbience": top_ambience
    }