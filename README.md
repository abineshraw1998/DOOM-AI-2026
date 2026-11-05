# DOOM-AI-2026
# DOOM AI — Digital Observatory of Our Multiverse

**Global Intelligence Command Center**

**Developer:** Abinesh Boopal  
**Hackathon:** Meta Global AI Developer Hackathon 2026  
**Track:** Indie Developer Track  
**Challenge:** Build for Your World

## Project Overview

DOOM AI is an interactive Global Intelligence Command Center that brings together seven missions in one platform.

Inspired by the challenge **Build for Your World**, the project explores how artificial intelligence, public scientific data, interactive 3D visualizations, and educational simulations can help people better understand our shared world.

## The Seven Missions

1. **Communication Intelligence (`app.py`)** — Meta Muse Spark 1.3-assisted translation, respectful rewriting, language guidance, accessibility, and speech features.
2. **Nature & Earth Intelligence (`nature.py`)** — Interactive 3D globe with weather, earthquakes, reported natural events, and geographic exploration.
3. **Space Intelligence (`space.py`)** — ISS visualization, calculated satellite positions, rocket launch information, NASA resources, and experimental astronomy assistance.
4. **Flight Intelligence (`flight.py`)** — Aircraft visualization using available OpenSky observations and a clearly labeled simulated demonstration mode.
5. **Communication Impact Simulator (`impact.py`)** — Rule-based estimates of message warmth, clarity, calmness, and urgency, with suggested improvements.
6. **Earth Quest (`Earth_Quest.py`)** — Geography exploration and interactive environmental conservation challenges.
7. **Wildlife Guardian (`wildlife.py`)** — Educational wildlife habitat reference markers, conservation information, and rescue challenges.

## Technology

- Python and Tkinter
- HTML, CSS, and JavaScript
- Globe.gl and Three.js
- Meta Muse Spark 1.3 through the Meta Model API
- Public environmental, aviation, and space information services
- Skyfield for orbital calculations
- Text-to-speech functionality

## How to Run

1. Install Python and the required dependencies for the mission you want to use.
2. Download or clone this repository.
3. Open the project folder in a terminal.
4. For AI-assisted features, configure your own API credentials using the `MODEL_API_KEY` environment variable. Never publish API credentials.
5. Launch the main interface:

```bash
python doom_launcher.py
```

Some missions require internet access and availability of external public data services.

## Demo Video

**YouTube demo:** Add your unlisted YouTube video URL here.

## Project Documents

- `DOOM AI.pptx` — Project presentation
- `DOOM_AI_Defect_Report.docx` — Known defects, testing observations, and limitations

## Known Limitations

- The Space Intelligence astronomy assistant has a known response issue.
- External public data services may be unavailable or incomplete.
- Satellite positions are calculated from published orbital data, not direct live telemetry.
- Flight simulation data is clearly distinguished from observed aircraft.
- Communication impact scores are rule-based educational estimates.
- Wildlife and Earth Quest markers are educational references, not live tracking.

## Future Development

**DOOM AI Lens** is a proposed future feature for camera-based educational recognition of plants, animals, and everyday objects. It is not part of the current prototype.

## References and Acknowledgments

- Meta AI — https://ai.meta.com/
- NASA — https://www.nasa.gov/
- NASA Worldview — https://worldview.earthdata.nasa.gov/
- NASA EONET — https://eonet.gsfc.nasa.gov/
- USGS Earthquake Hazards — https://earthquake.usgs.gov/
- Open-Meteo — https://open-meteo.com/
- OpenStreetMap — https://www.openstreetmap.org/
- Nominatim — https://nominatim.org/
- CelesTrak — https://celestrak.org/
- Skyfield — https://rhodesmill.org/skyfield/
- OpenSky Network — https://opensky-network.org/
- The Space Devs — https://thespacedevs.com/
- Globe.gl — https://globe.gl/
- Three.js — https://threejs.org/

## Vision

**One platform. Seven missions. A world of discovery.**

Developed by **Abinesh Boopal** for the Meta Global AI Developer Hackathon 2026.
