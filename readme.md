# Signal Feed API

A FastAPI backend that builds personalized content feeds using user interests and aggregates content from external sources such as Reddit and News APIs.

## Features

* User onboarding with structured interest profiles
* Personalized feed generation
* Reddit + NewsAPI aggregation
* SQLite persistence for prototype use
* Weighted interests and sub-interests
* FastAPI automatic docs

## Tech Stack

* Python 3.13+
* FastAPI
* Uvicorn
* Pydantic
* SQLite

## Project Structure

```text
.
├── test_newsAPI.py      # Main FastAPI app
├── db.py                # Database helpers
├── reddit_feeds.py      # Reddit feed fetcher
├── newsAPI_feeds.py     # News source fetcher
├── signal_feed.db       # SQLite database
└── README.md
```

## Setup

### 1. Create virtual environment

```bash
python -m venv venv
```

### 2. Activate environment

Windows:

```bash
venv\Scripts\activate
```

macOS/Linux:

```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install fastapi uvicorn pydantic requests
```

## Run the Server

```bash
uvicorn test_newsAPI:app --reload
```

Server runs at:

* [http://127.0.0.1:8000](http://127.0.0.1:8000)
* Docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## Database Improvements Implemented

## Connection Handling

* Fresh SQLite connection per operation
* `timeout=30` to reduce lock failures
* `check_same_thread=False` for FastAPI worker threads
* Connections always closed after use

## Startup Initialization

Database initialization moved to FastAPI startup event instead of module import.

Benefits:

* Avoids reload/import lock issues
* Cleaner application lifecycle

## WAL Mode

Write-Ahead Logging enabled during initialization only.

Benefits:

* Better read/write concurrency
* Reduced locking during reads

## Transaction Improvements

User onboarding uses a single transaction for all inserts:

* Create user
* Save interests
* Save sub-interests
* Commit once

Benefits:

* Faster writes
* Fewer locks
* Atomic onboarding

## API Endpoints

## GET /

Health check.

Response:

```json
{
  "message": "Signal Feed Live Backend Running"
}
```

## GET /feed?interests=technology

Returns combined NewsAPI + Reddit feed.

## GET /feed_newsapi?interests=technology

Returns NewsAPI only.

## GET /feed_reddit?interests=technology

Returns Reddit only.

## POST /onboard

Stores user profile from frontend or LLM output.

Example request:

```json
{
  "primary_interests": [
    {
      "name": "Technology",
      "weight": 0.95,
      "sub_interests": [
        {"name": "AI", "weight": 0.92}
      ]
    }
  ],
  "secondary_interests": [],
  "locations": [
    {"name": "Bengaluru", "weight": 0.9}
  ],
  "content_modes": [
    {"name": "Direct Explanations", "weight": 0.95}
  ]
}
```

Example response:

```json
{
  "message": "User onboarded successfully",
  "user_id": 1
}
```

## Common Errors

## sqlite3.OperationalError: database is locked

Fixes already applied:

* Per-request connections
* Timeout increased
* Startup initialization fixed
* Single transaction onboarding

If needed:

1. Stop server
2. Delete `signal_feed.db-wal`
3. Delete `signal_feed.db-shm`
4. Restart server

## Scaling Recommendation

SQLite is ideal for prototyping. For production or many concurrent users, migrate to PostgreSQL.

## Next Roadmap Ideas

* JWT authentication
* Saved feeds per user
* Feed ranking engine
* Background jobs / schedulers
* PostgreSQL migration
* Docker deployment
* Frontend integration
* Analytics dashboard

## License

Personal / Internal Project


## Here is prompt

You are a user interest extraction engine.

Your task:
Analyze the user based on:
- what they care about
- what they consume
- what they repeatedly ask about
- what they want to learn
- what updates they would likely want

Goal:
Return a clean ranked JSON of the user's interests.

Important:
The backend has its own routing map later.
Your job is only to detect interests accurately.

This means:
- infer hidden interests from behavior
- map niche interests into broader known interests
- rank them by relevance
- include sub-interests

Example:
- nihilism -> philosophy
- startup ideas -> startups, business
- ETFs -> investing, finance
- cameras -> photography
- conspiracy theories -> geopolitics, psychology
- self analysis -> psychology
- coding in C -> programming
- AI agents -> ai, technology

Use ONLY interests from this allowed set:

[
"world news",
"india news",
"politics",
"geopolitics",

"ai",
"technology",
"programming",
"startups",
"cybersecurity",

"marketing",
"business",
"sales",
"finance",
"investing",
"crypto",

"cricket",
"football",
"basketball",
"tennis",
"sports",

"fitness",
"health",
"nutrition",
"mental health",

"photography",
"cameras",
"videography",
"design",
"art",

"movies",
"tv shows",
"music",
"gaming",
"anime",

"science",
"space",
"history",
"psychology",
"philosophy",

"travel",
"food",
"cooking",
"fashion",
"cars",

"bangalore",
"kerala",
"mumbai",
"delhi",

"memes",
"productivity",
"self improvement"
]

Rules:
1. Return ONLY valid JSON.
2. Use only interests from the allowed set above.
3. Weights between 0.0 and 1.0
4. Higher weight = stronger relevance
5. Avoid duplicates
6. Include likely interests, not only explicit ones
7. Max 12 primary interests
8. Max 12 secondary interests
9. Sub-interests must also come from the allowed set when possible
10. Use locations only if relevant
11. No explanation text outside JSON

Return JSON in this exact structure:

{
  "primary_interests": [
    {
      "name": "",
      "weight": 0.0,
      "sub_interests": [
        {
          "name": "",
          "weight": 0.0
        }
      ]
    }
  ],
  "secondary_interests": [
    {
      "name": "",
      "weight": 0.0,
      "sub_interests": [
        {
          "name": "",
          "weight": 0.0
        }
      ]
    }
  ],
  "locations": [
    {
      "name": "",
      "weight": 0.0
    }
  ],
  "content_modes": [
    {
      "name": "",
      "weight": 0.0
    }
  ]
}