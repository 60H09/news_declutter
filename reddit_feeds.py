import requests

from db import save_items

SUBREDDIT_MAP = {
    "world news": ["worldnews", "news", "geopolitics"],
    "india news": ["india", "indianews"],
    "politics": ["politics", "PoliticalDiscussion"],
    "geopolitics": ["geopolitics", "worldnews"],

    "ai": ["artificial", "OpenAI", "MachineLearning"],
    "technology": ["technology", "gadgets", "Futurology"],
    "programming": ["programming", "learnprogramming", "webdev"],
    "startups": ["startups", "Entrepreneur"],
    "cybersecurity": ["cybersecurity", "netsec"],

    "marketing": ["marketing", "Entrepreneur", "socialmedia"],
    "business": ["business", "Entrepreneur", "smallbusiness"],
    "sales": ["sales", "Entrepreneur"],
    "finance": ["finance", "economy"],
    "investing": ["investing", "stocks", "StockMarket"],
    "crypto": ["CryptoCurrency", "Bitcoin", "ethfinance"],

    "cricket": ["Cricket", "IPL"],
    "football": ["soccer", "football"],
    "basketball": ["nba", "basketball"],
    "tennis": ["tennis"],
    "sports": ["sports"],

    "fitness": ["fitness", "bodyweightfitness", "Gym"],
    "health": ["Health", "nutrition"],
    "nutrition": ["nutrition", "HealthyFood"],
    "mental health": ["mentalhealth", "selfimprovement"],

    "photography": ["photography", "itookapicture", "AskPhotography"],
    "cameras": ["cameras", "AskPhotography"],
    "videography": ["videography", "Filmmakers"],
    "design": ["design", "graphic_design", "UI_Design"],
    "art": ["Art", "digitalart"],

    "movies": ["movies", "TrueFilm", "boxoffice"],
    "tv shows": ["television", "NetflixBestOf"],
    "music": ["music", "listentothis"],
    "gaming": ["gaming", "pcgaming", "Games"],
    "anime": ["anime", "manga"],

    "science": ["science", "EverythingScience"],
    "space": ["space", "SpaceX"],
    "history": ["history", "AskHistorians"],
    "psychology": ["psychology", "selfimprovement"],
    "philosophy": ["philosophy"],

    "travel": ["travel", "solotravel"],
    "food": ["food", "Cooking", "AskCulinary"],
    "cooking": ["Cooking", "AskCulinary"],
    "fashion": ["fashion", "malefashionadvice"],
    "cars": ["cars", "whatcarshouldIbuy"],

    "bangalore": ["bangalore", "india"],
    "kerala": ["Kerala", "india"],
    "mumbai": ["mumbai", "india"],
    "delhi": ["delhi", "india"],

    "memes": ["memes", "dankmemes"],
    "productivity": ["productivity", "GetMotivated"],
    "self improvement": ["selfimprovement", "DecidingToBeBetter"]
}

def fetch_reddit(subreddit="technology", limit=5):
    if subreddit not in SUBREDDIT_MAP:
        subreddit = SUBREDDIT_MAP["world news"]
    else:        
        subreddit = SUBREDDIT_MAP[subreddit]
    for sub in subreddit:
        url = f"https://www.reddit.com/r/{sub}/hot.json?limit={limit}"
        print(url)
        headers = {
            "User-Agent": "signal-feed-app/0.1"
        }

    response = requests.get(url, headers=headers)
    data = response.json()

    posts = []

    for child in data["data"]["children"]:
        post = child["data"]

        posts.append({
            "title": post["title"],
            "source": f"reddit:r/{subreddit}",
            "url": "https://reddit.com" + post["permalink"],
            "category": subreddit
        })
    save_items(posts)
    return posts
