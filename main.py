from fastapi import FastAPI, Query
from typing import List, Optional
import requests
app = FastAPI(
    title="Signal Feed API",
    description="Basic backend for personalized feed",
    version="1.0.0"
)

# --------------------------------------------------
# Sample data (replace later with DB / Reddit / News)
# --------------------------------------------------
content_data = [
    {
        "title": "Traffic advisory in Bangalore due to VIP movement",
        "category": "local",
        "city": "bangalore"
    },
    {
        "title": "Water supply disruption in Bangalore tomorrow",
        "category": "local",
        "city": "bangalore"
    },
    {
        "title": "New AI startup raises funding in India",
        "category": "ai",
        "city": None
    },
    {
        "title": "Instagram reels trend marketers are using",
        "category": "marketing",
        "city": None
    },
    {
        "title": "Global markets react to geopolitical tensions",
        "category": "world",
        "city": None
    },
    {
        "title": "Major football tournament updates",
        "category": "sports",
        "city": None
    }
]

# --------------------------------------------------
# Health Check
# --------------------------------------------------
@app.get("/")
def home():
    return {"message": "Signal Feed Backend Running"}

# --------------------------------------------------
# Feed Endpoint
# Example:
# /feed?city=bangalore&interests=ai,marketing
# --------------------------------------------------
@app.get("/feed")
def get_feed(
    city: Optional[str] = Query(None),
    interests: Optional[str] = Query(None)
):
    user_interests = []

    if interests:
        user_interests = [
            item.strip().lower()
            for item in interests.split(",")
        ]

    results = []

    for item in content_data:
        # Local match
        if city and item["city"] == city.lower():
            results.append(item)
            continue

        # Interest match
        if item["category"].lower() in user_interests:
            results.append(item)
            continue

        # Always include world news
        if item["category"] == "world":
            results.append(item)

    return {
        "city": city,
        "interests": user_interests,
        "count": len(results),
        "feed": results
    }