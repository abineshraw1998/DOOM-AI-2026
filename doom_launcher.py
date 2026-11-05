
import os
import sys
import subprocess
import tkinter as tk
from tkinter import messagebox
from pathlib import Path
from datetime import datetime

# ==========================================================
# DOOM AI — GLOBAL INTELLIGENCE COMMAND CENTER
# Mission launcher for the Meta AI Developer Hackathon
# ==========================================================

BASE = Path(__file__).resolve().parent

BG = "#061323"
CARD = "#10283e"
BORDER = "#24506a"
WHITE = "#eaf8ff"
MUTED = "#93b4c8"
CYAN = "#48cfff"
GREEN = "#48e5ac"
PURPLE = "#b59bff"
ORANGE = "#ffbc70"

MISSIONS = [
    {
        "number": "01",
        "icon": "💬",
        "name": "COMMUNICATION INTELLIGENCE",
        "subtitle": "Translate • Rewrite • Understand",
        "description": "Explore multilingual communication and AI-assisted language tools.",
        "files": ["app.py"],
        "color": CYAN
    },
    {
        "number": "02",
        "icon": "🌍",
        "name": "NATURE & EARTH INTELLIGENCE",
        "subtitle": "Weather • Earthquakes • Wildfires",
        "description": "Explore public Earth observation and environmental information.",
        "files": ["nature.py"],
        "color": GREEN
    },
    {
        "number": "03",
        "icon": "🚀",
        "name": "SPACE INTELLIGENCE",
        "subtitle": "ISS • Satellites • Astronomy",
        "description": "Discover space science through interactive visualizations.",
        "files": ["space.py"],
        "color": PURPLE
    },
    {
        "number": "04",
        "icon": "✈️",
        "name": "FLIGHT INTELLIGENCE",
        "subtitle": "Aircraft • Routes • Aviation",
        "description": "Explore available aircraft data and clearly labeled simulations.",
        "files": ["flight.py"],
        "color": ORANGE
    },
    {
        "number": "05",
        "icon": "🧠",
        "name": "COMMUNICATION IMPACT",
        "subtitle": "Tone • Clarity • Rewriting",
        "description": "Analyze estimated message tone and explore alternative wording.",
        "files": [
            "impact.py",
            "communication_impact.py",
            "communication_impact_simulator.py",
            "mission5.py"
        ],
        "color": CYAN
    },
    {
        "number": "06",
        "icon": "🌐",
        "name": "EARTH QUEST",
        "subtitle": "3D Globe • Planet Rescue",
        "description": "Explore geography, volcanoes, oceans and conservation challenges.",
        "files": ["earth_quest.py", "Earth_quest.py"],
        "color": GREEN
    },
    {
        "number": "07",
        "icon": "🐾",
        "name": "WILDLIFE GUARDIAN",
        "subtitle": "Habitats • Species • Rescue",
        "description": "Discover animal habitats and make educational conservation decisions.",
        "files": ["wildlife.py", "wildlife_guardian.py"],
        "color": ORANGE
    }
]


def find_script(mission):
    """Find a matching script without relying on filename capitalization."""
    if not BASE.exists():
        return None

    available = {
        p.name.lower(): p
        for p in BASE.iterdir()
        if p.is_file() and p.suffix.lower() == ".py"
    }

    for filename in mission["files"]:
        match = available.get(filename.lower())
        if match:
            return match

    return None


