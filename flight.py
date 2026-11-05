
import json
import math
import random
import threading
import time
import webbrowser
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

import requests


# ============================================================
# DOOM AI — FLIGHT INTELLIGENCE
# Worldwide 3D aircraft explorer and educational simulator
# ============================================================

REGIONS = {
    "world": None,
    "europe": (30, 72, -15, 45),
    "america": (15, 65, -130, -55),
    "asia": (-5, 55, 60, 145),
    "oceania": (-48, 0, 110, 180),
}

# Real airport locations used for fictional demonstration routes.
AIRPORTS = [
    ["London Heathrow", "LHR", 51.470, -0.454],
    ["New York JFK", "JFK", 40.641, -73.778],
    ["Los Angeles", "LAX", 33.942, -118.408],
    ["San Francisco", "SFO", 37.621, -122.379],
    ["Paris Charles de Gaulle", "CDG", 49.010, 2.548],
    ["Frankfurt", "FRA", 50.037, 8.562],
    ["Dubai", "DXB", 25.253, 55.366],
    ["Singapore", "SIN", 1.364, 103.992],
    ["Tokyo Haneda", "HND", 35.549, 139.779],
    ["Sydney", "SYD", -33.939, 151.175],
    ["Mumbai", "BOM", 19.090, 72.868],
    ["Delhi", "DEL", 28.556, 77.100],
    ["Toronto", "YYZ", 43.677, -79.631],
    ["Sao Paulo", "GRU", -23.435, -46.473],
    ["Johannesburg", "JNB", -26.139, 28.246],
    ["Cairo", "CAI", 30.121, 31.406],
    ["Istanbul", "IST", 41.275, 28.752],
    ["Seoul Incheon", "ICN", 37.460, 126.440],
    ["Mexico City", "MEX", 19.436, -99.072],
    ["Auckland", "AKL", -37.008, 174.792],
    ["Nairobi", "NBO", -1.319, 36.928],
    ["Doha", "DOH", 25.273, 51.608],
    ["Bangkok", "BKK", 13.690, 100.750],
    ["Chicago", "ORD", 41.974, -87.908],
]

# Reference launch sites — NOT live rocket positions.
LAUNCH_SITES = [
    {
        "name": "Kennedy Space Center",
        "country": "United States",
        "lat": 28.573,
        "lng": -80.649,
    },
    {
        "name": "Vandenberg Space Force Base",
        "country": "United States",
        "lat": 34.742,
        "lng": -120.573,
    },
    {
        "name": "Starbase",
        "country": "United States",
        "lat": 25.997,
        "lng": -97.157,
    },
    {
        "name": "Guiana Space Centre",
        "country": "French Guiana",
        "lat": 5.236,
        "lng": -52.769,
    },
    {
        "name": "Tanegashima Space Center",
        "country": "Japan",
        "lat": 30.400,
        "lng": 130.971,
    },
    {
        "name": "Satish Dhawan Space Centre",
        "country": "India",
        "lat": 13.733,
        "lng": 80.235,
    },
    {
        "name": "Jiuquan Satellite Launch Center",
        "country": "China",
        "lat": 40.960,
        "lng": 100.298,
    },
    {
        "name": "Baikonur Cosmodrome",
        "country": "Kazakhstan",
        "lat": 45.965,
        "lng": 63.305,
    },
    {
        "name": "Mahia Launch Complex",
        "country": "New Zealand",
        "lat": -39.262,
        "lng": 177.865,
    },
]

CACHE = {}
CACHE_LOCK = threading.Lock()


