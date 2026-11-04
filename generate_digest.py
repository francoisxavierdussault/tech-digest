import os
import sys
import json
import urllib.request
from datetime import datetime

TODAY = datetime.now().strftime("%Y-%m-%d")
os.makedirs("data", exist_ok=True)
os.makedirs("digests", exist_ok=True)

def fetch_data():
    """Stage 1: Fetch raw JSON stories from Hacker News."""
    url = "https://hacker-news.firebaseio.com/v0/topstories.json"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as res:
        story_ids = json.loads(res.read().decode())[:10]

    stories = []
    for sid in story_ids:
        item_url = f"https://hacker-news.firebaseio.com/v0/item/{sid}.json"
        try:
            with urllib.request.urlopen(urllib.request.Request(item_url, headers={'User-Agent': 'Mozilla/5.0'})) as item_res:
                stories.append(json.loads(item_res.read().decode()))
        except Exception:
            continue
            
    with open(f"data/{TODAY}.json", "w", encoding="utf-8") as f:
        json.dump(stories, f, indent=2)

def build_digest():
    """Stage 2: Compile JSON into Markdown."""
    json_path = f"data/{TODAY}.json"
    if not os.path.exists(json_path):
        fetch_data()
        
    with open(json_path, "r", encoding="utf-8") as f:
        stories = json.load(f)
        
    with open(f"digests/{TODAY}.md", "w", encoding="utf-8") as f:
        f.write(f"# Tech Digest — {TODAY}\n\n")
        f.write("Curated top stories and technical updates.\n\n")
        for s in stories:
            title = s.get("title", "Untitled")
            url = s.get("url", f"https://news.ycombinator.com/item?id={s.get('id')}")
            score = s.get("score", 0)
            f.write(f"- [{title}]({url}) (Score: {score})\n")

def update_index():
    """Stage 3: Update README archive table."""
    digests = sorted([f for f in os.listdir("digests") if f.endswith(".md")], reverse=True)[:15]
    with open("README.md", "w", encoding="utf-8") as f:
        f.write("# Automated Engineering Digest\n\n")
        f.write("An automated service tracking top industry discussions, architecture write-ups, and developer news.\n\n")
        f.write("### Recent Archives\n")
        for d in digests:
            date_label = d.replace(".md", "")
            f.write(f"- [{date_label}](digests/{d})\n")

if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else "all"
    if action == "fetch":
        fetch_data()
    elif action == "build":
        build_digest()
    elif action == "index":
        update_index()
    elif action == "all":
        fetch_data()
        build_digest()
        update_index()