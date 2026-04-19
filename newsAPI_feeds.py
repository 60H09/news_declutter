import requests
from fastapi import FastAPI, Query

from db import save_items

API_KEY = "5454d9a3a5664006a7b81c13715eb48d"
def fetch_newsapi(query="technology", limit=5):
    url = (
        f"https://newsapi.org/v2/everything?"
        f"q={query}&language=en&sortBy=publishedAt&apiKey={API_KEY}"
    )

    response = requests.get(url)
    data = response.json()

    articles = []

    for article in data.get("articles", [])[:limit]:
        articles.append({
            "title": article["title"],
            "source": article["source"]["name"],
            "url": article["url"],
            "category": query
        })
    save_items(articles)
    return articles