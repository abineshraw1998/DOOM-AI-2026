import os
import json
import time
import threading
import webbrowser
import http.server
import socketserver
import urllib.parse
import datetime

import requests

# ============================================================
# DOOM AI — SPACE INTELLIGENCE
# Install: pip install requests skyfield
# Run: python space.py
# ============================================================

KEY = os.getenv("MODEL_API_KEY", "").strip()
BASE = os.getenv("MODEL_API_BASE", "https://api.meta.ai/v1").rstrip("/")
MODEL = os.getenv("MODEL_NAME", "muse-spark-1.3")
NASA_KEY = os.getenv("NASA_API_KEY", "DEMO_KEY")

CACHE = {}
SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "DOOM-AI-Educational-Hackathon/1.0"
})


def cached(name, seconds, function):
    now = time.time()
    old = CACHE.get(name)

    if old and now - old[0] < seconds:
        return old[1]

    result = function()
    CACHE[name] = (now, result)
    return result


def get_json(url, timeout=14):
    response = SESSION.get(url, timeout=timeout)
    response.raise_for_status()
    return response.json()


# ============================================================
# ISS TRACKING
# ============================================================

def iss():
    def load():
        errors = []

        try:
            data = get_json(
                "https://api.wheretheiss.at/v1/satellites/25544",
                12
            )

            return {
                "lat": data["latitude"],
                "lng": data["longitude"],
                "alt": data.get("altitude"),
                "speed": data.get("velocity"),
                "source": "Where the ISS At",
            }

        except Exception as error:
            errors.append(str(error))

        try:
            data = get_json(
                "http://api.open-notify.org/iss-now.json",
                10
            )

            position = data["iss_position"]

            return {
                "lat": float(position["latitude"]),
                "lng": float(position["longitude"]),
                "alt": None,
                "speed": None,
                "source": "Open Notify",
            }

        except Exception as error:
            errors.append(str(error))

        raise RuntimeError(
            "ISS data unavailable: " + " | ".join(errors)[:300]
        )

    return cached("iss", 8, load)


# ============================================================
# SATELLITE TRACKING
# ============================================================

GROUPS = {
    "starlink": "starlink",
    "stations": "stations",
    "active": "active",
    "gps": "gps-ops",
    "weather": "weather",
    "science": "science",
    "visual": "visual",
}


def satellites(group):
    group = GROUPS.get(group, "starlink")

    def load():
        from skyfield.api import EarthSatellite
        from skyfield.api import load as skyfield_load
        from skyfield.api import wgs84

        urls = [
            (
                "https://celestrak.org/NORAD/elements/gp.php"
                f"?GROUP={group}&FORMAT=tle"
            ),
            (
                "https://celestrak.com/NORAD/elements/gp.php"
                f"?GROUP={group}&FORMAT=tle"
            ),
            f"https://celestrak.org/NORAD/elements/{group}.txt",
        ]

        raw = None
        errors = []

        for url in urls:
            try:
                response = SESSION.get(url, timeout=14)
                response.raise_for_status()

                text = response.text

                if "1 " not in text or "2 " not in text:
                    raise ValueError("No TLE records found")

                raw = text
                break

            except Exception as error:
                errors.append(str(error)[:100])

        if raw is None:
            return {
                "items": [],
                "warning": (
                    "CelesTrak catalog unavailable. "
                    + " | ".join(errors)[:220]
                ),
            }

        lines = [
            line.strip()
            for line in raw.splitlines()
            if line.strip()
        ]

        timescale = skyfield_load.timescale()
        current_time = timescale.now()

        items = []
        index = 0

        while index < len(lines) - 2 and len(items) < 320:
            if (
                lines[index + 1].startswith("1 ")
                and lines[index + 2].startswith("2 ")
            ):
                try:
                    satellite = EarthSatellite(
                        lines[index + 1],
                        lines[index + 2],
                        lines[index],
                        timescale,
                    )

                    position = wgs84.subpoint(
                        satellite.at(current_time)
                    )

                    items.append({
                        "name": lines[index],
                        "lat": round(
                            position.latitude.degrees, 3
                        ),
                        "lng": round(
                            position.longitude.degrees, 3
                        ),
                        "alt": round(
                            position.elevation.km, 1
                        ),
                    })

                except Exception:
                    pass

                index += 3

            else:
                index += 1

        return {
            "items": items,
            "warning": (
                None if items else "No usable satellite records."
            ),
            "note": (
                "Positions calculated from published orbital "
                "elements, not live satellite telemetry."
            ),
        }

    return cached("sat-" + group, 1200, load)


