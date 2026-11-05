
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import requests
import webbrowser
import http.server
from pathlib import Path
from urllib.parse import urlencode

# DOOM AI - MISSION 2: NATURE & EARTH INTELLIGENCE
# Free sources: Open-Meteo, OpenStreetMap, NASA, USGS
# No paid API key required.

BASE = Path(__file__).resolve().parent
HTML_FILE = BASE / "doom_earth.html"

BG = "#101827"
PANEL = "#1c293b"
BLUE = "#38bdf8"

GLOBE_HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>DOOM AI - Earth Intelligence</title>
<script src="https://unpkg.com/globe.gl"></script>
<style>
*{box-sizing:border-box}
body{margin:0;background:#07111f;color:#fff;font-family:Arial}
header{background:#14243a;padding:14px;text-align:center}
h1{color:#38bdf8;margin:0;font-size:27px}
header p{margin:6px;color:#cbd5e1}
main{display:grid;grid-template-columns:minmax(0,1fr) 390px}
#earth{height:calc(100vh - 86px);min-height:450px}
aside{background:#1c293b;padding:18px;overflow-y:auto;
max-height:calc(100vh - 86px)}
h2{font-size:18px;color:#38bdf8}
button,input,select{width:100%;padding:11px;margin:5px 0;
border:0;border-radius:6px;font-size:14px}
button{background:#38bdf8;color:#07111f;font-weight:bold;cursor:pointer}
button:hover{background:#7dd3fc}
pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#101827;
padding:12px;border-radius:8px;font:13px/1.6 Arial}
.small{font-size:12px;color:#cbd5e1;line-height:1.5}
a{color:#7dd3fc}
@media(max-width:850px){
main{grid-template-columns:1fr}
#earth{height:55vh;min-height:350px}
aside{max-height:none}
}
</style>
</head>
<body>
<header>
<h1>DOOM AI - EARTH & NATURE INTELLIGENCE</h1>
<p>Explore Earth | Identify places | Weather | NASA imagery | Natural hazards</p>
</header>
<main>
<div id="earth"></div>
<aside>
<h2>Explore Worldwide</h2>
<p class="small">Rotate Earth by dragging. Zoom with the mouse wheel.
Click any land or ocean location for weather and geographic information.</p>

<input id="city" value="Luton" placeholder="Search a city">
<button id="search">SEARCH WORLDWIDE LOCATION</button>
<button id="satellite">NASA SATELLITE IMAGERY - SELECTED AREA</button>

<h2>Weather Options</h2>
<select id="weatherMode">
<option value="all">Current weather + 3-day forecast</option>
<option value="current">Current weather only</option>
<option value="forecast">3-day forecast only</option>
</select>
<button id="refresh">REFRESH SELECTED WEATHER</button>
<label><input id="alerts" type="checkbox" checked style="width:auto">
Show weather risk popup alerts</label>

<h2>Natural Hazards</h2>
<button id="earthquakes">SHOW RECENT EARTHQUAKES</button>
<button id="nasa">SHOW NASA NATURAL EVENTS</button>
<button id="fires">SHOW NASA REPORTED WILDFIRES</button>
<button id="clear">HIDE EVENT MARKERS</button>

<h2>Selected Place</h2>
<pre id="place">Click a location on Earth.</pre>

<h2>Weather Intelligence</h2>
<pre id="weather">Waiting for selection.</pre>

<h2>Event Intelligence</h2>
<pre id="events">Select an event layer above.</pre>

<p class="small">
Sources: Open-Meteo, OpenStreetMap Nominatim, NASA EONET, USGS.
Satellite observations are not continuous live video.
Event feeds can be delayed or incomplete.
Forecast risk indicators are not official emergency warnings.
</p>
<a href="https://weather.metoffice.gov.uk/warnings-and-advice/uk-warnings"
target="_blank" rel="noopener">Official UK Weather Warnings</a>
</aside>
</main>

<script>
const $ = id => document.getElementById(id);
const container = $("earth");

let selected = null;
let weatherRequest = 0;
let eventRequest = 0;
let markers = [];

if (typeof Globe === "undefined") {
  $("place").textContent =
    "Globe library failed to load. Check your internet connection.";
} else {
  initialize();
}

function initialize() {
const globe = Globe()(container)
 .globeImageUrl(
   "https://unpkg.com/three-globe/example/img/earth-blue-marble.jpg")
 .bumpImageUrl(
   "https://unpkg.com/three-globe/example/img/earth-topology.png")
 .backgroundColor("#07111f")
 .showAtmosphere(true)
 .atmosphereColor("#38bdf8");

function resize() {
 globe.width(container.clientWidth);
 globe.height(container.clientHeight);
}
window.addEventListener("resize", resize);
resize();

function weatherRisks(d, i) {
 const out = [];
 const rain = d.precipitation_sum[i] ?? 0;
 const snow = d.snowfall_sum[i] ?? 0;
 const wind = d.wind_gusts_10m_max[i] ?? 0;
 const code = d.weather_code[i];

 if (rain >= 20) out.push("HIGH rainfall indicator");
 else if (rain >= 10) out.push("Elevated rainfall indicator");

 if (snow > 0) out.push("Snow forecast");

 if (wind >= 70) out.push("HIGH wind indicator");
 else if (wind >= 45) out.push("Elevated wind indicator");

 if (code != null && code >= 95 && code <= 99)
   out.push("Thunderstorm forecast");

 return out;
}

async function identifyPlace(lat, lng, request) {
 try {
   const params = new URLSearchParams({
     lat: lat, lon: lng,
     format: "jsonv2",
     zoom: "10",
     addressdetails: "1"
   });

   const response = await fetch(
     "https://nominatim.openstreetmap.org/reverse?" + params
   );

   if (!response.ok) throw new Error("Place lookup unavailable");

   const data = await response.json();

   if (request !== weatherRequest) return;

   const a = data.address || {};
   const nearby =
     a.city || a.town || a.village ||
     a.municipality || a.county ||
     data.name || "No nearby place identified";

   $("place").textContent =
     "Nearby place: " + nearby + "\n" +
     "State/Region: " +
       (a.state || a.region || a.county || "Unavailable") + "\n" +
     "Country: " + (a.country || "Unavailable") + "\n" +
     "Latitude: " + lat.toFixed(4) + "\n" +
     "Longitude: " + lng.toFixed(4) + "\n\n" +
     "Approximate geographic identification from OpenStreetMap.";
 } catch (error) {
   if (request === weatherRequest) {
     $("place").textContent =
       "Coordinates: " + lat.toFixed(4) + ", " +
       lng.toFixed(4) +
       "\nPlace name unavailable for this location.";
   }
 }
}

async function selectLocation(lat, lng, label) {
 selected = {lat, lng, label};
 const request = ++weatherRequest;

 $("place").textContent =
   label + "\nCoordinates: " +
   lat.toFixed(4) + ", " + lng.toFixed(4) +
   "\nIdentifying nearby place...";

 $("weather").textContent = "Loading weather...";

 globe.pointOfView({lat, lng, altitude:1.4}, 900);

 identifyPlace(lat, lng, request);

 try {
   const params = new URLSearchParams({
     latitude:lat,
     longitude:lng,
     timezone:"auto",
     forecast_days:"3",
     current:[
       "temperature_2m",
       "relative_humidity_2m",
       "apparent_temperature",
       "precipitation",
       "wind_speed_10m",
       "weather_code"
     ].join(","),
     daily:[
       "temperature_2m_max",
       "temperature_2m_min",
       "precipitation_sum",
       "snowfall_sum",
       "wind_gusts_10m_max",
       "weather_code"
     ].join(",")
   });

   const response = await fetch(
     "https://api.open-meteo.com/v1/forecast?" + params
   );

   if (!response.ok) throw new Error("Weather API error");

   const data = await response.json();
   if (request !== weatherRequest) return;

   const c = data.current;
   const d = data.daily;
   const mode = $("weatherMode").value;
   const alerts = [];

   let text = "";

   if (mode !== "forecast") {
     text +=
       "LATEST AVAILABLE CONDITIONS\n\n" +
       "Local timestamp: " + c.time + "\n" +
       "Temperature: " + c.temperature_2m + " °C\n" +
       "Feels like: " + c.apparent_temperature + " °C\n" +
       "Humidity: " + c.relative_humidity_2m + "%\n" +
       "Wind speed: " + c.wind_speed_10m + " km/h\n" +
       "Precipitation: " + c.precipitation + " mm\n\n";
   }

   if (mode !== "current") {
     text += "THREE-DAY FORECAST\n";

     d.time.forEach((day, i) => {
       const risks = weatherRisks(d, i);

       text +=
         "\n" + day + "\n" +
         "High: " + d.temperature_2m_max[i] + " °C\n" +
         "Low: " + d.temperature_2m_min[i] + " °C\n" +
         "Rain: " + d.precipitation_sum[i] + " mm\n" +
         "Snow: " + d.snowfall_sum[i] + " cm\n" +
         "Max gust: " + d.wind_gusts_10m_max[i] + " km/h\n" +
         "Risk: " +
         (risks.join("; ") || "No elevated indicators") + "\n";

       risks.forEach(r => alerts.push(day + ": " + r));
     });
   }

   text +=
     "\nSource: Open-Meteo.\n" +
     "Model-based conditions, not direct ground measurements.\n" +
     "Risk indicators are not official warnings.";

   $("weather").textContent = text;

   if (alerts.length && $("alerts").checked) {
     alert(
       "DOOM AI - WEATHER RISK INDICATORS\n\n" +
       alerts.slice(0,8).join("\n") +
       "\n\nNot official emergency warnings."
     );
   }

 } catch (error) {
   if (request === weatherRequest) {
     $("weather").textContent =
       "Weather unavailable: " + error.message;
   }
 }
}

globe.onGlobeClick(({lat,lng}) => {
 selectLocation(lat,lng,"Selected Earth location");
});

$("search").onclick = async () => {
 const city = $("city").value.trim();
 if (!city) return alert("Enter a city.");

 $("place").textContent = "Searching...";

 try {
   const params = new URLSearchParams({
     name:city, count:5, language:"en", format:"json"
   });

   const response = await fetch(
     "https://geocoding-api.open-meteo.com/v1/search?" + params
   );

   if (!response.ok) throw new Error("City search failed");

   const data = await response.json();
   if (!data.results?.length)
     throw new Error("City not found");

   const p = data.results[0];

   selectLocation(
     p.latitude, p.longitude,
     [p.name,p.admin1,p.country].filter(Boolean).join(", ")
   );
 } catch (error) {
   $("place").textContent = error.message;
 }
};

$("refresh").onclick = () => {
 if (!selected) return alert("Select a location first.");
 selectLocation(selected.lat,selected.lng,selected.label);
};

$("satellite").onclick = () => {
 if (!selected) return alert("Select a location first.");

 const {lat,lng} = selected;

 const west = Math.max(-180,lng-5);
 const east = Math.min(180,lng+5);
 const south = Math.max(-90,lat-4);
 const north = Math.min(90,lat+4);

 const url =
   "https://worldview.earthdata.nasa.gov/?" +
   new URLSearchParams({
     v:[west,south,east,north].join(",")
   });

 window.open(url,"_blank","noopener");
};

function showMarkers(items,summary) {
 markers = items;

 globe
  .pointsData(items)
  .pointLat("lat")
  .pointLng("lng")
  .pointAltitude(0.02)
  .pointRadius(item => item.kind === "earthquake"
      ? Math.max(0.12,Math.abs(item.magnitude || 0)*0.04)
      : 0.23)
  .pointColor(item => item.kind === "earthquake"
      ? "#ff5555" : "#fbbf24")
  .pointLabel(item => item.title)
  .onPointClick(item => {
    $("events").textContent =
      item.title + "\n" +
      (item.date || "") + "\n" +
      (item.link || "") +
      "\n\nSource-reported event.";
    globe.pointOfView(
      {lat:item.lat,lng:item.lng,altitude:1.2},900
    );
  });

 $("events").textContent =
   summary + "\nClick a marker for event details.";
}

$("earthquakes").onclick = async () => {
 const request = ++eventRequest;
 $("events").textContent = "Loading USGS earthquakes...";

 try {
   const response = await fetch(
     "https://earthquake.usgs.gov/earthquakes/" +
     "feed/v1.0/summary/all_day.geojson"
   );
   if (!response.ok) throw new Error("USGS unavailable");

   const data = await response.json();
   if (request !== eventRequest) return;

   const items = data.features
    .filter(f => f.geometry?.coordinates?.length >= 2)
    .map(f => ({
      lat:f.geometry.coordinates[1],
      lng:f.geometry.coordinates[0],
      kind:"earthquake",
      magnitude:f.properties.mag,
      title:
        "Magnitude " + (f.properties.mag ?? "?") +
        " - " + (f.properties.place || "Unknown"),
      date:new Date(f.properties.time).toLocaleString(),
      link:f.properties.url || ""
    }));

   showMarkers(
     items,
     items.length + " USGS past-day earthquake reports.\n\n"
   );
 } catch(error) {
   if (request === eventRequest)
     $("events").textContent = error.message;
 }
};

async function loadNASA(wildfiresOnly) {
 const request = ++eventRequest;
 $("events").textContent = "Loading NASA EONET events...";

 try {
   const response = await fetch(
     "https://eonet.gsfc.nasa.gov/api/v3/" +
     "events?status=open&limit=200"
   );
   if (!response.ok) throw new Error("NASA EONET unavailable");

   const data = await response.json();
   if (request !== eventRequest) return;

   const items = [];

   for (const event of data.events || []) {
     const categories = (event.categories || [])
       .map(c => c.id);

     if (
       wildfiresOnly &&
       !categories.includes("wildfires")
     ) continue;

     const g = event.geometry?.at(-1);
     if (!g) continue;

     let coords = null;

     if (g.type === "Point")
       coords = g.coordinates;
     else if (g.type === "Polygon")
       coords = g.coordinates?.[0]?.[0];
     else if (g.type === "MultiPolygon")
       coords = g.coordinates?.[0]?.[0]?.[0];

     if (
       !coords ||
       !Number.isFinite(coords[0]) ||
       !Number.isFinite(coords[1])
     ) continue;

     items.push({
       lat:coords[1],
       lng:coords[0],
       kind:"nasa",
       title:event.title,
       date:g.date || "",
       link:event.link || ""
     });
   }

   showMarkers(
     items,
     items.length +
     (wildfiresOnly
       ? " mapped NASA-reported wildfire events."
       : " mapped NASA natural events.") +
     "\nReports are not exhaustive or necessarily live.\n\n"
   );

 } catch(error) {
   if (request === eventRequest)
     $("events").textContent = error.message;
 }
}

$("nasa").onclick = () => loadNASA(false);
$("fires").onclick = () => loadNASA(true);

$("clear").onclick = () => {
 ++eventRequest;
 markers = [];
 globe.pointsData([]);
 $("events").textContent = "Event markers hidden.";
};

selectLocation(
 51.5074,-0.1278,"London, United Kingdom"
);

}
</script>
</body>
</html>
"""


def risk_list(d, i):
    out = []
    rain = d["precipitation_sum"][i] or 0
    snow = d["snowfall_sum"][i] or 0
    gust = d["wind_gusts_10m_max"][i] or 0
    code = d["weather_code"][i]

    if rain >= 20:
        out.append("HIGH rainfall indicator")
    elif rain >= 10:
        out.append("Elevated rainfall indicator")

    if snow > 0:
        out.append("Snow forecast")

    if gust >= 70:
        out.append("HIGH wind indicator")
    elif gust >= 45:
        out.append("Elevated wind indicator")

    if code is not None and 95 <= code <= 99:
        out.append("Thunderstorm forecast")

    return out


class NatureApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DOOM AI - Mission 2")
        self.root.geometry("860x750")
        self.root.configure(bg=BG)

        self.forecast = None
        self.busy = False
        self.server = None

        tk.Label(
            root, text="DOOM AI",
            bg=BG, fg=BLUE,
            font=("Arial", 28, "bold")
        ).pack(pady=(12, 2))

        tk.Label(
            root,
            text="MISSION 2 - NATURE & EARTH INTELLIGENCE",
            bg=BG, fg="white",
            font=("Arial", 12, "bold")
        ).pack(pady=(0, 12))

        panel = tk.Frame(root, bg=PANEL, padx=14, pady=12)
        panel.pack(fill="x", padx=18)

        tk.Label(
            panel,
            text="Search worldwide weather:",
            bg=PANEL, fg="white"
        ).pack(anchor="w")

        self.city = tk.StringVar(value="Luton")

        ttk.Entry(
            panel, textvariable=self.city,
            font=("Arial", 12)
        ).pack(fill="x", pady=7)

        self.popup = tk.BooleanVar(value=True)

        ttk.Checkbutton(
            panel,
            text="Show weather risk popup alerts",
            variable=self.popup
        ).pack(anchor="w")

        self.weather_button = tk.Button(
            panel,
            text="GET WORLDWIDE WEATHER",
            command=self.start_weather,
            bg=BLUE, fg=BG,
            font=("Arial", 11, "bold"),
            pady=9
        )
        self.weather_button.pack(fill="x", pady=6)

        tk.Button(
            panel,
            text="OPEN 3D EARTH + NASA SATELLITE + WILDFIRE",
            command=self.open_globe,
            bg="#7dd3fc", fg=BG,
            font=("Arial", 11, "bold"),
            pady=11
        ).pack(fill="x", pady=5)

        self.status = tk.StringVar(value="Ready")

        tk.Label(
            root, textvariable=self.status,
            bg=BG, fg=BLUE
        ).pack(pady=8)

        self.output = tk.Text(
            root, bg="#f8fafc", fg="#111827",
            font=("Arial", 11),
            wrap="word", padx=12, pady=12
        )
        self.output.pack(
            fill="both", expand=True,
            padx=18, pady=(0, 9)
        )

        bottom = tk.Frame(root, bg=BG)
        bottom.pack(fill="x", padx=18)

        tk.Button(
            bottom,
            text="SHOW TEMPERATURE GRAPH",
            command=self.show_graph,
            bg="#334155", fg="white",
            pady=7
        ).pack(side="left")

        tk.Button(
            bottom,
            text="OFFICIAL UK WARNINGS",
            command=lambda: webbrowser.open(
                "https://weather.metoffice.gov.uk/"
                "warnings-and-advice/uk-warnings"
            ),
            bg="#334155", fg="white",
            pady=7
        ).pack(side="right")

        tk.Label(
            root,
            text=(
                "Sources: Open-Meteo, NASA, USGS, OpenStreetMap. "
                "Experimental risk indicators, not official warnings."
            ),
            bg=BG, fg="white",
            wraplength=820
        ).pack(pady=11)

    def open_globe(self):
        try:
            HTML_FILE.write_text(
                GLOBE_HTML, encoding="utf-8"
            )

            if self.server is None:
                from functools import partial

                handler = partial(
                    http.server.SimpleHTTPRequestHandler,
                    directory=str(BASE)
                )

                self.server = http.server.ThreadingHTTPServer(
                    ("127.0.0.1", 0),
                    handler
                )

                threading.Thread(
                    target=self.server.serve_forever,
                    daemon=True
                ).start()

            port = self.server.server_address[1]

            webbrowser.open(
                f"http://127.0.0.1:{port}/doom_earth.html"
            )

            self.status.set(
                "Earth Intelligence opened in browser."
            )

        except Exception as error:
            messagebox.showerror(
                "Globe Error", str(error)
            )

    def start_weather(self):
        city = self.city.get().strip()

        if len(city) < 2:
            messagebox.showwarning(
                "City Required", "Enter a city."
            )
            return

        if self.busy:
            return

        self.busy = True
        self.weather_button.config(state="disabled")
        self.status.set("Loading weather...")

        threading.Thread(
            target=self.fetch_weather,
            args=(city,),
            daemon=True
        ).start()

    def fetch_weather(self, city):
        try:
            response = requests.get(
                "https://geocoding-api.open-meteo.com/v1/search",
                params={
                    "name": city,
                    "count": 1,
                    "language": "en",
                    "format": "json"
                },
                timeout=20
            )
            response.raise_for_status()

            places = response.json().get("results") or []

            if not places:
                raise ValueError("City not found.")

            place = places[0]

            name = ", ".join(filter(None, [
                place.get("name"),
                place.get("admin1"),
                place.get("country")
            ]))

            response = requests.get(
                "https://api.open-meteo.com/v1/forecast",
                params={
                    "latitude": place["latitude"],
                    "longitude": place["longitude"],
                    "timezone": "auto",
                    "forecast_days": 3,
                    "current": (
                        "temperature_2m,"
                        "relative_humidity_2m,"
                        "apparent_temperature,"
                        "wind_speed_10m"
                    ),
                    "daily": (
                        "temperature_2m_max,"
                        "temperature_2m_min,"
                        "precipitation_sum,"
                        "snowfall_sum,"
                        "wind_gusts_10m_max,"
                        "weather_code"
                    )
                },
                timeout=25
            )
            response.raise_for_status()

            data = response.json()
            current = data["current"]
            daily = data["daily"]

            lines = [
                "DOOM AI - NATURE INTELLIGENCE",
                "Location: " + name,
                "Local timestamp: " + current["time"],
                "",
                "CURRENT WEATHER",
                f"Temperature: {current['temperature_2m']} °C",
                f"Feels like: {current['apparent_temperature']} °C",
                f"Humidity: {current['relative_humidity_2m']}%",
                f"Wind: {current['wind_speed_10m']} km/h",
                "",
                "THREE-DAY FORECAST",
                "=" * 42
            ]

            alerts = []

            for i, day in enumerate(daily["time"]):
                risks = risk_list(daily, i)

                lines.extend([
                    "",
                    day,
                    (
                        "High / Low: "
                        f"{daily['temperature_2m_max'][i]} / "
                        f"{daily['temperature_2m_min'][i]} °C"
                    ),
                    f"Rain: {daily['precipitation_sum'][i]} mm",
                    f"Snow: {daily['snowfall_sum'][i]} cm",
                    (
                        "Maximum wind gust: "
                        f"{daily['wind_gusts_10m_max'][i]} km/h"
                    ),
                    "Risk: " + (
                        "; ".join(risks) or
                        "No elevated indicators"
                    )
                ])

                for risk in risks:
                    alerts.append(day + ": " + risk)

            lines.extend([
                "",
                "Source: Open-Meteo.",
                "Risk indicators are not official warnings."
            ])

            result = "\n".join(lines)

            self.root.after(
                0,
                lambda: self.finish_weather(
                    result, name, daily, alerts
                )
            )

        except Exception as error:
            error_text = str(error)
            self.root.after(
                0,
                lambda: self.weather_error(error_text)
            )

    def finish_weather(self, result, name, daily, alerts):
        self.output.delete("1.0", tk.END)
        self.output.insert("1.0", result)

        self.forecast = (name, daily)
        self.busy = False
        self.weather_button.config(state="normal")
        self.status.set("Weather loaded: " + name)

        if alerts and self.popup.get():
            messagebox.showwarning(
                "Forecast Risk Indicators",
                "\n".join(alerts[:8]) +
                "\n\nNot official emergency warnings."
            )

    def weather_error(self, error):
        self.busy = False
        self.weather_button.config(state="normal")
        self.status.set("Weather request failed")
        messagebox.showerror("Weather Error", error)

    def show_graph(self):
        if not self.forecast:
            messagebox.showinfo(
                "Graph", "Get a forecast first."
            )
            return

        try:
            import matplotlib.pyplot as plt

            name, daily = self.forecast

            plt.figure(figsize=(8, 4))

            plt.plot(
                daily["time"],
                daily["temperature_2m_max"],
                marker="o", label="High °C"
            )

            plt.plot(
                daily["time"],
                daily["temperature_2m_min"],
                marker="o", label="Low °C"
            )

            plt.title("DOOM AI Forecast - " + name)
            plt.ylabel("Temperature °C")
            plt.grid(alpha=0.3)
            plt.legend()
            plt.tight_layout()
            plt.show()

        except ImportError:
            messagebox.showerror(
                "Package Missing",
                "Run: python -m pip install matplotlib"
            )
        except Exception as error:
            messagebox.showerror(
                "Graph Error", str(error)
            )


if __name__ == "__main__":
    root = tk.Tk()
    NatureApp(root)
    root.mainloop()