HTML = r"""
<!DOCTYPE html>
<html lang="en">

<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">

<title>DOOM AI — Flight Intelligence</title>

<script src="https://cdn.jsdelivr.net/npm/globe.gl@2.33.0/dist/globe.gl.min.js"></script>

<style>

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    background: #061322;
    color: #e8f6ff;
    font-family: "Segoe UI", Arial, sans-serif;
}

header {
    padding: 25px;
    background: linear-gradient(110deg, #07162b, #154667);
}

h1 {
    margin: 0;
    color: #49caff;
    font-size: 36px;
}

header p {
    color: #b8e8ff;
}

nav {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    padding: 14px;
    background: #0a1c31;
}

button, select, input {
    padding: 12px;
    border-radius: 9px;
    border: 1px solid #457394;
    font-size: 14px;
}

button {
    background: #40bff4;
    color: #031b2d;
    font-weight: bold;
    cursor: pointer;
}

button:hover {
    background: #91e4ff;
}

select, input {
    background: #e9f5ff;
    color: #082239;
}

main {
    padding: 15px;
    max-width: 1800px;
    margin: auto;
}

.toolbar {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-bottom: 12px;
}

.layout {
    display: grid;
    grid-template-columns: minmax(0, 2fr) minmax(310px, 1fr);
    gap: 14px;
}

.panel {
    background: #102a43;
    border: 1px solid #315b79;
    border-radius: 14px;
    padding: 16px;
    margin-bottom: 14px;
}

h2 {
    color: #50c9ff;
}

h3 {
    color: #86ddff;
}

.globe {
    height: 580px;
    background: #020b18;
    border-radius: 12px;
    overflow: hidden;
    position: relative;
}

.status {
    background: #09243a;
    padding: 13px;
    border-radius: 9px;
    margin: 12px 0;
    color: #bfeaff;
    line-height: 1.5;
}

.stats {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 10px;
    margin: 14px 0;
}

.stat {
    background: #103d5d;
    padding: 13px;
    border-radius: 10px;
    text-align: center;
}

.stat strong {
    display: block;
    font-size: 26px;
    color: #67d4ff;
}

.card {
    background: #0b2035;
    padding: 13px;
    border-radius: 10px;
    margin: 10px 0;
    line-height: 1.8;
}

.warning {
    background: #452b34;
    border: 1px solid #cb6b77;
}

.legend {
    display: flex;
    gap: 14px;
    flex-wrap: wrap;
    margin: 13px 0;
}

.legend span {
    font-size: 13px;
}

.dot {
    display: inline-block;
    width: 12px;
    height: 12px;
    border-radius: 50%;
    margin-right: 5px;
}

.note {
    color: #a4c7dd;
    font-size: 12px;
    line-height: 1.6;
}

a {
    color: #77d8ff;
}

.plane {
    width: 36px;
    height: 36px;
    font-size: 28px;
    display: flex;
    justify-content: center;
    align-items: center;
    cursor: pointer;
    pointer-events: auto;
    filter: drop-shadow(0 0 5px #000);
}

.plane.selected {
    font-size: 40px;
    filter: drop-shadow(0 0 9px white);
}

.rocket {
    font-size: 32px;
    cursor: pointer;
    pointer-events: auto;
    filter: drop-shadow(0 0 7px orange);
}

.tag {
    display: inline-block;
    background: #275a7a;
    padding: 5px 9px;
    border-radius: 6px;
    font-size: 12px;
}

footer {
    padding: 25px;
    color: #9dbfd4;
    font-size: 12px;
}

@media (max-width: 900px) {

    .layout {
        grid-template-columns: 1fr;
    }

    .globe {
        height: 440px;
    }

    .stats {
        grid-template-columns: repeat(2, 1fr);
    }
}

</style>
</head>

<body>

<header>
    <h1>🌍 DOOM AI — FLIGHT INTELLIGENCE</h1>
    <p>
        ✈️ Worldwide Aircraft Explorer ·
        🌈 Color-Coded Flights ·
        🧭 Trajectory Intelligence ·
        🚀 Rocket Launch Sites ·
        🚨 Emergency Awareness
    </p>
</header>

<nav>
    <button onclick="showTab('flights')">✈️ FLIGHT GLOBE</button>
    <button onclick="showTab('rockets')">🚀 ROCKET GLOBE</button>
    <button onclick="showTab('emergency')">🚨 EMERGENCY</button>
    <button onclick="showTab('research')">🛸 UAP & MILITARY</button>
</nav>

<main>

<section id="flights">

    <div class="toolbar">

        <select id="region" onchange="regionChanged()">
            <option value="world">🌐 Entire World</option>
            <option value="europe">Europe</option>
            <option value="america">North America</option>
            <option value="asia">Asia</option>
            <option value="oceania">Oceania</option>
        </select>

        <button onclick="startDemo()">
            ✨ WORLDWIDE DEMO
        </button>

        <button onclick="startLive()">
            📡 PUBLIC FLIGHT DATA
        </button>

        <button onclick="pauseFlights()">
            ⏸ PAUSE
        </button>

        <button onclick="focusSelected()">
            🎯 FIND SELECTED
        </button>

        <input
            id="search"
            placeholder="Search callsign or aircraft ID"
            oninput="drawFlights()"
        >

    </div>

    <div id="flightStatus" class="status">
        Click WORLDWIDE DEMO to explore animated fictional flights
        between real airports. Public flight observations are available
        separately when the source responds.
    </div>

    <div class="stats">

        <div class="stat">
            <strong id="count">0</strong>
            Aircraft
        </div>

        <div class="stat">
            <strong id="climbing">0</strong>
            Climbing
        </div>

        <div class="stat">
            <strong id="descending">0</strong>
            Descending
        </div>

        <div class="stat">
            <strong id="emergencyCount">0</strong>
            Squawk alerts
        </div>

    </div>

    <div class="layout">

        <div class="panel">

            <h2>🌎 1. Worldwide 3D Aircraft Globe</h2>

            <div id="flightGlobe" class="globe"></div>

            <div class="legend">

                <span>
                    <i class="dot" style="background:#49f2a0"></i>
                    Climbing
                </span>

                <span>
                    <i class="dot" style="background:#42caff"></i>
                    Level flight
                </span>

                <span>
                    <i class="dot" style="background:#ffbb52"></i>
                    Descending
                </span>

                <span>
                    <i class="dot" style="background:#ff506a"></i>
                    Emergency squawk
                </span>

                <span>
                    <i class="dot" style="background:#c5cdd8"></i>
                    Ground / unknown
                </span>

            </div>

            <p class="note">
                Click an airplane to highlight its trajectory.
                Demo routes and aircraft are fictional.
                Public flight positions are observations, not continuous telemetry.
            </p>

        </div>

        <div class="panel">

            <h2>🧭 2. Flight Route Intelligence</h2>

            <div id="details" class="card">
                Click an airplane icon to see where it is,
                which direction it is heading, and its route information.
            </div>

            <h3>🚨 Emergency Awareness</h3>

            <div id="alerts" class="card">
                No aircraft loaded.
            </div>

            <p class="note">
                This educational prototype cannot prevent collisions,
                guarantee emergency detection, or predict crashes.
            </p>

        </div>

    </div>

</section>


<section id="rockets" style="display:none">

    <div class="layout">

        <div class="panel">

            <h2>🚀 Rocket Launch-Site Globe</h2>

            <div id="rocketGlobe" class="globe"></div>

            <p class="note">
                Rocket icons show reference launch facilities.
                They do not represent live rocket positions or confirmed liftoffs.
            </p>

        </div>

        <div class="panel">

            <h2>🛰️ Launch Intelligence</h2>

            <button onclick="loadRockets()">
                REFRESH UPCOMING LAUNCHES
            </button>

            <div id="rocketStatus" class="status">
                Reference launch facilities are available without an API.
            </div>

            <div id="rocketDetails" class="card">
                Click a 🚀 icon to explore a launch site.
            </div>

            <div id="rocketList"></div>

            <p>
                <a
                    href="https://www.nasa.gov/live/"
                    target="_blank"
                    rel="noopener"
                >
                    Watch NASA's official live coverage
                </a>
            </p>

        </div>

    </div>

</section>


<section id="emergency" style="display:none">

    <div class="panel">

        <h2>🚨 Aviation Emergency Awareness</h2>

        <div class="card">
            🔴 <b>7700</b> — General emergency
        </div>

        <div class="card">
            🔴 <b>7600</b> — Radio communication failure
        </div>

        <div class="card">
            🔴 <b>7500</b> — Unlawful interference
        </div>

        <div id="emergencyList" class="status">
            Load aircraft data first.
        </div>

        <p class="note">
            An observed emergency squawk does not prove an accident.
            Missing emergency data does not prove all aircraft are safe.
            Simulated alerts are fictional.
        </p>

    </div>

</section>


<section id="research" style="display:none">

    <div class="panel">

        <h2>🛸 UAP Research & Public Military Aviation</h2>

        <div class="card">

            <h3>🛸 Unidentified Anomalous Phenomena</h3>

            <p>
                UAP reports can be studied through official sources.
                Ordinary aircraft tracking cannot reliably identify UFOs.
                No fictional UFO positions are presented as live sightings.
            </p>

            <a
                href="https://www.aaro.mil/"
                target="_blank"
                rel="noopener"
            >
                Official AARO UAP research
            </a>

        </div>

        <div class="card">

            <h3>🛩️ Military Aircraft</h3>

            <p>
                Some military aircraft may appear in public flight data.
                We do not label an aircraft a fighter jet without verified
                aircraft-type information or attempt to reveal restricted flights.
            </p>

        </div>

    </div>

</section>

</main>

<footer>
    DOOM AI — Independent educational hackathon prototype.
    Sources: OpenSky Network, TheSpaceDevs, NASA, AARO.
    Simulated flights are fictional. Do not use this app for aviation navigation,
    air traffic control, emergency response, or safety decisions.
</footer>


<script>

const AIRPORTS = __AIRPORTS__;
const SITES = __SITES__;

let flightGlobe = null;
let rocketGlobe = null;

let planes = [];
let mode = "idle";
let timer = null;
let selected = null;
let requestId = 0;
let trails = new Map();
let rocketInitialized = false;

const views = {

    world: {
        lat: 15,
        lng: 15,
        altitude: 2.6
    },

    europe: {
        lat: 50,
        lng: 15,
        altitude: 1.9
    },

    america: {
        lat: 38,
        lng: -95,
        altitude: 2.0
    },

    asia: {
        lat: 28,
        lng: 105,
        altitude: 2.0
    },

    oceania: {
        lat: -25,
        lng: 145,
        altitude: 2.0
    }
};


function $(id) {
    return document.getElementById(id);
}


function escapeHtml(value) {

    return String(value ?? "").replace(
        /[&<>"']/g,
        c => ({
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#39;"
        }[c])
    );
}


function fmt(value, decimals = 0) {

    if (
        value === null ||
        value === undefined ||
        !Number.isFinite(Number(value))
    ) {
        return "Unknown";
    }

    return Number(value).toFixed(decimals);
}


function showTab(name) {

    for (const id of [
        "flights",
        "rockets",
        "emergency",
        "research"
    ]) {

        $(id).style.display =
            id === name ? "block" : "none";
    }

    if (name === "rockets") {

        initRocketGlobe();

        setTimeout(() => {
            if (rocketGlobe) {
                rocketGlobe.width(
                    $("rocketGlobe").clientWidth
                );
            }
        }, 100);
    }

    if (name === "flights") {

        setTimeout(() => {
            if (flightGlobe) {
                flightGlobe.width(
                    $("flightGlobe").clientWidth
                );
            }
        }, 100);
    }
}


function makeGlobe(id) {

    if (typeof Globe === "undefined") {

        $(id).innerHTML =
            "<p style='padding:20px'>" +
            "3D globe library could not load. " +
            "Check your internet connection." +
            "</p>";

        return null;
    }

    const el = $(id);

    return Globe()(el)

        .globeImageUrl(
            "https://unpkg.com/three-globe/example/img/earth-blue-marble.jpg"
        )

        .backgroundColor("#020b18")

        .showAtmosphere(true)

        .atmosphereColor("#60beff")

        .atmosphereAltitude(0.15)

        .width(el.clientWidth)

        .height(580);
}


function aircraftColor(a) {

    if (["7700", "7600", "7500"].includes(a.squawk)) {
        return "#ff506a";
    }

    if (a.ground) {
        return "#c5cdd8";
    }

    if (a.vertical > 1.5) {
        return "#49f2a0";
    }

    if (a.vertical < -1.5) {
        return "#ffbb52";
    }

    return "#42caff";
}


function aircraftMarker(a) {

    const el = document.createElement("div");

    el.className =
        "plane" + (a.id === selected ? " selected" : "");

    el.textContent = "✈";

    el.style.color = aircraftColor(a);

    el.title =
        (a.callsign || a.id) +
        (a.demo ? " — SIMULATED" : " — PUBLIC DATA");

    el.onclick = () => choosePlane(a.id);

    return el;
}


function initFlightGlobe() {

    flightGlobe = makeGlobe("flightGlobe");

    if (!flightGlobe) {
        return;
    }

    flightGlobe

        .htmlElementsData([])

        .htmlLat(a => a.lat)

        .htmlLng(a => a.lng)

        .htmlAltitude(0.025)

        .htmlElement(aircraftMarker)

        .pathsData([])

        .pathPoints("coords")

        .pathPointLat(p => p.lat)

        .pathPointLng(p => p.lng)

        .pathColor(p => p.color)

        .pathStroke(p => p.selected ? 2.5 : 0.5)

        .pathDashLength(1)

        .pathDashGap(0);

    flightGlobe.pointOfView(views.world, 0);

    flightGlobe.controls().autoRotate = false;
}


// Great-circle route between two real airport coordinates.
// Used only for fictional demonstration flights.

function greatCircle(from, to, progress) {

    const rad = Math.PI / 180;
    const deg = 180 / Math.PI;

    const lat1 = from[2] * rad;
    const lon1 = from[3] * rad;

    const lat2 = to[2] * rad;
    const lon2 = to[3] * rad;

    const x1 = Math.cos(lat1) * Math.cos(lon1);
    const y1 = Math.cos(lat1) * Math.sin(lon1);
    const z1 = Math.sin(lat1);

    const x2 = Math.cos(lat2) * Math.cos(lon2);
    const y2 = Math.cos(lat2) * Math.sin(lon2);
    const z2 = Math.sin(lat2);

    const dot = Math.max(
        -1,
        Math.min(1, x1*x2 + y1*y2 + z1*z2)
    );

    const angle = Math.acos(dot);

    if (angle < 0.000001) {
        return {
            lat: from[2],
            lng: from[3]
        };
    }

    const sinAngle = Math.sin(angle);

    const a =
        Math.sin((1 - progress) * angle) / sinAngle;

    const b =
        Math.sin(progress * angle) / sinAngle;

    const x = a*x1 + b*x2;
    const y = a*y1 + b*y2;
    const z = a*z1 + b*z2;

    return {
        lat: Math.atan2(z, Math.hypot(x, y)) * deg,
        lng: Math.atan2(y, x) * deg
    };
}


function bearing(a, b) {

    const rad = Math.PI / 180;

    const lat1 = a.lat * rad;
    const lat2 = b.lat * rad;

    const deltaLon = (b.lng - a.lng) * rad;

    const y =
        Math.sin(deltaLon) * Math.cos(lat2);

    const x =
        Math.cos(lat1) * Math.sin(lat2) -
        Math.sin(lat1) *
        Math.cos(lat2) *
        Math.cos(deltaLon);

    return (
        Math.atan2(y, x) * 180 / Math.PI + 360
    ) % 360;
}


function compass(heading) {

    if (!Number.isFinite(heading)) {
        return "Unknown";
    }

    const directions = [
        "North",
        "Northeast",
        "East",
        "Southeast",
        "South",
        "Southwest",
        "West",
        "Northwest"
    ];

    return directions[
        Math.round(heading / 45) % 8
    ];
}


function routeCoordinates(a) {

    if (!a.demo || !a.from || !a.to) {
        return [];
    }

    const points = [];

    for (let i = 0; i <= 60; i++) {

        const p = greatCircle(
            a.from,
            a.to,
            i / 60
        );

        points.push(p);
    }

    return points;
}


function saveTrails() {

    for (const a of planes) {

        if (
            !Number.isFinite(a.lat) ||
            !Number.isFinite(a.lng)
        ) {
            continue;
        }

        const history = trails.get(a.id) || [];

        history.push({
            lat: a.lat,
            lng: a.lng
        });

        if (history.length > 30) {
            history.shift();
        }

        trails.set(a.id, history);
    }
}


function drawFlights() {

    $("count").textContent = planes.length;

    $("climbing").textContent =
        planes.filter(a =>
            !a.ground && a.vertical > 1.5
        ).length;

    $("descending").textContent =
        planes.filter(a =>
            !a.ground && a.vertical < -1.5
        ).length;

    const emergencyPlanes = planes.filter(a =>
        ["7700", "7600", "7500"].includes(a.squawk)
    );

    $("emergencyCount").textContent =
        emergencyPlanes.length;

    const search = $("search").value
        .trim()
        .toLowerCase();

    const visible = planes.filter(a =>
        !search ||
        String(a.callsign).toLowerCase().includes(search) ||
        String(a.id).toLowerCase().includes(search)
    );

    if (flightGlobe) {

        flightGlobe.htmlElementsData(visible);

        const paths = [];

        // Show a bright trajectory for the selected demo flight.
        if (selected) {

            const chosen = planes.find(
                a => a.id === selected
            );

            if (chosen && chosen.demo) {

                paths.push({
                    coords: routeCoordinates(chosen),
                    color: "#ffe16a",
                    selected: true
                });
            }
        }

        // Recent observed or simulated movement trails.
        for (const a of visible) {

            const history = trails.get(a.id) || [];

            if (history.length > 1) {

                paths.push({
                    coords: history,
                    color: aircraftColor(a),
                    selected: a.id === selected
                });
            }
        }

        flightGlobe.pathsData(paths);
    }

    updateAlerts();

    if (selected) {

        const a = planes.find(
            x => x.id === selected
        );

        if (a) {
            showDetails(a);
        }
    }
}


function showDetails(a) {

    const direction = compass(a.heading);

    let routeInfo = "";

    if (a.demo && a.from && a.to) {

        routeInfo = `
            <p><b>Departure:</b>
                ${escapeHtml(a.from[0])}
                (${escapeHtml(a.from[1])})
            </p>

            <p><b>Destination:</b>
                ${escapeHtml(a.to[0])}
                (${escapeHtml(a.to[1])})
            </p>

            <p><b>Next stop:</b>
                ${escapeHtml(a.to[0])}
                — simulated
            </p>

            <p><b>Route progress:</b>
                ${fmt(a.progress * 100, 1)}%
            </p>

            <p class="note">
                Departure, destination, and route progress
                are fictional demonstration information.
            </p>
        `;

    } else {

        routeInfo = `
            <p><b>Departure:</b>
                Not available from this feed
            </p>

            <p><b>Destination:</b>
                Not available from this feed
            </p>

            <p><b>Next stop:</b>
                Not available
            </p>

            <p class="note">
                Heading indicates direction of travel.
                It does not establish the destination airport.
            </p>
        `;
    }

    $("details").innerHTML = `

        <span class="tag">
            ${a.demo ? "SIMULATED AIRCRAFT" : "PUBLIC OBSERVATION"}
        </span>

        <h3>✈️ ${escapeHtml(a.callsign)}</h3>

        <p><b>Aircraft ID:</b>
            ${escapeHtml(a.id)}
        </p>

        <p><b>Country:</b>
            ${escapeHtml(a.country)}
        </p>

        ${routeInfo}

        <p><b>Travel direction:</b>
            ${escapeHtml(direction)}
        </p>

        <p><b>Heading:</b>
            ${fmt(a.heading)}°
        </p>

        <p><b>Altitude:</b>
            ${fmt(a.altitude)} meters
        </p>

        <p><b>Speed:</b>
            ${a.speed == null
                ? "Unknown"
                : fmt(a.speed * 3.6) + " km/h"}
        </p>

        <p><b>Vertical rate:</b>
            ${fmt(a.vertical, 1)} m/s
        </p>

        <p><b>Squawk:</b>
            ${escapeHtml(a.squawk || "Not reported")}
        </p>

        <p><b>Current coordinates:</b>
            ${fmt(a.lat, 3)},
            ${fmt(a.lng, 3)}
        </p>

        <p><b>Observation:</b>
            ${escapeHtml(a.observed)}
        </p>
    `;
}


function choosePlane(id) {

    selected = id;

    const a = planes.find(
        x => x.id === id
    );

    if (!a) {
        return;
    }

    drawFlights();

    focusSelected();
}


function focusSelected() {

    if (!selected || !flightGlobe) {
        return;
    }

    const a = planes.find(
        x => x.id === selected
    );

    if (!a) {
        return;
    }

    flightGlobe.pointOfView({
        lat: a.lat,
        lng: a.lng,
        altitude: 1.3
    }, 900);
}


function updateAlerts() {

    const flagged = planes.filter(a =>
        ["7700", "7600", "7500"].includes(a.squawk)
    );

    let message;

    if (!planes.length) {

        message = "No aircraft loaded.";

    } else if (!flagged.length) {

        message =
            "No emergency squawk codes observed among the " +
            planes.length +
            " displayed aircraft. This does not prove all flights are safe.";

    } else {

        message = flagged.map(a => `

            <div class="card warning">

                🚨 ${escapeHtml(a.callsign)}

                <p>
                    Squawk ${escapeHtml(a.squawk)}
                </p>

                <p>
                    ${a.demo
                        ? "SIMULATED EMERGENCY EXAMPLE"
                        : "PUBLIC OBSERVATION — VERIFY INDEPENDENTLY"}
                </p>

            </div>

        `).join("");
    }

    $("alerts").innerHTML = message;

    $("emergencyList").innerHTML = message;
}


function clearTimer() {

    if (timer) {
        clearInterval(timer);
        timer = null;
    }
}


function pauseFlights() {

    clearTimer();

    requestId++;

    mode = "paused";

    $("flightStatus").textContent =
        "⏸ Updates paused. Select DEMO or PUBLIC DATA to resume.";
}


function regionChanged() {

    const region = $("region").value;

    if (flightGlobe) {
        flightGlobe.pointOfView(
            views[region],
            900
        );
    }

    if (mode === "live") {
        startLive();
    }
}


// ------------------------------------------------------------
// WORLDWIDE FICTIONAL FLIGHT SIMULATOR
// ------------------------------------------------------------

function createDemoFlights() {

    const out = [];

    for (let i = 0; i < 110; i++) {

        const fromIndex = Math.floor(
            Math.random() * AIRPORTS.length
        );

        let toIndex = Math.floor(
            Math.random() * (AIRPORTS.length - 1)
        );

        if (toIndex >= fromIndex) {
            toIndex++;
        }

        const from = AIRPORTS[fromIndex];
        const to = AIRPORTS[toIndex];

        const progress =
            0.05 + Math.random() * 0.88;

        const position = greatCircle(
            from,
            to,
            progress
        );

        const next = greatCircle(
            from,
            to,
            Math.min(0.999, progress + 0.001)
        );

        out.push({

            id: "DEMO-" + (i + 1),

            callsign:
                ["SKY", "STAR", "JET", "AIR", "WING"][i % 5] +
                (200 + i),

            country: "Fictional demonstration",

            lat: position.lat,
            lng: position.lng,

            altitude:
                8000 + Math.random() * 4500,

            speed:
                170 + Math.random() * 120,

            heading: bearing(position, next),

            vertical:
                i % 6 === 0 ? 2.5 :
                i % 7 === 0 ? -2.8 : 0,

            ground: false,

            squawk:
                i === 0 ? "7700" : null,

            observed: "SIMULATED — not real",

            demo: true,

            from: from,
            to: to,
            progress: progress,

            // Simulation progress per animation tick.
            rate:
                0.00012 + Math.random() * 0.0002
        });
    }

    return out;
}


function moveDemo() {

    if (mode !== "demo") {
        return;
    }

    for (const a of planes) {

        a.progress += a.rate;

        if (a.progress >= 0.995) {

            const previous = a.from;

            a.from = a.to;
            a.to = previous;

            a.progress = 0.005;
        }

        const p = greatCircle(
            a.from,
            a.to,
            a.progress
        );

        const next = greatCircle(
            a.from,
            a.to,
            Math.min(0.999, a.progress + 0.001)
        );

        a.lat = p.lat;
        a.lng = p.lng;

        a.heading = bearing(p, next);

        a.altitude = Math.max(
            3000,
            a.altitude + a.vertical * 1.5
        );
    }

    saveTrails();
    drawFlights();
}


function startDemo() {

    clearTimer();

    requestId++;

    mode = "demo";

    selected = null;

    trails.clear();

    planes = createDemoFlights();

    saveTrails();
    drawFlights();

    $("flightStatus").textContent =
        "✨ WORLDWIDE DEMO — 110 FICTIONAL aircraft " +
        "flying between real airport locations. " +
        "Routes, destinations, movement, and emergency examples " +
        "are SIMULATED — NOT LIVE.";

    if (flightGlobe) {

        flightGlobe.pointOfView(
            views[$("region").value],
            900
        );
    }

    timer = setInterval(
        moveDemo,
        1500
    );
}


// ------------------------------------------------------------
// PUBLIC AIRCRAFT OBSERVATIONS
// ------------------------------------------------------------

async function startLive() {

    clearTimer();

    const currentRequest = ++requestId;

    mode = "live";

    selected = null;

    trails.clear();

    planes = [];

    drawFlights();

    const region = $("region").value;

    $("flightStatus").textContent =
        "📡 Loading public aircraft observations...";

    async function refresh() {

        try {

            const response = await fetch(
                "/api/flights?region=" +
                encodeURIComponent(region)
            );

            const data = await response.json();

            if (
                currentRequest !== requestId ||
                mode !== "live"
            ) {
                return;
            }

            if (!response.ok) {
                throw Error(
                    data.error || "Public feed unavailable"
                );
            }

            planes = data.aircraft || [];

            saveTrails();
            drawFlights();

            $("flightStatus").textContent =
                "📡 PUBLIC OBSERVATIONS | " +
                planes.length +
                " aircraft displayed | " +
                (data.updated || "Unknown update time") +
                " | Refresh about every 60 seconds. " +
                "Coverage is incomplete and may be delayed.";

        } catch (error) {

            if (
                currentRequest !== requestId ||
                mode !== "live"
            ) {
                return;
            }

            $("flightStatus").textContent =
                "⚠️ Public flight data unavailable: " +
                error.message +
                ". Try WORLDWIDE DEMO instead.";
        }
    }

    await refresh();

    if (
        currentRequest === requestId &&
        mode === "live"
    ) {

        timer = setInterval(
            refresh,
            60000
        );
    }
}


// ------------------------------------------------------------
// ROCKET LAUNCH GLOBE
// ------------------------------------------------------------

function rocketMarker(site) {

    const el = document.createElement("div");

    el.className = "rocket";

    el.textContent = "🚀";

    el.title = site.name;

    el.onclick = () => {

        $("rocketDetails").innerHTML = `

            <h3>🚀 ${escapeHtml(site.name)}</h3>

            <p>
                <b>Country:</b>
                ${escapeHtml(site.country)}
            </p>

            <p>
                <b>Coordinates:</b>
                ${fmt(site.lat, 3)},
                ${fmt(site.lng, 3)}
            </p>

            <p class="note">
                This is a reference launch facility,
                not a confirmed active launch.
            </p>
        `;

        rocketGlobe.pointOfView({
            lat: site.lat,
            lng: site.lng,
            altitude: 1.3
        }, 900);
    };

    return el;
}


function initRocketGlobe() {

    if (rocketInitialized) {
        return;
    }

    rocketInitialized = true;

    rocketGlobe = makeGlobe("rocketGlobe");

    if (!rocketGlobe) {
        return;
    }

    rocketGlobe

        .htmlElementsData(SITES)

        .htmlLat(site => site.lat)

        .htmlLng(site => site.lng)

        .htmlAltitude(0.03)

        .htmlElement(rocketMarker);

    rocketGlobe.pointOfView({
        lat: 15,
        lng: -20,
        altitude: 2.4
    }, 0);

    rocketGlobe.controls().autoRotate = false;

    $("rocketStatus").textContent =
        "🚀 " + SITES.length +
        " reference launch facilities mapped. " +
        "Checking upcoming launch schedule...";

    loadRockets();
}


async function loadRockets() {

    $("rocketStatus").textContent =
        "🚀 Reference launch sites mapped. " +
        "Checking upcoming scheduled launches...";

    try {

        const response = await fetch("/api/rockets");

        const data = await response.json();

        if (!response.ok) {
            throw Error(
                data.error || "Launch schedule unavailable"
            );
        }

        const launches = data.launches || [];

        $("rocketStatus").textContent =
            "🚀 " + SITES.length +
            " reference launch sites | " +
            launches.length +
            " upcoming scheduled launches.";

        $("rocketList").innerHTML =
            launches.map(item => `

                <div class="card">

                    <h3>🚀 ${escapeHtml(item.name)}</h3>

                    <p>
                        <b>Scheduled UTC:</b>
                        ${escapeHtml(item.date)}
                    </p>

                    <p>
                        <b>Launch pad:</b>
                        ${escapeHtml(item.pad)}
                    </p>

                    <p>
                        <b>Status:</b>
                        ${escapeHtml(item.status)}
                    </p>

                </div>

            `).join("");

    } catch (error) {

        $("rocketStatus").textContent =
            "🚀 " + SITES.length +
            " reference launch facilities are visible. " +
            "⚠️ Upcoming launch schedule unavailable: " +
            error.message;

        $("rocketList").innerHTML =
            "<p class='note'>" +
            "The reference-site globe works even when " +
            "the launch schedule API is unavailable." +
            "</p>";
    }
}


window.addEventListener("resize", () => {

    if (flightGlobe) {

        flightGlobe.width(
            $("flightGlobe").clientWidth
        );
    }

    if (
        rocketGlobe &&
        $("rockets").style.display !== "none"
    ) {

        rocketGlobe.width(
            $("rocketGlobe").clientWidth
        );
    }
});


initFlightGlobe();

</script>

</body>
</html>
"""

