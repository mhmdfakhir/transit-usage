# TransLink Transit Usage Visualizer

A web app that maps your TransLink transit usage history onto an 
interactive map, showing the frequency of your visits at each stop you've
visited in the date range of the data that you provide.

Upload your TransLink trip history CSV (details on how to generate it are available below)
and instantly see a heatmap of your transit habits across Vancouver.

## Status
🚧 In progress — currently in initial setup phase.

## Planned Stack
- **Python** — data parsing and GTFS stop matching
- **Go** — REST API backend
- **Leaflet.js** — interactive map frontend
- **Docker** — containerized deployment

## Data Sources
- Personal trip history exported from the TransLink website
- GTFS static feed from TransLink Open Data