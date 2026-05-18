import csv
import json
from parse_history import parse_history, count_visits

# Paths
STOPS_FILE = "../data/stops.txt"
HISTORY_FILE = "../data/transit_usage_history.csv"
OUTPUT_FILE = "output/stops.json"


def load_stops(filepath: str) -> tuple[dict, dict]:
    """
    Reads the GTFS stops.txt and returns two lookup structures:

    bus_stops: a dict mapping stop_code → {name, lat, lon}
      e.g. {"52024": {"name": "...", "lat": 49.21, "lon": -123.14}}

    skytrain_stops: a dict mapping stop_name → {lat, lon}
      but only for rows where location_type == 1 (the station itself)
      e.g. {"Aberdeen Station": {"lat": 49.184, "lon": -123.136}}
    """
    bus_stops = {}
    skytrain_stops = {}

    with open(filepath, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        for row in reader:
            location_type = row["location_type"].strip()
            stop_code = row["stop_code"].strip()
            stop_name = row["stop_name"].strip()
            lat = row["stop_lat"].strip()
            lon = row["stop_lon"].strip()

            if location_type == "1":
                # This is a SkyTrain station
                skytrain_stops[stop_name] = {"lat": float(lat), "lon": float(lon)}
            elif stop_code:
                # This is a bus stop — keyed by stop_code
                bus_stops[stop_code] = {"name": stop_name, "lat": float(lat), "lon": float(lon)}

    return bus_stops, skytrain_stops


def find_skytrain_station(history_name: str, skytrain_stops: dict) -> dict | None:
    """
    Given a name from the customer's history like "Langara-49th Stn",
    strips "Stn" and searches for a GTFS station whose name contains
    the remaining string.

    Returns the matching station dict or None if not found.
    """
    # "Langara-49th Stn" → "Langara-49th"
    search_term = history_name.replace("Stn", "").strip()

    for gtfs_name, coords in skytrain_stops.items():
        if search_term in gtfs_name:
            return {"name": gtfs_name, **coords}

    return None


def match_stops(visits: list[dict], bus_stops: dict, skytrain_stops: dict) -> list[dict]:
    """
    Takes the visit counts from parse_history and enriches each entry
    with a name, lat, and lon from the GTFS data.

    Skips any stops it can't match and prints a warning so you know.
    """
    matched = []
    unmatched = []

    for visit in visits:
        lid = visit["location_id"]
        ltype = visit["location_type"]
        visits_count = visit["visits"]

        if ltype == "bus":
            stop = bus_stops.get(lid)
            if stop:
                matched.append({
                    "location_id": lid,
                    "location_type": "bus",
                    "name": stop["name"],
                    "lat": stop["lat"],
                    "lon": stop["lon"],
                    "visits": visits_count,
                })
            else:
                unmatched.append(lid)

        elif ltype == "skytrain":
            stop = find_skytrain_station(lid, skytrain_stops)
            if stop:
                matched.append({
                    "location_id": lid,
                    "location_type": "skytrain",
                    "name": stop["name"],
                    "lat": stop["lat"],
                    "lon": stop["lon"],
                    "visits": visits_count,
                })
            else:
                unmatched.append(lid)

    if unmatched:
        print(f"\nWarning: could not match {len(unmatched)} stop(s):")
        for u in unmatched:
            print(f"  - {u}")

    return matched


if __name__ == "__main__":
    # Step 1: parse the customer's history
    events = parse_history(HISTORY_FILE)
    visits = count_visits(events)

    # Step 2: load the GTFS stop data
    bus_stops, skytrain_stops = load_stops(STOPS_FILE)

    # Step 3: match visits to coordinates
    matched = match_stops(visits, bus_stops, skytrain_stops)

    # Step 4: write the output JSON
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(matched, f, indent=2)

    print(f"\nMatched {len(matched)} of {len(visits)} stops")
    print(f"Output written to {OUTPUT_FILE}")