HTML = HTML.replace(
    "__AIRPORTS__",
    json.dumps(AIRPORTS)
).replace(
    "__SITES__",
    json.dumps(LAUNCH_SITES)
)


# ============================================================
# PYTHON BACKEND — PUBLIC DATA SOURCES
# ============================================================

def get_cached(key, seconds, loader):

    with CACHE_LOCK:

        existing = CACHE.get(key)

        if (
            existing and
            time.time() - existing["time"] < seconds
        ):
            return existing["data"]

    data = loader()

    with CACHE_LOCK:

        CACHE[key] = {
            "time": time.time(),
            "data": data
        }

    return data


def fetch_region(region):

    bounds = REGIONS[region]

    params = dict(zip(
        ("lamin", "lamax", "lomin", "lomax"),
        bounds
    ))

    response = requests.get(
        "https://opensky-network.org/api/states/all",
        params=params,
        headers={
            "User-Agent": "DOOMAI-EducationalPrototype/1.0"
        },
        timeout=16
    )

    response.raise_for_status()

    data = response.json()

    timestamp = data.get("time")

    if timestamp:

        observed = datetime.fromtimestamp(
            timestamp,
            timezone.utc
        ).strftime("%Y-%m-%d %H:%M:%S UTC")

    else:

        observed = "Unknown"

    aircraft = []

    for state in data.get("states") or []:

        if (
            len(state) < 17 or
            state[5] is None or
            state[6] is None
        ):
            continue

        aircraft.append({

            "id": state[0],

            "callsign":
                (state[1] or state[0]).strip(),

            "country": state[2],

            "lat": state[6],

            "lng": state[5],

            "altitude":
                state[13]
                if state[13] is not None
                else state[7],

            "speed": state[9],

            "heading": state[10],

            "vertical": state[11] or 0,

            "ground": bool(state[8]),

            "squawk":
                str(state[14])
                if state[14] else None,

            "observed": observed,

            "demo": False
        })

    return {
        "aircraft": aircraft[:220],
        "updated": observed
    }


