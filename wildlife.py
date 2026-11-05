
import json
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# DOOM AI — MISSION 7: WILDLIFE GUARDIAN
# Interactive 3D wildlife explorer and conservation simulator
# No additional Python packages required.
# Internet is required for the 3D globe library and Earth image.
#
# Animal positions are educational habitat reference points.
# They are NOT real-time wildlife tracking coordinates.

ANIMALS = [
    {
        "name": "African Elephant",
        "emoji": "🐘",
        "region": "East Africa",
        "lat": -2.5,
        "lng": 34.8,
        "group": "Mammals",
        "habitat": "Savannas, forests and grasslands",
        "threat": "Habitat loss, conflict with people and poaching",
        "action": "Protect migration corridors and support community-led conservation.",
        "fact": "Elephants disperse seeds and help shape ecosystems.",
        "color": "#ffd166"
    },
    {
        "name": "Bengal Tiger",
        "emoji": "🐅",
        "region": "India",
        "lat": 22.5,
        "lng": 80.5,
        "group": "Mammals",
        "habitat": "Forests, grasslands and mangroves",
        "threat": "Habitat fragmentation and poaching",
        "action": "Protect connected forests and reduce conflict between tigers and people.",
        "fact": "Tigers are apex predators that help regulate prey populations.",
        "color": "#ffb86c"
    },
    {
        "name": "Giant Panda",
        "emoji": "🐼",
        "region": "China",
        "lat": 31.0,
        "lng": 103.0,
        "group": "Mammals",
        "habitat": "Mountain bamboo forests",
        "threat": "Habitat fragmentation and environmental change",
        "action": "Connect protected bamboo forests and conserve mountain habitats.",
        "fact": "Bamboo makes up most of a giant panda's diet.",
        "color": "#a6e3ff"
    },
    {
        "name": "Bornean Orangutan",
        "emoji": "🦧",
        "region": "Borneo",
        "lat": 0.9,
        "lng": 114.0,
        "group": "Mammals",
        "habitat": "Tropical rainforests",
        "threat": "Deforestation and forest fires",
        "action": "Protect intact rainforests and support responsible land use.",
        "fact": "Orangutans help spread seeds through the forest.",
        "color": "#ff9b71"
    },
    {
        "name": "Snow Leopard",
        "emoji": "🐆",
        "region": "Himalayas",
        "lat": 31.5,
        "lng": 79.0,
        "group": "Mammals",
        "habitat": "High-altitude mountain landscapes",
        "threat": "Habitat pressures and conflict involving livestock",
        "action": "Support local herders and protect mountain wildlife corridors.",
        "fact": "Snow leopards have thick fur and long tails adapted for mountain life.",
        "color": "#e2e6ff"
    },
    {
        "name": "Mountain Gorilla",
        "emoji": "🦍",
        "region": "Virunga Mountains",
        "lat": -1.45,
        "lng": 29.5,
        "group": "Mammals",
        "habitat": "Mountain forests",
        "threat": "Disease, habitat pressure and human disturbance",
        "action": "Support protected areas, veterinary care and responsible tourism.",
        "fact": "Gorillas live in social family groups.",
        "color": "#c4b5fd"
    },
    {
        "name": "Green Sea Turtle",
        "emoji": "🐢",
        "region": "Great Barrier Reef",
        "lat": -18.5,
        "lng": 147.0,
        "group": "Ocean",
        "habitat": "Tropical seas, seagrass meadows and nesting beaches",
        "threat": "Fishing gear, marine pollution and warming beaches",
        "action": "Protect nesting beaches and reduce accidental fishing capture.",
        "fact": "Adult green sea turtles mainly feed on seagrass and algae.",
        "color": "#67e8a5"
    },
    {
        "name": "Blue Whale",
        "emoji": "🐋",
        "region": "Pacific Ocean",
        "lat": 20.0,
        "lng": -125.0,
        "group": "Ocean",
        "habitat": "Open ocean",
        "threat": "Ship strikes, underwater noise and fishing gear entanglement",
        "action": "Support safer shipping practices and whale protection measures.",
        "fact": "Blue whales are the largest animals known to have lived.",
        "color": "#74c0fc"
    },
    {
        "name": "Polar Bear",
        "emoji": "🐻‍❄️",
        "region": "Arctic",
        "lat": 75.0,
        "lng": -100.0,
        "group": "Polar",
        "habitat": "Arctic sea ice and coastal regions",
        "threat": "Loss of sea ice caused by climate warming",
        "action": "Support climate mitigation and science-based Arctic conservation.",
        "fact": "Polar bears rely on sea ice to hunt seals.",
        "color": "#d8f4ff"
    },
    {
        "name": "Emperor Penguin",
        "emoji": "🐧",
        "region": "Antarctica",
        "lat": -73.0,
        "lng": 40.0,
        "group": "Polar",
        "habitat": "Antarctic sea ice",
        "threat": "Changes in sea ice conditions",
        "action": "Protect Antarctic ecosystems and reduce climate pressures.",
        "fact": "Emperor penguins breed during the Antarctic winter.",
        "color": "#b7d5ff"
    },
    {
        "name": "Jaguar",
        "emoji": "🐆",
        "region": "Amazon Basin",
        "lat": -5.0,
        "lng": -63.0,
        "group": "Mammals",
        "habitat": "Tropical forests and wetlands",
        "threat": "Deforestation and habitat fragmentation",
        "action": "Protect forest corridors and reduce illegal wildlife killing.",
        "fact": "Jaguars are powerful predators and strong swimmers.",
        "color": "#ffc86a"
    },
    {
        "name": "African Penguin",
        "emoji": "🐧",
        "region": "South Africa",
        "lat": -34.2,
        "lng": 18.5,
        "group": "Ocean",
        "habitat": "Southern African coasts and islands",
        "threat": "Reduced prey availability and marine environmental pressures",
        "action": "Protect breeding colonies and support sustainable fisheries.",
        "fact": "African penguins live along the southern African coastline.",
        "color": "#93e1ed"
    }
]

