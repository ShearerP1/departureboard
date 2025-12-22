# app.py
from flask import Flask, jsonify, render_template
import requests, time
from datetime import datetime



with open("api_key.txt", "r") as f:
    API_KEY = f.read().strip()

STATION_ID = "740000031"
CACHE_TTL = 300  # 5 minutes

app = Flask(__name__)

cache = {
    "timestamp": 0,
    "data": []
}

def fetch_departures():
    url = (
        f"https://api.resrobot.se/v2.1/departureBoard"
        f"?id={STATION_ID}"
        f"&format=json"
        f"&maxJourneys=8"
        f"&accessId={API_KEY}"
    )

    raw = requests.get(url).json()
    departures = []

    for d in raw.get("Departure", []):
        notes = d.get("Notes", {}).get("Note", [])
        if not any(n.get("txtN") == "Pendeltåg" for n in notes):
            continue

        dep_dt = datetime.strptime(
            f"{d['date']} {d['time']}",
            "%Y-%m-%d %H:%M:%S"
        )

        departures.append({
            "name": d.get("name"),
            "direction": d.get("direction"),
            "track": d.get("track", ""),
            "departure_ts": int(dep_dt.timestamp())
        })

    return departures

def get_cached_departures():
    now = time.time()
    if now - cache["timestamp"] > CACHE_TTL:
        cache["data"] = fetch_departures()
        cache["timestamp"] = now
    return cache["data"]

@app.route("/data")
def data():
    return jsonify(get_cached_departures())

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run()