# ============================================================
# ROCKET LAUNCHES
# ============================================================

def launches():
    def load():
        urls = [
            (
                "https://ll.thespacedevs.com/"
                "2.3.0/launches/upcoming/?limit=20"
            ),
            (
                "https://ll.thespacedevs.com/"
                "2.2.0/launch/upcoming/?limit=20"
            ),
        ]

        errors = []

        for url in urls:
            try:
                data = get_json(url, 16)
                results = data.get("results", [])

                items = []
                now = datetime.datetime.now(
                    datetime.timezone.utc
                )

                for launch in results:
                    pad = launch.get("pad") or {}
                    location = pad.get("location") or {}

                    latitude = (
                        pad.get("latitude")
                        or location.get("latitude")
                    )

                    longitude = (
                        pad.get("longitude")
                        or location.get("longitude")
                    )

                    try:
                        latitude = float(latitude)
                        longitude = float(longitude)
                    except (ValueError, TypeError):
                        continue

                    launch_date = (
                        launch.get("net")
                        or launch.get("window_start")
                        or ""
                    )

                    try:
                        date_object = (
                            datetime.datetime.fromisoformat(
                                launch_date.replace("Z", "+00:00")
                            )
                        )

                        if date_object.tzinfo is None:
                            date_object = date_object.replace(
                                tzinfo=datetime.timezone.utc
                            )

                        if date_object < (
                            now - datetime.timedelta(hours=3)
                        ):
                            continue

                    except ValueError:
                        pass

                    items.append({
                        "name": launch.get("name", "Launch"),
                        "date": launch_date,
                        "lat": latitude,
                        "lng": longitude,
                        "site": (
                            pad.get("name")
                            or location.get("name")
                            or "Launch site"
                        ),
                        "status": (
                            (launch.get("status") or {})
                            .get("name", "Scheduled")
                        ),
                    })

                return {
                    "items": items,
                    "warning": (
                        None if items
                        else "No mapped upcoming launches found."
                    ),
                }

            except Exception as error:
                errors.append(str(error)[:120])

        return {
            "items": [],
            "warning": (
                "Launch schedule unavailable: "
                + " | ".join(errors)
            ),
        }

    return cached("launches", 1800, load)


# ============================================================
# NASA IMAGE GALLERY
# ============================================================

def gallery(query):
    query = (query or "nebula").strip()[:80]

    url = (
        "https://images-api.nasa.gov/search?"
        + urllib.parse.urlencode({
            "q": query,
            "media_type": "image",
            "page_size": 16,
        })
    )

    data = get_json(url)

    items = []

    for entry in (
        data.get("collection", {}).get("items", [])
    ):
        information = (
            entry.get("data") or [{}]
        )[0]

        links = entry.get("links") or []

        image_url = next(
            (
                link.get("href")
                for link in links
                if link.get("render") == "image"
            ),
            None,
        )

        if image_url:
            items.append({
                "title": information.get(
                    "title", "NASA Image"
                ),
                "description": (
                    information.get("description") or ""
                )[:350],
                "image": image_url,
            })

    return {"items": items}


# ============================================================
# NASA ASTRONOMY PICTURE OF THE DAY
# ============================================================

