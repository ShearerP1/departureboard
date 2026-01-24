# app.py
from flask import Flask, jsonify, render_template
import requests, time
from datetime import datetime
from zoneinfo import ZoneInfo
from cache import Cache

# importing os module for environment variables
import os
# importing necessary functions from dotenv library
from dotenv import load_dotenv, dotenv_values 
# loading variables from .env file
load_dotenv() 

# accessing and printing value
API_KEY = os.environ["SL_KEY"]
DEFAULT_STATION_ID = "740000031" # Flemingsberg

STATION_NAMES_LOOKUP = {
  "740000031": "Flemingsberg",
  "740000001": "Stockholm Centralstation"
}

CACHE_TTL = 150  # 2.5 minutes
cache = Cache()

app = Flask(__name__)


def fetch_departures(station_id):
    url = (
        f"https://api.resrobot.se/v2.1/departureBoard"
        f"?id={station_id}"
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
        ).replace(tzinfo=ZoneInfo("Europe/Stockholm"))

        departures.append({
            "name": d.get("name"),
            "direction": d.get("direction"),
            "track": d.get("track", ""),
            "departure_ts": int(dep_dt.timestamp())
        })

    return departures

def get_cached_departures(station_id):
    cached_data = cache.get(station_id)
    if cached_data:
        return cached_data
    
    data = fetch_departures(station_id)
    cache.set(station_id=station_id, data=data, ttl=CACHE_TTL)
    return data

@app.route("/data/<station_id>")
def data(station_id):
    return jsonify(get_cached_departures(station_id))

@app.route("/")
@app.route("/<station_id>")
def index(station_id=DEFAULT_STATION_ID):
    station_name = STATION_NAMES_LOOKUP.get(station_id, station_id) # Just use ID if name is not found in lookup
    return render_template("index.html",station_id=station_id, station_name=station_name)

#adding for railway compatibility
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
