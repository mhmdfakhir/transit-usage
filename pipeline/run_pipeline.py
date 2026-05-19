import sys
import json
from parse_history import parse_history, count_visits
from match_stops import load_stops, match_stops

# The Go server passes the temp CSV path as a command line argument
HISTORY_FILE = sys.argv[1]
STOPS_FILE = "../data/stops.txt"

events = parse_history(HISTORY_FILE)
visits = count_visits(events)
bus_stops, skytrain_stops = load_stops(STOPS_FILE)
matched = match_stops(visits, bus_stops, skytrain_stops)

# Print JSON to stdout so Go can capture it
print(json.dumps(matched))