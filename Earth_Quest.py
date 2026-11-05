
import json
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# ============================================================
# DOOM AI — MISSION 6: PLANET EXPLORER & RESCUE
# Interactive 3D Earth + Educational Environmental Missions
#
# No Python packages required.
# Internet required for Globe.gl and Earth texture.
# Locations are reference coordinates, not live monitoring.
# Transportation routes are illustrative, not live tracking.
# ============================================================

PLACES = [
    {"name": "London", "lat": 51.5074, "lng": -0.1278,
     "type": "city", "emoji": "🏙️",
     "fact": "London is the capital of the United Kingdom."},

    {"name": "New York City", "lat": 40.7128, "lng": -74.006,
     "type": "city", "emoji": "🏙️",
     "fact": "New York is a major international transportation and cultural center."},

    {"name": "Tokyo", "lat": 35.6762, "lng": 139.6503,
     "type": "city", "emoji": "🏙️",
     "fact": "Tokyo is Japan's capital and one of the world's largest urban areas."},

    {"name": "Paris", "lat": 48.8566, "lng": 2.3522,
     "type": "city", "emoji": "🏙️",
     "fact": "Paris is the capital of France."},

    {"name": "Nairobi", "lat": -1.2864, "lng": 36.8172,
     "type": "city", "emoji": "🏙️",
     "fact": "Nairobi is Kenya's capital and a regional center for conservation."},

    {"name": "Sydney", "lat": -33.8688, "lng": 151.2093,
     "type": "city", "emoji": "🏙️",
     "fact": "Sydney is a major coastal city in Australia."},

    {"name": "Mumbai", "lat": 19.076, "lng": 72.8777,
     "type": "city", "emoji": "🏙️",
     "fact": "Mumbai is a major Indian port and commercial center."},

    {"name": "Rio de Janeiro", "lat": -22.9068, "lng": -43.1729,
     "type": "city", "emoji": "🏙️",
     "fact": "Rio de Janeiro is a major Brazilian coastal city."},

    {"name": "Mount Fuji", "lat": 35.3606, "lng": 138.7274,
     "type": "volcano", "emoji": "🌋",
     "fact": "Mount Fuji is an active stratovolcano in Japan."},

    {"name": "Mount Etna", "lat": 37.751, "lng": 14.9934,
     "type": "volcano", "emoji": "🌋",
     "fact": "Mount Etna in Sicily is one of Europe's most active volcanoes."},

    {"name": "Kilauea", "lat": 19.421, "lng": -155.287,
     "type": "volcano", "emoji": "🌋",
     "fact": "Kilauea is an active volcano on Hawaii's Big Island."},

    {"name": "Mount Vesuvius", "lat": 40.821, "lng": 14.426,
     "type": "volcano", "emoji": "🌋",
     "fact": "Vesuvius is famous for its eruption in AD 79."},

    {"name": "Pacific Ocean", "lat": 5, "lng": -145,
     "type": "ocean", "emoji": "🌊",
     "fact": "The Pacific is Earth's largest and deepest ocean."},

    {"name": "Atlantic Ocean", "lat": 5, "lng": -30,
     "type": "ocean", "emoji": "🌊",
     "fact": "The Atlantic Ocean separates the Americas from Europe and Africa."},

    {"name": "Indian Ocean", "lat": -15, "lng": 80,
     "type": "ocean", "emoji": "🌊",
     "fact": "The Indian Ocean supports major marine ecosystems and trade routes."},

    {"name": "Arctic Ocean", "lat": 80, "lng": 0,
     "type": "ocean", "emoji": "🌊",
     "fact": "Arctic sea ice helps regulate Earth's climate."},

    {"name": "Amazon Rainforest", "lat": -3.4653, "lng": -62.2159,
     "type": "forest", "emoji": "🌳",
     "fact": "The Amazon is a vast tropical forest supporting extraordinary biodiversity."},

    {"name": "Congo Basin", "lat": -0.5, "lng": 22,
     "type": "forest", "emoji": "🌳",
     "fact": "The Congo Basin contains the world's second-largest tropical rainforest."},

    {"name": "Borneo Rainforest", "lat": 0.96, "lng": 114.55,
     "type": "forest", "emoji": "🌳",
     "fact": "Borneo's forests provide important habitat for orangutans."},

    {"name": "Great Barrier Reef", "lat": -18.2871, "lng": 147.6992,
     "type": "wildlife", "emoji": "🐠",
     "fact": "The Great Barrier Reef is a vast coral reef ecosystem threatened by ocean warming."},

    {"name": "Serengeti", "lat": -2.3333, "lng": 34.8333,
     "type": "wildlife", "emoji": "🦁",
     "fact": "The Serengeti supports large migrations of wildebeest and other wildlife."},

    {"name": "Galapagos Islands", "lat": -0.9538, "lng": -90.9656,
     "type": "wildlife", "emoji": "🐢",
     "fact": "The Galapagos Islands are famous for unique wildlife and evolutionary research."},

    {"name": "Antarctica", "lat": -78, "lng": 20,
     "type": "climate", "emoji": "🧊",
     "fact": "Antarctica holds most of Earth's freshwater ice."},

    {"name": "Greenland Ice Sheet", "lat": 72, "lng": -40,
     "type": "climate", "emoji": "🧊",
     "fact": "The Greenland Ice Sheet is an important part of Earth's climate system."},

    {"name": "Kennedy Space Center", "lat": 28.5729, "lng": -80.649,
     "type": "space", "emoji": "🚀",
     "fact": "Kennedy Space Center is a major NASA launch facility in Florida."}
]

