import csv
from collections import defaultdict

# The path to your downloaded TransLink CSV
INPUT_FILE = "../data/transit_usage_history.csv"


def should_include(transaction: str) -> bool:
    """
    Returns True only for Tap in and Transfer events.
    Skips Tap out, Refund, Purchase, Loaded, etc.
    """
    return transaction.startswith("Tap in") or transaction.startswith("Transfer")


def parse_location(transaction: str) -> tuple[str, str]:
    """
    Given a transaction string like:
      "Tap in at Bus Stop 51972"
      "Transfer at Aberdeen Stn"

    Returns a tuple of (location_id, location_type) like:
      ("51972", "bus")
      ("Aberdeen Stn", "skytrain")
    """
    
    # Everything after " at " is the location
    # e.g. "Tap in at Bus Stop 51972" → "Bus Stop 51972"
    after_at = transaction.split(" at ", maxsplit=1)[1]
    
    if "Bus Stop" in after_at:
        # Last word is the stop number
        # "Bus Stop 51972" → "51972"
        stop_id = after_at.split()[-1]
        return stop_id, "bus"
    elif "Stn" in after_at:
        # The whole thing is the station name
        # "Aberdeen Stn" → "Aberdeen Stn"
        return after_at, "skytrain"
      
def parse_history(filepath: str) -> list[dict]:
    """
    Reads the TransLink CSV and returns a list of dicts, one per
    relevant tap event, each containing the location id, type,
    and the original datetime string.
    """
    results = []

    with open(filepath, newline="", encoding="utf-8-sig") as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            transaction = row["Transaction"].strip()

            if not should_include(transaction):
                continue

            location_id, location_type = parse_location(transaction)

            results.append({
                "datetime": row["DateTime"],
                "transaction": transaction,
                "location_id": location_id,
                "location_type": location_type,
            })

    return results


def count_visits(events: list[dict]) -> list[dict]:
    """
    Takes the raw list of events and collapses them into
    a visit count per location.

    Returns a list of dicts like:
      {"location_id": "51972", "location_type": "bus", "visits": 12}
    """
    counts = defaultdict(lambda: {"visits": 0, "location_type": ""})

    for event in events:
        lid = event["location_id"]
        counts[lid]["visits"] += 1
        counts[lid]["location_type"] = event["location_type"]

    return [
        {"location_id": lid, "location_type": data["location_type"], "visits": data["visits"]}
        for lid, data in counts.items()
    ]


if __name__ == "__main__":
    events = parse_history(INPUT_FILE)
    visits = count_visits(events)

    # Print a quick summary so you can sanity check the output
    print(f"Total relevant events: {len(events)}")
    print(f"Unique stops/stations visited: {len(visits)}")
    print("\nTop 10 most visited:")

    sorted_visits = sorted(visits, key=lambda x: x["visits"], reverse=True)
    for stop in sorted_visits[:10]:
        print(f"  {stop['location_id']} ({stop['location_type']}) — {stop['visits']} visits")