def fetch_flights(region):

    if region != "world":
        return fetch_region(region)

    # Worldwide mode samples multiple regions.
    # It is NOT complete worldwide coverage.

    combined = []
    timestamps = []

    for part in (
        "europe",
        "america",
        "asia",
        "oceania"
    ):

        try:

            data = get_cached(
                "region-" + part,
                75,
                lambda p=part: fetch_region(p)
            )

            combined.extend(
                data["aircraft"][:65]
            )

            timestamps.append(
                data["updated"]
            )

        except Exception as error:

            print(
                "Region unavailable:",
                part,
                type(error).__name__
            )

    if not combined:

        raise RuntimeError(
            "Public regional flight feeds unavailable"
        )

    unique = {
        a["id"]: a
        for a in combined
    }

    return {
        "aircraft": list(unique.values())[:260],
        "updated":
            "Regional sample; timestamps may vary: " +
            ", ".join(sorted(set(timestamps)))
    }


def fetch_launches():

    endpoints = [
        "https://ll.thespacedevs.com/2.3.0/launches/upcoming/",
        "https://ll.thespacedevs.com/2.2.0/launch/upcoming/"
    ]

    for endpoint in endpoints:

        try:

            response = requests.get(
                endpoint,
                params={"limit": 12},
                headers={
                    "User-Agent":
                        "DOOMAI-EducationalPrototype/1.0"
                },
                timeout=14
            )

            response.raise_for_status()

            launches = []

            for item in (
                response.json().get("results") or []
            ):

                pad = item.get("pad") or {}

                status = item.get("status") or {}

                launches.append({

                    "name":
                        item.get("name") or "Unknown",

                    "date":
                        item.get("net") or "Unannounced",

                    "pad":
                        pad.get("name") or "Unknown",

                    "status":
                        status.get("name") or "Scheduled"
                })

            return {
                "launches": launches
            }

        except Exception as error:

            print(
                "Launch endpoint unavailable:",
                type(error).__name__
            )

    raise RuntimeError(
        "Public launch schedule endpoints unavailable"
    )