MISSIONS = [
    {
        "title": "🌋 Volcano Explorer",
        "place": "Mount Fuji",
        "story": "Scientists detect changes near a volcano. A nearby community needs reliable safety information.",
        "question": "What is the safest response?",
        "choices": [
            "Ignore official warnings",
            "Follow official monitoring and evacuation guidance",
            "Travel closer to the crater"
        ],
        "correct": 1,
        "explain": "Volcano observatories monitor earthquakes, gases, and ground changes. Follow official emergency guidance."
    },
    {
        "title": "🌊 Ocean Rescue",
        "place": "Pacific Ocean",
        "story": "Plastic waste is harming marine wildlife.",
        "question": "Which action helps reduce ocean plastic pollution?",
        "choices": [
            "Reduce unnecessary plastic and dispose of waste responsibly",
            "Throw plastic into rivers",
            "Leave fishing gear in the sea"
        ],
        "correct": 0,
        "explain": "Reducing waste, improving collection, and preventing lost fishing gear help protect marine ecosystems."
    },
    {
        "title": "🌳 Forest Guardian",
        "place": "Amazon Rainforest",
        "story": "Deforestation is destroying habitat and affecting local communities.",
        "question": "What helps protect rainforest biodiversity?",
        "choices": [
            "Clear more intact forest",
            "Remove every animal",
            "Protect existing forests and restore damaged habitats"
        ],
        "correct": 2,
        "explain": "Forest protection and responsible restoration can help species, water systems, and communities."
    },
    {
        "title": "🧊 Climate Challenge",
        "place": "Greenland Ice Sheet",
        "story": "A student sees one unusually cold day and says global warming cannot be happening.",
        "question": "What is the correct scientific explanation?",
        "choices": [
            "One day's weather determines the global climate",
            "Climate is studied using long-term patterns",
            "Weather and climate are exactly the same"
        ],
        "correct": 1,
        "explain": "Weather describes short-term conditions. Climate describes patterns measured over longer periods."
    },
    {
        "title": "🐾 Wildlife Rescue",
        "place": "Serengeti",
        "story": "Animals need safe movement between seasonal habitats.",
        "question": "Which action can help protect migrating wildlife?",
        "choices": [
            "Maintain wildlife corridors and reduce habitat fragmentation",
            "Block all migration routes",
            "Remove natural water sources"
        ],
        "correct": 0,
        "explain": "Connected habitats and well-managed wildlife corridors support animal movement."
    },
    {
        "title": "🛰️ Space Explorer",
        "place": "Kennedy Space Center",
        "story": "Scientists want to monitor storms, forests, and changes in Earth's surface.",
        "question": "How can Earth-observing satellites help?",
        "choices": [
            "They prevent every natural disaster",
            "They replace all ground measurements",
            "They collect observations that support environmental research"
        ],
        "correct": 2,
        "explain": "Satellite measurements help scientists study Earth, especially when combined with ground observations."
    }
]

ROUTES = [
    {
        "name": "London → New York",
        "kind": "Illustrative air corridor",
        "color": "#4cc9ff",
        "coords": [[51.5074, -0.1278], [55, -20], [52, -40], [40.7128, -74.006]]
    },
    {
        "name": "Tokyo → Sydney",
        "kind": "Illustrative air corridor",
        "color": "#ffd166",
        "coords": [[35.6762, 139.6503], [10, 145], [-12, 148], [-33.8688, 151.2093]]
    },
    {
        "name": "Mumbai → Nairobi",
        "kind": "Illustrative shipping corridor",
        "color": "#65e5a5",
        "coords": [[19.076, 72.8777], [12, 65], [3, 53], [-1.2864, 36.8172]]
    }
]

HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>DOOM AI — Planet Explorer & Rescue</title>
<script src="https://cdn.jsdelivr.net/npm/globe.gl@2.33.0/dist/globe.gl.min.js"></script>
<style>
*{box-sizing:border-box}
body{
 margin:0;background:#061426;color:#eaf8ff;
 font-family:Segoe UI,Arial,sans-serif
}
header{
 padding:17px 24px;
 background:linear-gradient(90deg,#092943,#142b55);
 border-bottom:1px solid #2a5c79;
 display:flex;align-items:center;justify-content:space-between;
 flex-wrap:wrap;gap:10px
}
h1{margin:0;color:#54d6ff;font-size:25px}
.small{color:#a8c8dc;font-size:12px}
button,select{
 background:#173a58;color:#eefaff;border:1px solid #39718d;
 padding:10px 13px;border-radius:9px;cursor:pointer;
 font-weight:600
}
button:hover{background:#256386}
button.active{background:#18a5c9;color:#041523}
.layout{
 display:grid;grid-template-columns:minmax(0,1fr) 355px;
 min-height:calc(100vh - 78px)
}
.maparea{position:relative;min-height:650px}
#globe{height:calc(100vh - 140px);min-height:600px}
.toolbar{
 position:absolute;top:14px;left:15px;right:15px;
 display:flex;gap:7px;flex-wrap:wrap;z-index:5;
 pointer-events:none
}
.toolbar button{pointer-events:auto}
.overlay{
 position:absolute;bottom:15px;left:15px;
 background:#092139df;border:1px solid #2d6880;
 padding:12px;border-radius:12px;max-width:450px;
 font-size:13px;z-index:5
}
aside{
 background:#0d2238;border-left:1px solid #2a5269;
 padding:18px;overflow-y:auto;max-height:calc(100vh - 78px)
}
.panel{
 background:#14314a;border:1px solid #285471;
 border-radius:13px;padding:15px;margin-bottom:14px
}
h2{color:#5bd5ff;font-size:17px;margin:0 0 10px}
h3{margin:0 0 10px;font-size:16px}
p{line-height:1.5}
#missionButtons{display:grid;grid-template-columns:1fr 1fr;gap:7px}
#missionButtons button{font-size:12px;text-align:left}
.choice{
 display:block;width:100%;margin:7px 0;
 text-align:left;line-height:1.4
}
.correct{background:#17674e!important}
.wrong{background:#753447!important}
#feedback{min-height:55px;color:#b5f7d7}
#score{color:#ffd66d;font-size:20px;font-weight:bold}
.status{color:#9db8cc;font-size:12px}
@media(max-width:950px){
 .layout{grid-template-columns:1fr}
 #globe{height:560px;min-height:560px}
 .maparea{min-height:620px}
 aside{max-height:none;border-left:none}
}
</style>
</head>
<body>

<header>
 <div>
  <h1>🌍 DOOM AI — PLANET EXPLORER & RESCUE</h1>
  <div class="small">Explore Earth • Discover Science • Protect Nature</div>
 </div>
 <div class="small">MISSION 6 • INTERACTIVE EDUCATIONAL SIMULATOR</div>
</header>

<div class="layout">
 <section class="maparea">
  <div id="globe"></div>

  <div class="toolbar" id="toolbar">
   <button onclick="filterPlaces('all',this)" class="active">🌍 All</button>
   <button onclick="filterPlaces('city',this)">🏙️ Cities</button>
   <button onclick="filterPlaces('volcano',this)">🌋 Volcanoes</button>
   <button onclick="filterPlaces('ocean',this)">🌊 Oceans</button>
   <button onclick="filterPlaces('forest',this)">🌳 Forests</button>
   <button onclick="filterPlaces('wildlife',this)">🐾 Wildlife</button>
   <button onclick="filterPlaces('climate',this)">🧊 Climate</button>
   <button onclick="filterPlaces('space',this)">🚀 Space</button>
   <button onclick="toggleRoutes()" id="routeButton">✈️🚢 Show Routes</button>
  </div>

  <div class="overlay">
   🖱️ Drag to rotate • Scroll to zoom • Click markers to explore
   <div class="status" id="mapStatus">
    Geographic reference locations • Not live tracking
   </div>
  </div>
 </section>

 <aside>
  <div class="panel">
   <h2>📍 Explore This Location</h2>
   <h3 id="placeTitle">Select a location on the globe</h3>
   <p id="placeFact">
    Choose a city, volcano, ocean, forest, or wildlife habitat
    to discover why it matters.
   </p>
   <div class="status" id="coordinates"></div>
  </div>

  <div class="panel">
   <h2>🎮 Planet Rescue Academy</h2>
   <p>Make decisions to protect our planet and earn points.</p>
   <div id="score">⭐ Score: 0 / 600</div>
   <p class="status" id="progress">Choose a mission to begin.</p>
   <div id="missionButtons"></div>
  </div>

  <div class="panel">
   <h2 id="missionTitle">🌱 Your Next Adventure</h2>
   <p id="story">Select one of the six missions above.</p>
   <h3 id="question"></h3>
   <div id="choices"></div>
   <p id="feedback"></p>
   <button onclick="nextMission()" id="nextButton" style="display:none">
    Next Adventure →
   </button>
  </div>

  <div class="panel">
   <h2>🔬 Science & Data Integrity</h2>
   <p class="small">
    Real geographic reference coordinates are used for map markers.
    Environmental challenges are educational scenarios.
    Air and sea routes are illustrative examples, not actual journeys.
    This globe does not report current volcano eruptions, pollution
    measurements, or wildlife movements.
   </p>
  </div>
 </aside>
</div>

<script>
const places = __PLACES__;
const missions = __MISSIONS__;
const routes = __ROUTES__;

let globe = null;
let currentFilter = "all";
let routesVisible = false;
let currentMission = -1;
let score = 0;
let completed = new Set();
let answered = false;

const byId = id => document.getElementById(id);

function marker(place){
 const element = document.createElement("div");
 element.style.cssText = `
  cursor:pointer;display:flex;align-items:center;gap:5px;
  white-space:nowrap;filter:drop-shadow(0 2px 3px #000);
 `;
 const icon = document.createElement("span");
 icon.textContent = place.emoji;
 icon.style.cssText = `
  font-size:25px;background:#0a2748dd;
  border:1px solid #6ad9ff;border-radius:50%;
  width:39px;height:39px;display:grid;place-items:center;
 `;
 const name = document.createElement("span");
 name.textContent = place.name;
 name.style.cssText = `
  background:#061a2bdd;border:1px solid #2b6884;
  padding:5px 8px;border-radius:7px;
  font-size:12px;color:white;font-weight:700;
 `;
 element.append(icon,name);
 element.title = place.name;
 element.onclick = event => {
  event.stopPropagation();
  showPlace(place);
 };
 return element;
}

function showPlace(place){
 byId("placeTitle").textContent = place.emoji + " " + place.name;
 byId("placeFact").textContent = place.fact;
 byId("coordinates").textContent =
  "Latitude: " + place.lat.toFixed(3) +
  "°  |  Longitude: " + place.lng.toFixed(3) + "°";
 if(globe){
  globe.pointOfView({
   lat:place.lat,lng:place.lng,altitude:1.65
  },900);
 }
}

function filterPlaces(type,button){
 currentFilter = type;
 document.querySelectorAll("#toolbar button").forEach(b=>{
  if(b.id !== "routeButton") b.classList.remove("active");
 });
 if(button) button.classList.add("active");
 updateMarkers();
}

function updateMarkers(){
 if(!globe)return;
 const selected = currentFilter === "all"
  ? places : places.filter(p=>p.type===currentFilter);
 globe.htmlElementsData(selected);
 byId("mapStatus").textContent =
  selected.length + " reference locations shown • Not live tracking";
}

function toggleRoutes(){
 routesVisible = !routesVisible;
 if(globe)globe.pathsData(routesVisible?routes:[]);
 byId("routeButton").textContent =
  routesVisible ? "✈️🚢 Hide Routes" : "✈️🚢 Show Routes";
 byId("routeButton").classList.toggle("active",routesVisible);
 byId("mapStatus").textContent = routesVisible
  ? "Illustrative transport corridors — NOT live aircraft or ship tracks"
  : "Geographic reference locations • Not live tracking";
}

function initializeGlobe(){
 if(typeof Globe === "undefined"){
  byId("mapStatus").textContent =
   "3D library failed to load. Check internet access.";
  return;
 }

 globe = Globe()(byId("globe"))
  .globeImageUrl(
   "https://unpkg.com/three-globe/example/img/earth-blue-marble.jpg"
  )
  .bumpImageUrl(
   "https://unpkg.com/three-globe/example/img/earth-topology.png"
  )
  .backgroundColor("#061426")
  .htmlElementsData([])
  .htmlLat(d=>d.lat)
  .htmlLng(d=>d.lng)
  .htmlAltitude(0.025)
  .htmlElement(marker)
  .pathsData([])
  .pathPoints(d=>d.coords)
  .pathPointLat(p=>p[0])
  .pathPointLng(p=>p[1])
  .pathColor(d=>d.color)
  .pathStroke(1.5)
  .pathDashLength(0.7)
  .pathDashGap(0.2)
  .pathDashAnimateTime(3500);

 globe.pointOfView({lat:18,lng:20,altitude:2.5},0);
 globe.controls().autoRotate = true;
 globe.controls().autoRotateSpeed = 0.3;

 updateMarkers();

 const resize = ()=>{
  const box=byId("globe");
  globe.width(box.clientWidth);
  globe.height(box.clientHeight);
 };
 window.addEventListener("resize",resize);
 resize();
}

function createMissionButtons(){
 const container=byId("missionButtons");
 missions.forEach((mission,index)=>{
  const button=document.createElement("button");
  button.textContent=mission.title;
  button.id="mission-"+index;
  button.onclick=()=>startMission(index);
  container.appendChild(button);
 });
}

function startMission(index){
 currentMission=index;
 answered=false;
 const mission=missions[index];

 byId("missionTitle").textContent=mission.title;
 byId("story").textContent=mission.story;
 byId("question").textContent=mission.question;
 byId("feedback").textContent="";
 byId("nextButton").style.display="none";

 document.querySelectorAll("#missionButtons button").forEach(b=>{
  b.classList.remove("active");
 });
 byId("mission-"+index).classList.add("active");

 const container=byId("choices");
 container.innerHTML="";

 mission.choices.forEach((choice,i)=>{
  const button=document.createElement("button");
  button.className="choice";
  button.textContent=(i+1)+". "+choice;
  button.onclick=()=>answerMission(i);
  container.appendChild(button);
 });

 const place=places.find(p=>p.name===mission.place);
 if(place)showPlace(place);

 byId("progress").textContent=
  completed.size+" of "+missions.length+" missions completed";
}

function answerMission(index){
 if(answered)return;
 answered=true;

 const mission=missions[currentMission];
 const buttons=[...document.querySelectorAll("#choices button")];
 const correct=index===mission.correct;

 if(correct && !completed.has(currentMission)){
  score+=100;
 }

 completed.add(currentMission);

 buttons.forEach((button,i)=>{
  button.disabled=true;
  if(i===mission.correct)button.classList.add("correct");
  else if(i===index)button.classList.add("wrong");
 });

 byId("feedback").textContent=
  (correct?"✅ Great decision! ":"💡 Let's learn! ")+mission.explain;

 byId("score").textContent="⭐ Score: "+score+" / 600";
 byId("progress").textContent=
  completed.size+" of "+missions.length+" missions completed";

 byId("mission-"+currentMission).textContent=
  "✓ "+mission.title;

 byId("nextButton").style.display="inline-block";

 if(completed.size===missions.length){
  byId("nextButton").textContent="Replay Missions ↻";
 }else{
  byId("nextButton").textContent="Next Adventure →";
 }
}

function nextMission(){
 if(completed.size===missions.length){
  completed.clear();
  score=0;
  byId("score").textContent="⭐ Score: 0 / 600";
  missions.forEach((mission,i)=>{
   byId("mission-"+i).textContent=mission.title;
  });
  startMission(0);
  return;
 }

 for(let i=1;i<=missions.length;i++){
  const candidate=(currentMission+i)%missions.length;
  if(!completed.has(candidate)){
   startMission(candidate);
   return;
  }
 }
}

createMissionButtons();
initializeGlobe();
</script>
</body>
</html>
"""

class Handler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path not in ("/", "/index.html"):
            self.send_error(404)
            return

        page = HTML.replace(
            "__PLACES__", json.dumps(PLACES)
        ).replace(
            "__MISSIONS__", json.dumps(MISSIONS)
        ).replace(
            "__ROUTES__", json.dumps(ROUTES)
        )

        data = page.encode("utf-8")

        self.send_response(200)
        self.send_header(
            "Content-Type", "text/html; charset=utf-8"
        )
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, format, *args):
        pass


def main():
    server = ThreadingHTTPServer(
        ("127.0.0.1", 0), Handler
    )

    port = server.server_address[1]
    url = f"http://127.0.0.1:{port}/"

    print("=" * 55)
    print("DOOM AI — PLANET EXPLORER & RESCUE")
    print("Local URL:", url)
    print("Press Ctrl+C to stop the server.")
    print("=" * 55)

    threading.Timer(
        1.0,
        lambda: webbrowser.open(url)
    ).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Earth Quest...")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