MISSIONS = [
    {
        "animal": "African Elephant",
        "title": "🐘 Elephant Corridor Rescue",
        "story": "A new road is planned across an elephant migration route.",
        "question": "Which plan best protects both elephants and nearby communities?",
        "choices": [
            "Block every elephant migration route",
            "Design wildlife crossings and protect migration corridors",
            "Move all elephants into a small enclosure"
        ],
        "correct": 1,
        "explain": "Wildlife crossings and protected corridors help elephants move safely and can reduce conflict."
    },
    {
        "animal": "Bornean Orangutan",
        "title": "🦧 Rainforest Rescue",
        "story": "An orangutan habitat is being fragmented by forest clearing.",
        "question": "Which conservation action is most helpful?",
        "choices": [
            "Protect connected forest habitat",
            "Remove all the remaining trees",
            "Release orangutans into unsuitable open grassland"
        ],
        "correct": 0,
        "explain": "Connected rainforests provide food, shelter and movement routes for orangutans."
    },
    {
        "animal": "Green Sea Turtle",
        "title": "🐢 Ocean Guardian",
        "story": "Sea turtles are being accidentally caught in fishing equipment.",
        "question": "What can reduce accidental capture?",
        "choices": [
            "Leave abandoned fishing gear in the sea",
            "Increase plastic waste near nesting beaches",
            "Use appropriate turtle-safe fishing practices and gear"
        ],
        "correct": 2,
        "explain": "Appropriate fishing practices and turtle-excluder devices can reduce accidental capture."
    },
    {
        "animal": "Snow Leopard",
        "title": "🐆 Mountain Guardian",
        "story": "A herder loses livestock and fears that snow leopards are responsible.",
        "question": "What is a constructive conservation response?",
        "choices": [
            "Support predator-resistant livestock enclosures and local communities",
            "Destroy all wild predators",
            "Remove every animal from the mountains"
        ],
        "correct": 0,
        "explain": "Better livestock protection and community programs can reduce human-wildlife conflict."
    },
    {
        "animal": "Blue Whale",
        "title": "🐋 Whale Safe Passage",
        "story": "Ships travel through an area used by whales.",
        "question": "Which action can lower the risk of collisions?",
        "choices": [
            "Ignore whale observations",
            "Use science-based routing and speed measures where appropriate",
            "Increase vessel speed in whale areas"
        ],
        "correct": 1,
        "explain": "In suitable areas, vessel routing and speed management can reduce collision risks."
    },
    {
        "animal": "Polar Bear",
        "title": "🐻‍❄️ Arctic Climate Mission",
        "story": "Polar bears depend on sea ice for hunting, but Arctic ice is changing.",
        "question": "Which response addresses the long-term environmental threat?",
        "choices": [
            "Assume one cold day solves the problem",
            "Ignore long-term sea ice trends",
            "Reduce greenhouse gas emissions and support Arctic research"
        ],
        "correct": 2,
        "explain": "Reducing emissions addresses climate warming, while research improves conservation decisions."
    }
]

HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>DOOM AI — Wildlife Guardian</title>
<script src="https://cdn.jsdelivr.net/npm/globe.gl@2.33.0/dist/globe.gl.min.js"></script>
<style>
*{box-sizing:border-box}
body{
 margin:0;background:#061522;color:#e9f9ff;
 font-family:Segoe UI,Arial,sans-serif
}
header{
 background:linear-gradient(90deg,#092b3d,#123957);
 padding:17px 22px;border-bottom:1px solid #296477;
 display:flex;justify-content:space-between;align-items:center;
 flex-wrap:wrap;gap:10px
}
h1{margin:0;font-size:25px;color:#5be4c3}
.subtitle{font-size:12px;color:#a5c9d7;margin-top:4px}
.layout{
 display:grid;grid-template-columns:minmax(0,1fr) 375px;
 min-height:calc(100vh - 80px)
}
.maparea{position:relative;min-height:620px}
#globe{height:calc(100vh - 140px);min-height:600px}
.toolbar{
 position:absolute;top:12px;left:12px;right:12px;
 z-index:5;display:flex;flex-wrap:wrap;gap:7px;
 pointer-events:none
}
.toolbar button{pointer-events:auto}
button{
 background:#17405a;color:#f0ffff;
 border:1px solid #367d91;border-radius:8px;
 padding:10px 12px;cursor:pointer;font-weight:600
}
button:hover{background:#266782}
button.active{background:#39d9b0;color:#062b2d}
button:disabled{opacity:.7;cursor:default}
aside{
 background:#0c2638;border-left:1px solid #27556c;
 padding:14px;overflow-y:auto;
 max-height:calc(100vh - 80px)
}
.panel{
 background:#12354a;border:1px solid #28647a;
 padding:15px;border-radius:13px;margin-bottom:13px
}
h2{font-size:17px;color:#69e5c6;margin:0 0 10px}
h3{font-size:15px;margin:0 0 10px}
p{line-height:1.5}
.muted{font-size:12px;color:#aac6d1}
#missionList{
 display:grid;grid-template-columns:1fr 1fr;gap:7px
}
#missionList button{text-align:left;font-size:12px}
.choice{
 display:block;width:100%;text-align:left;
 margin:7px 0;line-height:1.4
}
.good{background:#176b52!important}
.bad{background:#7b374a!important}
#score{font-size:21px;color:#ffe18a;font-weight:700}
#feedback{min-height:42px;color:#baf5df}
.mapnote{
 position:absolute;bottom:15px;left:15px;
 z-index:5;background:#082b3be8;
 padding:12px;border:1px solid #3a7a87;
 border-radius:10px;font-size:12px;
 max-width:420px
}
.stats{display:flex;gap:10px;flex-wrap:wrap}
.stat{
 background:#19445b;padding:10px;border-radius:10px;
 font-size:12px
}
.stat strong{font-size:19px;color:#65e4c4}
@media(max-width:950px){
 .layout{grid-template-columns:1fr}
 #globe{height:540px;min-height:540px}
 .maparea{min-height:590px}
 aside{max-height:none}
}
</style>
</head>
<body>

<header>
 <div>
  <h1>🐾 DOOM AI — WILDLIFE GUARDIAN</h1>
  <div class="subtitle">
   Explore Habitats • Discover Species • Make Conservation Decisions
  </div>
 </div>
 <div class="subtitle">MISSION 7 • EDUCATIONAL CONSERVATION SIMULATOR</div>
</header>

<div class="layout">
 <section class="maparea">
  <div id="globe"></div>
  <div class="toolbar" id="toolbar">
   <button class="active" onclick="filterAnimals('All',this)">🌍 All Animals</button>
   <button onclick="filterAnimals('Mammals',this)">🐘 Mammals</button>
   <button onclick="filterAnimals('Ocean',this)">🐋 Ocean Life</button>
   <button onclick="filterAnimals('Polar',this)">❄️ Polar Wildlife</button>
   <button onclick="focusRandom()">🎲 Discover Animal</button>
   <button onclick="resetView()">🌐 Reset Globe</button>
  </div>
  <div class="mapnote">
   🖱️ Rotate Earth • Scroll to zoom • Click animal markers
   <div class="muted" id="mapStatus">
    Educational habitat locations — not live animal positions
   </div>
  </div>
 </section>

 <aside>
  <div class="panel">
   <h2>🌎 Wildlife Explorer</h2>
   <div class="stats">
    <div class="stat"><strong id="animalCount">12</strong><br>Species examples</div>
    <div class="stat"><strong>6</strong><br>Rescue missions</div>
   </div>
   <h3 id="animalName" style="margin-top:14px">
    Select an animal on the globe
   </h3>
   <p id="animalFact">
    Discover habitats, threats and ways to protect wildlife.
   </p>
   <div id="animalInfo" class="muted"></div>
  </div>

  <div class="panel">
   <h2>🏆 Conservation Academy</h2>
   <div id="score">⭐ Score: 0 / 600</div>
   <p id="progress" class="muted">Choose a mission below.</p>
   <div id="missionList"></div>
  </div>

  <div class="panel">
   <h2 id="missionTitle">🌱 Choose Your Rescue Mission</h2>
   <p id="story">
    Learn about a conservation challenge and decide how to respond.
   </p>
   <h3 id="question"></h3>
   <div id="choices"></div>
   <p id="feedback"></p>
   <button id="nextButton" onclick="nextMission()" style="display:none">
    Next Rescue →
   </button>
  </div>

  <div class="panel">
   <h2>🔬 Research & Data Integrity</h2>
   <p class="muted">
    Animal markers show approximate representative habitat locations.
    They do not represent tagged animals, live movement, population
    estimates or current conservation status. Rescue situations are
    fictional educational scenarios based on real conservation issues.
    This application does not dispatch rescue teams or send reports
    to wildlife authorities.
   </p>
  </div>
 </aside>
</div>

<script>
const animals=__ANIMALS__;
const missions=__MISSIONS__;

let globe=null;
let currentFilter="All";
let currentMission=-1;
let answered=false;
let score=0;
let completed=new Set();

const el=id=>document.getElementById(id);

function makeMarker(animal){
 const root=document.createElement("div");
 root.style.cssText=`
  display:flex;align-items:center;gap:5px;
  cursor:pointer;white-space:nowrap;
  filter:drop-shadow(0 2px 3px #000)
 `;
 const symbol=document.createElement("span");
 symbol.textContent=animal.emoji;
 symbol.style.cssText=`
  display:grid;place-items:center;
  width:42px;height:42px;font-size:26px;
  background:#092d42e8;border:2px solid ${animal.color};
  border-radius:50%
 `;
 const label=document.createElement("span");
 label.textContent=animal.name;
 label.style.cssText=`
  background:#082336e8;border:1px solid #41758a;
  color:white;border-radius:7px;
  padding:5px 8px;font-size:12px;font-weight:bold
 `;
 root.append(symbol,label);
 root.title=animal.name;
 root.onclick=event=>{
  event.stopPropagation();
  showAnimal(animal);
 };
 return root;
}

function showAnimal(animal){
 el("animalName").textContent=animal.emoji+" "+animal.name;
 el("animalFact").textContent=animal.fact;
 el("animalInfo").innerHTML="";

 const fields=[
  ["Region",animal.region],
  ["Habitat",animal.habitat],
  ["Conservation threat",animal.threat],
  ["Helpful action",animal.action],
  ["Reference coordinates",
   animal.lat.toFixed(2)+"°, "+animal.lng.toFixed(2)+"°"]
 ];

 fields.forEach(([label,value])=>{
  const p=document.createElement("p");
  const strong=document.createElement("strong");
  strong.textContent=label+": ";
  p.append(strong,document.createTextNode(value));
  el("animalInfo").appendChild(p);
 });

 if(globe){
  globe.pointOfView({
   lat:animal.lat,lng:animal.lng,altitude:1.55
  },950);
 }
}

function filterAnimals(group,button){
 currentFilter=group;
 document.querySelectorAll("#toolbar button").forEach(b=>{
  b.classList.remove("active");
 });
 if(button)button.classList.add("active");
 updateMarkers();
}

function updateMarkers(){
 if(!globe)return;
 const shown=currentFilter==="All"
  ?animals:animals.filter(a=>a.group===currentFilter);
 globe.htmlElementsData(shown);
 el("animalCount").textContent=shown.length;
 el("mapStatus").textContent=
  shown.length+" educational habitat markers — not live tracking";
}

function focusRandom(){
 const pool=currentFilter==="All"
  ?animals:animals.filter(a=>a.group===currentFilter);
 if(pool.length){
  const item=pool[Math.floor(Math.random()*pool.length)];
  showAnimal(item);
 }
}

function resetView(){
 if(globe){
  globe.pointOfView({lat:10,lng:15,altitude:2.5},950);
 }
}

function initGlobe(){
 if(typeof Globe==="undefined"){
  el("mapStatus").textContent=
   "3D globe library unavailable. Check your internet connection.";
  return;
 }

 globe=Globe()(el("globe"))
  .globeImageUrl(
   "https://unpkg.com/three-globe/example/img/earth-blue-marble.jpg"
  )
  .bumpImageUrl(
   "https://unpkg.com/three-globe/example/img/earth-topology.png"
  )
  .backgroundColor("#061522")
  .htmlElementsData([])
  .htmlLat(d=>d.lat)
  .htmlLng(d=>d.lng)
  .htmlAltitude(0.025)
  .htmlElement(makeMarker);

 globe.pointOfView({lat:10,lng:15,altitude:2.5},0);
 globe.controls().autoRotate=true;
 globe.controls().autoRotateSpeed=0.25;

 const resize=()=>{
  const box=el("globe");
  globe.width(box.clientWidth);
  globe.height(box.clientHeight);
 };
 window.addEventListener("resize",resize);
 resize();
 updateMarkers();
}

function createMissionButtons(){
 missions.forEach((mission,i)=>{
  const b=document.createElement("button");
  b.id="mission-"+i;
  b.textContent=mission.title;
  b.onclick=()=>startMission(i);
  el("missionList").appendChild(b);
 });
}

function startMission(index){
 currentMission=index;
 answered=false;
 const m=missions[index];

 el("missionTitle").textContent=m.title;
 el("story").textContent=m.story;
 el("question").textContent=m.question;
 el("feedback").textContent="";
 el("nextButton").style.display="none";

 document.querySelectorAll("#missionList button").forEach(b=>{
  b.classList.remove("active");
 });
 el("mission-"+index).classList.add("active");

 const choices=el("choices");
 choices.innerHTML="";

 m.choices.forEach((choice,i)=>{
  const b=document.createElement("button");
  b.className="choice";
  b.textContent=(i+1)+". "+choice;
  b.onclick=()=>answer(i);
  choices.appendChild(b);
 });

 const animal=animals.find(a=>a.name===m.animal);
 if(animal)showAnimal(animal);

 el("progress").textContent=
  completed.size+" / "+missions.length+" missions completed";
}

function answer(index){
 if(answered)return;
 answered=true;

 const m=missions[currentMission];
 const correct=index===m.correct;
 const buttons=[...document.querySelectorAll("#choices button")];

 if(correct&&!completed.has(currentMission)){
  score+=100;
 }

 completed.add(currentMission);

 buttons.forEach((b,i)=>{
  b.disabled=true;
  if(i===m.correct)b.classList.add("good");
  else if(i===index)b.classList.add("bad");
 });

 el("feedback").textContent=
  (correct?"✅ Excellent conservation decision! ":
           "💡 Learning opportunity! ")+m.explain;

 el("score").textContent="⭐ Score: "+score+" / 600";
 el("progress").textContent=
  completed.size+" / "+missions.length+" missions completed";

 el("mission-"+currentMission).textContent="✓ "+m.title;
 el("nextButton").style.display="inline-block";
 el("nextButton").textContent=
  completed.size===missions.length
  ?"Replay Wildlife Academy ↻":"Next Rescue →";

 if(completed.size===missions.length){
  const p=document.createElement("p");
  p.textContent="🏆 All six rescue missions completed!";
  p.style.color="#ffe18a";
  el("feedback").appendChild(p);
 }
}

function nextMission(){
 if(completed.size===missions.length){
  completed.clear();
  score=0;
  el("score").textContent="⭐ Score: 0 / 600";
  missions.forEach((m,i)=>{
   el("mission-"+i).textContent=m.title;
  });
  startMission(0);
  return;
 }

 for(let i=1;i<=missions.length;i++){
  const next=(currentMission+i)%missions.length;
  if(!completed.has(next)){
   startMission(next);
   return;
  }
 }
}

createMissionButtons();
initGlobe();
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
            "__ANIMALS__", json.dumps(ANIMALS)
        ).replace(
            "__MISSIONS__", json.dumps(MISSIONS)
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

    url = f"http://127.0.0.1:{server.server_address[1]}/"

    print("=" * 56)
    print("DOOM AI — MISSION 7: WILDLIFE GUARDIAN")
    print("Local URL:", url)
    print("Press Ctrl+C to stop.")
    print("=" * 56)

    threading.Timer(
        1.0,
        lambda: webbrowser.open(url)
    ).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Wildlife Guardian...")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