# ============================================================
# LOCAL WEB SERVER
# ============================================================

class Handler(BaseHTTPRequestHandler):

    def send_json(self, payload, status=200):

        raw = json.dumps(payload).encode("utf-8")

        self.send_response(status)

        self.send_header(
            "Content-Type",
            "application/json; charset=utf-8"
        )

        self.send_header(
            "Content-Length",
            str(len(raw))
        )

        self.send_header(
            "Cache-Control",
            "no-store"
        )

        self.end_headers()

        self.wfile.write(raw)

    def do_GET(self):

        parsed = urlparse(self.path)

        if parsed.path == "/":

            raw = HTML.encode("utf-8")

            self.send_response(200)

            self.send_header(
                "Content-Type",
                "text/html; charset=utf-8"
            )

            self.send_header(
                "Content-Length",
                str(len(raw))
            )

            self.send_header(
                "Cache-Control",
                "no-store"
            )

            self.end_headers()

            self.wfile.write(raw)

        elif parsed.path == "/favicon.ico":

            self.send_response(204)
            self.end_headers()

        elif parsed.path == "/api/flights":

            region = parse_qs(
                parsed.query
            ).get("region", ["world"])[0]

            if region not in REGIONS:

                self.send_json(
                    {"error": "Invalid region"},
                    400
                )

                return

            try:

                data = get_cached(
                    "flight-" + region,
                    60,
                    lambda: fetch_flights(region)
                )

                self.send_json(data)

            except Exception as error:

                print(
                    "Flight API error:",
                    type(error).__name__,
                    str(error)[:180]
                )

                self.send_json({
                    "error":
                        "OpenSky unavailable, rate-limited, "
                        "or network restricted"
                }, 503)

        elif parsed.path == "/api/rockets":

            try:

                data = get_cached(
                    "rockets",
                    900,
                    fetch_launches
                )

                self.send_json(data)

            except Exception as error:

                print(
                    "Rocket API error:",
                    type(error).__name__,
                    str(error)[:180]
                )

                self.send_json({
                    "error":
                        "Public launch schedule unavailable"
                }, 503)

        else:

            self.send_json(
                {"error": "Not found"},
                404
            )

    def log_message(self, fmt, *args):

        if (
            args and
            "/api/" in str(args[0])
        ):

            print(
                "[Flight API]",
                fmt % args
            )


def main():

    server = ThreadingHTTPServer(
        ("127.0.0.1", 0),
        Handler
    )

    port = server.server_address[1]

    url = f"http://127.0.0.1:{port}/"

    print("=" * 55)
    print("DOOM AI — FLIGHT INTELLIGENCE")
    print("Website:", url)
    print("Worldwide demo: 110 fictional aircraft")
    print("Public data: OpenSky, when available")
    print("Rocket sites: reference locations")
    print("Press Ctrl+C to stop.")
    print("=" * 55)

    threading.Timer(
        1.0,
        lambda: webbrowser.open(url)
    ).start()

    try:

        server.serve_forever()

    except KeyboardInterrupt:

        print("\nStopping Flight Intelligence...")

    finally:

        server.server_close()


if __name__ == "__main__":
    main()