class CommandCenter:

    def __init__(self, root):
        self.root = root
        self.root.title("DOOM AI — Global Intelligence Command Center")
        self.root.geometry("1250x790")
        self.root.minsize(850, 620)
        self.root.configure(bg=BG)

        self.status_text = tk.StringVar(value="SYSTEM READY")
        self.clock_text = tk.StringVar()
        self.cards = []

        self.build_ui()
        self.refresh_status()
        self.update_clock()

    def build_ui(self):
        header = tk.Frame(self.root, bg=BG)
        header.pack(fill="x", padx=28, pady=(24, 12))

        tk.Label(
            header,
            text="◈  DOOM AI",
            font=("Segoe UI", 34, "bold"),
            fg=CYAN,
            bg=BG
        ).pack(anchor="w")

        tk.Label(
            header,
            text="GLOBAL INTELLIGENCE COMMAND CENTER",
            font=("Segoe UI", 15, "bold"),
            fg=WHITE,
            bg=BG
        ).pack(anchor="w", pady=(2, 5))

        tk.Label(
            header,
            text="EXPLORE  •  DISCOVER  •  UNDERSTAND  •  PROTECT",
            font=("Segoe UI", 10),
            fg=MUTED,
            bg=BG
        ).pack(anchor="w")

        line = tk.Frame(self.root, bg=CYAN, height=2)
        line.pack(fill="x", padx=28, pady=(8, 15))

        stats = tk.Frame(self.root, bg=BG)
        stats.pack(fill="x", padx=28, pady=(0, 16))

        self.ready_label = tk.Label(
            stats,
            text="CHECKING MISSIONS...",
            font=("Segoe UI", 12, "bold"),
            fg=GREEN,
            bg=BG
        )
        self.ready_label.pack(side="left")

        tk.Label(
            stats,
            textvariable=self.clock_text,
            font=("Consolas", 11),
            fg=MUTED,
            bg=BG
        ).pack(side="right")

        tk.Label(
            self.root,
            text="SELECT YOUR INTELLIGENCE MISSION",
            font=("Segoe UI", 13, "bold"),
            fg=WHITE,
            bg=BG
        ).pack(anchor="w", padx=28, pady=(0, 12))

        outer = tk.Frame(self.root, bg=BG)
        outer.pack(fill="both", expand=True, padx=20)

        self.canvas = tk.Canvas(
            outer,
            bg=BG,
            highlightthickness=0
        )
        scrollbar = tk.Scrollbar(
            outer,
            orient="vertical",
            command=self.canvas.yview
        )

        self.inner = tk.Frame(self.canvas, bg=BG)

        self.inner.bind(
            "<Configure>",
            lambda event: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.window_id = self.canvas.create_window(
            (0, 0),
            window=self.inner,
            anchor="nw"
        )

        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.canvas.bind(
            "<Configure>",
            self.resize_cards
        )

        for mission in MISSIONS:
            self.create_card(mission)

        footer = tk.Frame(self.root, bg="#0b2236")
        footer.pack(fill="x", side="bottom")

        tk.Label(
            footer,
            textvariable=self.status_text,
            font=("Consolas", 10),
            fg=GREEN,
            bg="#0b2236",
            anchor="w"
        ).pack(side="left", padx=20, pady=12)

        tk.Button(
            footer,
            text="↻ REFRESH",
            command=self.refresh_status,
            bg="#1c4b65",
            fg=WHITE,
            relief="flat",
            padx=16,
            pady=6
        ).pack(side="right", padx=20, pady=7)

    def create_card(self, mission):
        card = tk.Frame(
            self.inner,
            bg=CARD,
            highlightbackground=BORDER,
            highlightthickness=1
        )
        self.cards.append(card)

        top = tk.Frame(card, bg=CARD)
        top.pack(fill="x", padx=17, pady=(14, 7))

        tk.Label(
            top,
            text=mission["icon"],
            font=("Segoe UI Emoji", 26),
            bg=CARD,
            fg=WHITE
        ).pack(side="left")

        tk.Label(
            top,
            text="  MISSION " + mission["number"],
            font=("Consolas", 11, "bold"),
            bg=CARD,
            fg=mission["color"]
        ).pack(side="left")

        status = tk.Label(
            top,
            text="CHECKING",
            font=("Consolas", 9, "bold"),
            bg=CARD,
            fg=MUTED
        )
        status.pack(side="right")

        tk.Label(
            card,
            text=mission["name"],
            font=("Segoe UI", 13, "bold"),
            fg=WHITE,
            bg=CARD,
            anchor="w",
            wraplength=420,
            justify="left"
        ).pack(fill="x", padx=17, pady=(2, 3))

        tk.Label(
            card,
            text=mission["subtitle"],
            font=("Segoe UI", 10, "bold"),
            fg=mission["color"],
            bg=CARD,
            anchor="w"
        ).pack(fill="x", padx=17)

        tk.Label(
            card,
            text=mission["description"],
            font=("Segoe UI", 10),
            fg=MUTED,
            bg=CARD,
            wraplength=430,
            justify="left",
            anchor="nw"
        ).pack(fill="x", padx=17, pady=(10, 12))

        launch_button = tk.Button(
            card,
            text="▶  LAUNCH MISSION",
            command=lambda m=mission: self.launch(m),
            font=("Segoe UI", 10, "bold"),
            bg=mission["color"],
            fg="#061323",
            activebackground=WHITE,
            activeforeground=BG,
            relief="flat",
            cursor="hand2",
            pady=10
        )
        launch_button.pack(fill="x", padx=17, pady=(0, 15))

        mission["status_widget"] = status
        mission["button_widget"] = launch_button

    def resize_cards(self, event):
        width = max(1, event.width)
        self.canvas.itemconfigure(self.window_id, width=width)

        columns = 2 if width >= 760 else 1

        for card in self.cards:
            card.grid_forget()

        for i, card in enumerate(self.cards):
            card.grid(
                row=i // columns,
                column=i % columns,
                sticky="nsew",
                padx=8,
                pady=8
            )

        for col in range(2):
            self.inner.grid_columnconfigure(
                col,
                weight=1 if col < columns else 0
            )

    def refresh_status(self):
        ready = 0

        for mission in MISSIONS:
            script = find_script(mission)

            if script:
                ready += 1
                mission["status_widget"].config(
                    text="● FOUND",
                    fg=GREEN
                )
                mission["button_widget"].config(
                    state="normal"
                )
            else:
                mission["status_widget"].config(
                    text="● FILE MISSING",
                    fg=ORANGE
                )
                mission["button_widget"].config(
                    state="normal"
                )

        self.ready_label.config(
            text=f"● {ready} / {len(MISSIONS)} MISSION FILES FOUND"
        )

        self.status_text.set(
            "READY • Select a mission to launch"
        )

    def launch(self, mission):
        script = find_script(mission)

        if not script:
            names = "\n".join(mission["files"])
            messagebox.showwarning(
                "Mission file not found",
                "Could not find this mission's Python file.\n\n"
                "Expected one of:\n"
                + names
                + "\n\nProject folder:\n"
                + str(BASE)
                + "\n\nCheck the filename in VS Code."
            )
            return

        try:
            # Launch each mission independently.
            # Existing applications remain unchanged.
            subprocess.Popen(
                [sys.executable, str(script)],
                cwd=str(BASE),
                creationflags=(
                    subprocess.CREATE_NEW_CONSOLE
                    if os.name == "nt"
                    else 0
                )
            )

            self.status_text.set(
                f"LAUNCHED • {mission['name']} • {script.name}"
            )

        except Exception as error:
            messagebox.showerror(
                "Launch failed",
                str(error)
            )
            self.status_text.set(
                "ERROR • Mission could not launch"
            )

    def update_clock(self):
        self.clock_text.set(
            datetime.now().strftime(
                "%d %b %Y  •  %H:%M:%S"
            )
        )
        self.root.after(1000, self.update_clock)


if __name__ == "__main__":
    root = tk.Tk()
    app = CommandCenter(root)
    root.mainloop()
