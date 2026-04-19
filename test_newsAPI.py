from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import Optional, List

from reddit_feeds import fetch_reddit
from newsAPI_feeds import fetch_newsapi

from db import (
    init_db,
    create_user,
    save_interest,
    save_sub_interest
)

app = FastAPI(
    title="Signal Feed API",
    version="1.0.0"
)

# -----------------------------------
# Run database setup on startup
# Better than calling init_db() globally
# Prevents reload/import lock issues
# -----------------------------------
@app.on_event("startup")
def startup_event():
    init_db()


# -----------------------------------
# Pydantic Models
# -----------------------------------

class SubInterest(BaseModel):
    name: str
    weight: float


class Interest(BaseModel):
    name: str
    weight: float
    sub_interests: List[SubInterest] = []


class Location(BaseModel):
    name: str
    weight: float


class ContentMode(BaseModel):
    name: str
    weight: float


class OnboardRequest(BaseModel):
    primary_interests: List[Interest]
    secondary_interests: List[Interest]
    locations: List[Location]
    content_modes: List[ContentMode]


# -----------------------------------
# Home Route
# -----------------------------------
@app.get("/")
def home():
    return {"message": "Signal Feed Live Backend Running"}


# -----------------------------------
# Combined Feed
# Example:
# /feed?interests=technology
# -----------------------------------
@app.get("/feed")
def get_feed(interests: Optional[str] = Query("technology")):
    news_api = fetch_newsapi(query=interests)
    reddit_api = fetch_reddit(subreddit=interests)

    combined = news_api + reddit_api

    return {
        "interests": interests,
        "count": len(combined),
        "results": combined
    }


# -----------------------------------
# NewsAPI Only
# -----------------------------------
@app.get("/feed_newsapi")
def get_feed_newsapi(interests: Optional[str] = Query("technology")):
    news_api = fetch_newsapi(query=interests)

    return {
        "interests": interests,
        "count": len(news_api),
        "results": news_api
    }


# -----------------------------------
# Reddit Only
# -----------------------------------
@app.get("/feed_reddit")
def get_feed_reddit(interests: Optional[str] = Query("technology")):
    reddit_api = fetch_reddit(subreddit=interests)

    return {
        "interests": interests,
        "count": len(reddit_api),
        "results": reddit_api
    }


# -----------------------------------
# Onboard User
# Accepts JSON profile from frontend/LLM
# Saves interests + sub interests
# -----------------------------------
from db import get_connection

@app.post("/onboard")
def onboard_user(payload: OnboardRequest):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # create user
        cursor.execute(
            "INSERT INTO users (name, city) VALUES (?, ?)",
            ("New User", "Unknown")
        )
        user_id = cursor.lastrowid

        # save primary interests
        for item in payload.primary_interests:
            cursor.execute(
                "INSERT INTO user_interests (user_id, interest, weight) VALUES (?, ?, ?)",
                (user_id, item.name, item.weight)
            )

            for sub in item.sub_interests:
                cursor.execute(
                    """INSERT INTO user_sub_interests
                    (user_id, parent_interest, sub_interest, weight)
                    VALUES (?, ?, ?, ?)""",
                    (user_id, item.name, sub.name, sub.weight)
                )

        # save secondary interests
        for item in payload.secondary_interests:
            cursor.execute(
                "INSERT INTO user_interests (user_id, interest, weight) VALUES (?, ?, ?)",
                (user_id, item.name, item.weight)
            )

            for sub in item.sub_interests:
                cursor.execute(
                    """INSERT INTO user_sub_interests
                    (user_id, parent_interest, sub_interest, weight)
                    VALUES (?, ?, ?, ?)""",
                    (user_id, item.name, sub.name, sub.weight)
                )

        conn.commit()

        return {
            "message": "User onboarded successfully",
            "user_id": user_id
        }

    except Exception as e:
        conn.rollback()
        return {"error": str(e)}

    finally:
        conn.close()