def apod():
    def load():
        official_page = (
            "https://apod.nasa.gov/apod/astropix.html"
        )

        try:
            url = (
                "https://api.nasa.gov/planetary/apod?"
                + urllib.parse.urlencode({
                    "api_key": NASA_KEY,
                    "thumbs": "true",
                })
            )

            data = get_json(url, 12)

            image_url = (
                data.get("url")
                if data.get("media_type") == "image"
                else data.get("thumbnail_url")
            )

            return {
                "title": data.get(
                    "title",
                    "NASA Astronomy Picture of the Day",
                ),
                "description": data.get(
                    "explanation", ""
                ),
                "image": image_url,
                "page": official_page,
                "fallback": False,
            }

        except Exception:
            return {
                "title": "NASA Astronomy Picture of the Day",
                "description": (
                    "NASA's APOD API is temporarily unavailable. "
                    "Open the official APOD website instead."
                ),
                "image": None,
                "page": official_page,
                "fallback": True,
            }

    return cached("apod", 600, load)


# ============================================================
# META MODEL API
# ============================================================

def ask_model(question):
    if not KEY or KEY in (
        "YOUR_META_API_KEY",
        "PASTE_YOUR_REAL_META_API_KEY_HERE",
    ):
        return {
            "error": (
                "MODEL_API_KEY is missing. "
                "Set the key in PowerShell and restart space.py."
            )
        }

    url = BASE + "/chat/completions"

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are DOOM AI Space Intelligence, "
                    "a clear and scientifically accurate "
                    "astronomy tutor. Answer concisely."
                ),
            },
            {
                "role": "user",
                "content": question[:2000],
            },
        ],
        "max_tokens": 500,
    }

    try:
        response = SESSION.post(
            url,
            headers={
                "Authorization": "Bearer " + KEY,
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=28,
        )

        if not response.ok:
            return {
                "error": (
                    f"Model API HTTP {response.status_code}: "
                    f"{response.text[:350]}. "
                    "Check your API provider, endpoint and model."
                )
            }

        data = response.json()

        choices = data.get("choices") or [{}]

        message = (
            choices[0].get("message") or {}
        ).get("content", "")

        if isinstance(message, list):
            message = " ".join(
                part.get("text", "")
                for part in message
                if isinstance(part, dict)
            )

        answer = str(message).strip()

        return {
            "answer": (
                answer
                or "The model returned an empty response."
            )
        }

    except Exception as error:
        return {
            "error": (
                "Model API connection failed: "
                + str(error)[:300]
            )
        }


# ============================================================
# WEBSITE
# ============================================================

HTML = r"""
<!DOCTYPE html>
<html lang="en">

<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">

<title>DOOM AI — Space Intelligence</title>

<style>
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    background: #06101f;
    color: #dceeff;
    font-family: Segoe UI, Arial, sans-serif;
    font-size: 16px;
}

header {
    padding: 25px;
    background: linear-gradient(130deg, #0c1d34, #091626);
}

h1 {
    color: #38bdf8;
    font-size: 35px;
}

header p {
    color: #9dccf4;
}

nav {
    display: flex;
    flex-wrap: wrap;
    gap: 9px;
    padding: 12px;
    background: #0b1d32;
    position: sticky;
    top: 0;
    z-index: 10;
}

button, .linkbtn {
    background: #38bdf8;
    color: #061525;
    border: none;
    padding: 13px 16px;
    border-radius: 8px;
    font-weight: bold;
    cursor: pointer;
    text-decoration: none;
    display: inline-block;
}

button:disabled {
    opacity: 0.6;
    cursor: wait;
}

nav button {
    background: #213e5b;
    color: white;
}

nav button.active {
    background: #38bdf8;
    color: #061525;
}

main {
    padding: 16px;
}

.panel {
    background: #11263d;
    border: 1px solid #294e6b;
    border-radius: 15px;
    padding: 18px;
    min-width: 0;
}

h2, h3 {
    color: #38bdf8;
}

.grid3 {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 14px;
}

.grid2 {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 14px;
}

.globe {
    height: 390px;
    background: #020916;
    border-radius: 10px;
    overflow: hidden;
    position: relative;
    margin-top: 12px;
}

.status {
    color: #8be8ff;
    min-height: 28px;
    margin-bottom: 10px;
}

.details {
    background: #09203a;
    border-radius: 8px;
    padding: 12px;
    margin-top: 12px;
    min-height: 52px;
    white-space: pre-wrap;
    overflow-wrap: anywhere;
}

.small {
    font-size: 13px;
    color: #acc7df;
}

.hidden {
    display: none !important;
}

input, select, textarea {
    background: #eaf5ff;
    color: #0a1724;
    border: none;
    border-radius: 7px;
    padding: 12px;
    max-width: 100%;
}

textarea {
    width: 100%;
    height: 130px;
    resize: vertical;
}

.cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
    gap: 12px;
}

.gallerycard {
    background: #0b1d32;
    padding: 12px;
    border-radius: 10px;
}

.photo {
    width: 100%;
    height: 170px;
    object-fit: cover;
    border-radius: 8px;
}

.issmarker {
    width: 48px;
    height: 42px;
    cursor: pointer;
    filter: drop-shadow(0 0 7px #facc15);
}

.issmarker svg {
    width: 48px;
    height: 42px;
}

.fallback {
    position: absolute;
    inset: 0;
    display: grid;
    place-items: center;
    padding: 20px;
    text-align: center;
    background: radial-gradient(circle, #124a82, #020916 65%);
}

a {
    color: #75d6ff;
}

footer {
    padding: 25px;
    color: #a2c3df;
    font-size: 13px;
}

@media (max-width: 1000px) {
    .grid3, .grid2 {
        grid-template-columns: 1fr;
    }

    .globe {
        height: 340px;
    }
}
</style>
</head>

<body>

<header>
    <h1>DOOM AI — SPACE INTELLIGENCE</h1>
    <p>
        ISS · Satellites · Rocket Launches ·
        NASA Discoveries · Astronomy AI
    </p>
</header>

<nav>
    <button class="active" onclick="tab('globes',this)">
        🌍 THREE GLOBES
    </button>

    <button onclick="tab('launches',this)">
        🚀 LAUNCHES
    </button>

    <button onclick="tab('gallery',this)">
        🌌 NASA GALLERY
    </button>

    <button onclick="tab('apod',this)">
        ✨ PICTURE OF THE DAY
    </button>

    <button onclick="tab('video',this)">
        📺 SPACE STREAMING
    </button>

    <button onclick="tab('muse',this)">
        🤖 MUSE AI
    </button>
</nav>

<main>

<div id="status" class="status">
    Loading ISS position...
</div>

<section id="globes">

<div class="grid3">

    <div class="panel">
        <h2>🌍 1. ISS Position Tracker</h2>

        <button onclick="findISS()">FIND ISS</button>
        <button onclick="loadISS()">REFRESH POSITION</button>

        <div id="g1" class="globe"></div>

        <div id="issstats" class="details">
            Loading ISS data...
        </div>

        <p class="small">
            The ISS-shaped icon marks its reported ground
            position. Icon size is illustrative.
        </p>
    </div>

    <div class="panel">
        <h2>🛰️ 2. Satellite Network</h2>

        <select id="group">
            <option value="starlink">Starlink</option>
            <option value="stations">Space Stations</option>
            <option value="active">Active Satellites</option>
            <option value="gps">GPS</option>
            <option value="weather">Weather</option>
            <option value="science">Science</option>
            <option value="visual">Bright Satellites</option>
        </select>

        <button onclick="loadSat()">LOAD SATELLITES</button>

        <div id="g2" class="globe"></div>

        <div id="satstatus" class="details">
            Select a group and load satellites.
        </div>
    </div>

    <div class="panel">
        <h2>🚀 3. Rocket Launch Explorer</h2>

        <button onclick="loadLaunch()">
            LOAD LAUNCH SITES
        </button>

        <div id="g3" class="globe"></div>

        <div id="launchstatus" class="details">
            Scheduled launch sites, not live rocket positions.
        </div>
    </div>

</div>
</section>

<section id="launches" class="hidden">
    <div class="panel">
        <h2>Upcoming Rocket Launches</h2>

        <button onclick="loadLaunch()">
            REFRESH SCHEDULE
        </button>

        <div id="launchlist" class="cards"
             style="margin-top:15px"></div>
    </div>
</section>

<section id="gallery" class="hidden">
    <div class="panel">
        <h2>NASA Image Library</h2>

        <input id="search" value="nebula">

        <button onclick="loadGallery()">
            SEARCH NASA
        </button>

        <div id="gallerylist" class="cards"
             style="margin-top:16px"></div>
    </div>
</section>

<section id="apod" class="hidden">
    <div class="panel">
        <h2>NASA Astronomy Picture of the Day</h2>

        <button onclick="loadApod()">
            LOAD TODAY'S PICTURE
        </button>

        <div id="apodcontent" class="details">
            Click the button to load today's NASA picture.
        </div>
    </div>
</section>

<section id="video" class="hidden">
    <div class="panel">
        <h2>Official NASA Space Video</h2>

        <p>
            NASA live broadcasts depend on current availability.
            Open the official source to watch.
        </p>

        <a class="linkbtn"
           href="https://www.nasa.gov/live/"
           target="_blank"
           rel="noopener noreferrer">
            OPEN NASA LIVE
        </a>

        <a class="linkbtn"
           href="https://www.youtube.com/@NASA/live"
           target="_blank"
           rel="noopener noreferrer">
            NASA YOUTUBE LIVE
        </a>
    </div>
</section>

<section id="muse" class="hidden">
    <div class="grid2">

        <div class="panel">
            <h2>Ask DOOM Space AI — Meta Model API</h2>

            <p>
                Ask about the ISS, planets,
                rockets, and astronomy.
            </p>

            <textarea id="question"
                placeholder="Why does the ISS stay in orbit?">
            </textarea>

            <p>
                <button id="askbtn" onclick="askAI()">
                    ASK SPACE AI
                </button>
            </p>
        </div>

        <div class="panel">
            <h2>AI Response</h2>

            <div id="answer"
                 style="white-space:pre-wrap;overflow-wrap:anywhere">
            </div>
        </div>

    </div>
</section>

</main>

<footer>
    Independent educational hackathon prototype.
    Sources: Where the ISS At, Open Notify, CelesTrak,
    Skyfield, TheSpaceDevs and NASA.
    Satellite positions are orbital estimates,
    not live satellite telemetry.
</footer>

<script>

let globes = [];
let lastISS = null;

const $ = id => document.getElementById(id);

function safe(value) {
    return String(value ?? "").replace(
        /[&<>"']/g,
        character => ({
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#39;"
        }[character])
    );
}

function status(message) {
    $("status").textContent = message;
}

async function api(path, options) {
    const response = await fetch(path, options);

    let data;

    try {
        data = await response.json();
    } catch {
        throw Error("Server returned invalid JSON.");
    }

    if (!response.ok || data.error) {
        throw Error(data.error || "HTTP " + response.status);
    }

    return data;
}

function tab(id, button) {
    document.querySelectorAll("main section").forEach(
        section => section.classList.add("hidden")
    );

    $(id).classList.remove("hidden");

    document.querySelectorAll("nav button").forEach(
        item => item.classList.remove("active")
    );

    button.classList.add("active");

    if (id === "globes") {
        setTimeout(() => {
            globes.forEach(globe => {
                if (globe) {
                    globe.width(globe._dom.clientWidth);
                }
            });
        }, 80);
    }
}

function loadScript(url) {
    return new Promise((resolve, reject) => {
        const script = document.createElement("script");

        script.src = url;
        script.onload = resolve;
        script.onerror = reject;

        document.head.appendChild(script);
    });
}

function fallback(id) {
    $(id).innerHTML = `
        <div class="fallback">
            3D globe library unavailable.
            Check internet access and refresh.
        </div>
    `;
}

async function initGlobes() {
    const urls = [
        "https://cdn.jsdelivr.net/npm/globe.gl@2.33.0/dist/globe.gl.min.js",
        "https://unpkg.com/globe.gl@2.33.0/dist/globe.gl.min.js"
    ];

    for (const url of urls) {
        try {
            await loadScript(url);

            if (window.Globe) {
                break;
            }
        } catch (error) {
            console.warn(error);
        }
    }

    if (!window.Globe) {
        ["g1", "g2", "g3"].forEach(fallback);
        return;
    }

    for (let index = 1; index <= 3; index++) {
        const element = $("g" + index);

        try {
            const globe = Globe()(element)
                .globeImageUrl(
                    "https://unpkg.com/three-globe/example/img/earth-blue-marble.jpg"
                )
                .backgroundColor("#020916")
                .showAtmosphere(true)
                .atmosphereColor("#38bdf8")
                .atmosphereAltitude(0.13)
                .pointAltitude(0.025)
                .pointRadius(0.22)
                .pointColor(
                    item => item.color || "#38bdf8"
                )
                .pointLabel(
                    item => safe(item.name || "Marker")
                );

            globe.width(element.clientWidth);
            globe.height(element.clientHeight);

            globe.controls().autoRotate = true;
            globe.controls().autoRotateSpeed = 0.35;

            globe._dom = element;

            globes.push(globe);

        } catch (error) {
            console.error(error);

            globes.push(null);
            fallback("g" + index);
        }
    }

    if (lastISS) {
        drawISS();
    }

    window.addEventListener("resize", () => {
        globes.forEach(globe => {
            if (globe) {
                globe.width(globe._dom.clientWidth);
            }
        });
    });
}


// ============================================================
// ACTUAL ISS-SHAPED ICON — NOT A YELLOW DOT
// ============================================================

const issSVG = `
<svg viewBox="0 0 120 90"
     xmlns="http://www.w3.org/2000/svg">

    <g fill="#3bb6ff"
       stroke="#d9f7ff"
       stroke-width="2">

        <rect x="2" y="28"
              width="42" height="34" rx="2"/>

        <rect x="76" y="28"
              width="42" height="34" rx="2"/>
    </g>

    <g stroke="#173b62" stroke-width="2">
        <path d="M16 28v34 M30 28v34
                 M90 28v34 M104 28v34
                 M2 45h42 M76 45h42"/>
    </g>

    <g fill="#f8fafc"
       stroke="#facc15"
       stroke-width="2">

        <rect x="50" y="24"
              width="20" height="42" rx="5"/>

        <path d="M44 40h32v10H44z"/>
    </g>

    <path d="M60 14v62"
          stroke="#e2e8f0"
          stroke-width="3"/>

    <circle cx="60" cy="14"
            r="4" fill="#facc15"/>
</svg>
`;

function drawISS() {
    if (!globes[0] || !lastISS) {
        return;
    }

    const data = lastISS;

    globes[0]
        .pointsData([])
        .htmlElementsData([data])
        .htmlLat(item => item.lat)
        .htmlLng(item => item.lng)
        .htmlAltitude(0.035)
        .htmlElement(item => {
            const element = document.createElement("div");

            element.className = "issmarker";
            element.innerHTML = issSVG;
            element.title = "International Space Station";

            element.onclick = () => {
                alert(
                    "ISS reported position:\n" +
                    item.lat.toFixed(3) + "° latitude\n" +
                    item.lng.toFixed(3) + "° longitude"
                );
            };

            return element;
        });
}

async function loadISS() {
    try {
        const data = await api("/api/iss");

        lastISS = data;

        const lines = [
            "Latitude: " + Number(data.lat).toFixed(3) + "°",
            "Longitude: " + Number(data.lng).toFixed(3) + "°"
        ];

        if (data.alt != null) {
            lines.push(
                "Altitude: " +
                Number(data.alt).toFixed(1) +
                " km"
            );
        }

        if (data.speed != null) {
            lines.push(
                "Speed: " +
                Number(data.speed).toFixed(0) +
                " km/h"
            );
        }

        lines.push("Source: " + data.source);

        $("issstats").textContent = lines.join("\n");

        status("ISS position updated.");

        drawISS();

    } catch (error) {
        status("ISS position unavailable.");

        $("issstats").textContent = error.message;
    }
}

function findISS() {
    if (!lastISS || !globes[0]) {
        return;
    }

    globes[0].pointOfView({
        lat: lastISS.lat,
        lng: lastISS.lng,
        altitude: 1.9
    }, 1100);
}


// ============================================================
// SATELLITES
// ============================================================

async function loadSat() {
    const group = $("group").value;

    $("satstatus").textContent =
        "Loading public satellite records...";

    try {
        const data = await api(
            "/api/sat?group=" + encodeURIComponent(group)
        );

        if (globes[1]) {
            globes[1].pointsData(
                data.items.map(item => ({
                    ...item,
                    color: "#22d3ee"
                }))
            );

            globes[1].onPointClick(item => {
                $("satstatus").textContent =
                    item.name +
                    "\nAltitude: " + item.alt + " km" +
                    "\nLatitude: " + item.lat + "°" +
                    "\nLongitude: " + item.lng + "°" +
                    "\nEstimated from orbital elements.";
            });
        }

        $("satstatus").textContent =
            data.items.length +
            " satellite positions calculated.\n" +
            (data.warning || data.note || "");

    } catch (error) {
        $("satstatus").textContent =
            "Satellite data unavailable: " + error.message;
    }
}


// ============================================================
// ROCKET LAUNCHES
// ============================================================

async function loadLaunch() {
    $("launchstatus").textContent =
        "Loading rocket launch schedule...";

    try {
        const data = await api("/api/launch");

        if (globes[2]) {
            globes[2].pointsData(
                data.items.map(item => ({
                    ...item,
                    color: "#f472b6"
                }))
            );

            globes[2].onPointClick(item => {
                $("launchstatus").textContent =
                    item.name + "\n" +
                    item.site + "\n" +
                    item.date;
            });
        }

        $("launchstatus").textContent =
            data.items.length +
            " upcoming launches with mapped sites.\n" +
            (data.warning || "");

        $("launchlist").innerHTML =
            data.items.map(item => `
                <div class="gallerycard">
                    <h3>${safe(item.name)}</h3>
                    <p>${safe(item.date)}</p>
                    <p>${safe(item.site)}</p>
                    <p class="small">${safe(item.status)}</p>
                </div>
            `).join("") ||
            "<p>No mapped launches available.</p>";

    } catch (error) {
        $("launchstatus").textContent = error.message;
        $("launchlist").textContent = error.message;
    }
}


// ============================================================
// NASA GALLERY
// ============================================================

async function loadGallery() {
    $("gallerylist").textContent =
        "Loading NASA images...";

    try {
        const query = $("search").value;

        const data = await api(
            "/api/gallery?q=" + encodeURIComponent(query)
        );

        $("gallerylist").innerHTML =
            data.items.map(item => `
                <article class="gallerycard">
                    <img class="photo"
                         loading="lazy"
                         src="${safe(item.image)}"
                         alt="${safe(item.title)}">

                    <h3>${safe(item.title)}</h3>

                    <p class="small">
                        ${safe(item.description.slice(0, 170))}
                    </p>
                </article>
            `).join("") || "No images found.";

    } catch (error) {
        $("gallerylist").textContent =
            "NASA Gallery unavailable: " + error.message;
    }
}


// ============================================================
// NASA APOD
// ============================================================

async function loadApod() {
    $("apodcontent").textContent =
        "Loading NASA picture...";

    try {
        const data = await api("/api/apod");

        $("apodcontent").innerHTML = `
            <h3>${safe(data.title)}</h3>

            ${
                data.image
                    ? `<img src="${safe(data.image)}"
                            alt="NASA astronomy image"
                            style="max-width:100%;
                                   max-height:520px;
                                   border-radius:10px">`
                    : ""
            }

            <p>${safe(data.description)}</p>

            <p>
                <a href="${safe(data.page)}"
                   target="_blank"
                   rel="noopener noreferrer">
                    OPEN OFFICIAL NASA APOD PAGE
                </a>
            </p>

            ${
                data.fallback
                    ? '<p class="small">Official NASA fallback link.</p>'
                    : ""
            }
        `;

    } catch (error) {
        $("apodcontent").textContent = error.message;
    }
}


// ============================================================
// MUSE / META MODEL API
// ============================================================

async function askAI() {
    const question = $("question").value.trim();

    if (!question) {
        $("answer").textContent =
            "Please enter a question.";
        return;
    }

    const button = $("askbtn");

    button.disabled = true;

    $("answer").textContent =
        "Contacting model API. Please wait up to 30 seconds...";

    try {
        const data = await api("/api/ai", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                question: question
            })
        });

        $("answer").textContent =
            data.answer || "No response returned.";

    } catch (error) {
        $("answer").textContent =
            "AI connection error:\n" + error.message;

    } finally {
        button.disabled = false;
    }
}


// ============================================================
// START WEBSITE
// ============================================================

initGlobes();
loadISS();
loadLaunch();

setInterval(loadISS, 30000);

</script>

</body>
</html>
"""


# ============================================================
# LOCAL PYTHON SERVER
# ============================================================

class Handler(http.server.BaseHTTPRequestHandler):

    def log_message(self, format_string, *args):
        print("[HTTP]", format_string % args)

    def reply(self, data, code=200):
        body = json.dumps(
            data,
            ensure_ascii=False
        ).encode("utf-8")

        self.send_response(code)

        self.send_header(
            "Content-Type",
            "application/json; charset=utf-8"
        )

        self.send_header(
            "Cache-Control",
            "no-store"
        )

        self.send_header(
            "Content-Length",
            str(len(body))
        )

        self.end_headers()

        self.wfile.write(body)

    def do_GET(self):
        path = urllib.parse.urlsplit(self.path)

        if path.path == "/":
            body = HTML.encode("utf-8")

            self.send_response(200)

            self.send_header(
                "Content-Type",
                "text/html; charset=utf-8"
            )

            self.send_header(
                "Content-Length",
                str(len(body))
            )

            self.end_headers()
            self.wfile.write(body)
            return

        try:
            if path.path == "/api/iss":
                result = iss()

            elif path.path == "/api/sat":
                group = urllib.parse.parse_qs(
                    path.query
                ).get("group", ["starlink"])[0]

                result = satellites(group)

            elif path.path == "/api/launch":
                result = launches()

            elif path.path == "/api/gallery":
                query = urllib.parse.parse_qs(
                    path.query
                ).get("q", ["nebula"])[0]

                result = gallery(query)

            elif path.path == "/api/apod":
                result = apod()

            else:
                self.reply(
                    {"error": "Not found"},
                    404
                )
                return

            self.reply(result)

        except Exception as error:
            print("Service error:", str(error)[:500])

            self.reply(
                {"error": str(error)[:500]},
                503
            )

    def do_POST(self):
        path = urllib.parse.urlsplit(self.path)

        if path.path != "/api/ai":
            self.reply(
                {"error": "Not found"},
                404
            )
            return

        try:
            length = int(
                self.headers.get("Content-Length", "0")
            )

            if length > 12000:
                self.reply(
                    {"error": "Question too long"},
                    413
                )
                return

            data = json.loads(
                self.rfile.read(length).decode("utf-8")
            )

            question = str(
                data.get("question", "")
            ).strip()

            if not question:
                self.reply(
                    {"error": "Please enter a question"},
                    400
                )
                return

            result = ask_model(question)

            if "error" in result:
                print(
                    "Muse error:",
                    result["error"][:450]
                )

            self.reply(
                result,
                502 if "error" in result else 200
            )

        except Exception as error:
            print(
                "AI handler error:",
                str(error)[:450]
            )

            self.reply(
                {"error": str(error)[:400]},
                500
            )


class Server(
    socketserver.ThreadingMixIn,
    http.server.HTTPServer
):
    daemon_threads = True


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":

    server = Server(
        ("127.0.0.1", 0),
        Handler
    )

    url = (
        f"http://127.0.0.1:{server.server_port}/"
    )

    print()
    print("DOOM AI SPACE INTELLIGENCE")
    print("Meta key detected:", bool(KEY))
    print("Model:", MODEL)
    print("API base:", BASE)
    print(
        "NASA:",
        "DEMO_KEY"
        if NASA_KEY == "DEMO_KEY"
        else "Custom key"
    )
    print("Open:", url)
    print("Press Ctrl+C to stop.")
    print()

    threading.Timer(
        0.8,
        lambda: webbrowser.open(url)
    ).start()

    try:
        server.serve_forever()

    except KeyboardInterrupt:
        print("\nStopping server.")

    finally:
        server.server_close()