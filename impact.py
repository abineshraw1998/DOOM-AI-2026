
import tkinter as tk
from tkinter import ttk, messagebox
import re

# ============================================================
# DOOM AI — MISSION 5
# COMMUNICATION IMPACT SIMULATOR
#
# Educational, rule-based communication analysis.
# Does not predict actual human emotions.
# No API key or external packages required.
# ============================================================

BG = "#071527"
PANEL = "#102b43"
PANEL_2 = "#153751"
TEXT = "#e9f6ff"
MUTED = "#a8c7dc"
BLUE = "#49caff"
GREEN = "#55e6ab"
ORANGE = "#ffba64"
PURPLE = "#ba9cff"

POSITIVE = {
    "thank", "thanks", "please", "great", "wonderful",
    "appreciate", "happy", "help", "kind", "excellent",
    "love", "good", "welcome", "support", "sorry",
    "amazing", "well", "respect", "glad", "proud"
}

NEGATIVE = {
    "hate", "stupid", "idiot", "bad", "useless",
    "terrible", "wrong", "angry", "never", "failure",
    "shut", "awful", "blame", "worst", "lazy",
    "rubbish", "annoying", "disappointed"
}

URGENT = {
    "urgent", "immediately", "now", "asap",
    "emergency", "quickly", "hurry", "deadline"
}


def clamp(value):
    return max(0, min(100, round(value)))


def analyze_message(message):
    words = re.findall(r"[a-z']+", message.lower())

    positive = sum(word in POSITIVE for word in words)
    negative = sum(word in NEGATIVE for word in words)
    urgent = sum(word in URGENT for word in words)

    exclamations = message.count("!")
    questions = message.count("?")

    letters = [c for c in message if c.isalpha()]
    uppercase = sum(c.isupper() for c in letters)

    shouting = (
        len(letters) >= 8
        and uppercase / len(letters) > 0.6
    )

    warmth = clamp(
        50 + positive * 14 - negative * 16
    )

    clarity = clamp(
        85
        - max(0, len(words) - 25)
        - exclamations * 3
        - max(0, questions - 2) * 4
    )

    calmness = clamp(
        85
        - negative * 15
        - urgent * 12
        - exclamations * 5
        - (20 if shouting else 0)
    )

    urgency = clamp(
        10 + urgent * 24 + exclamations * 8
    )

    if negative > positive:
        tone = "Potentially harsh or critical"
    elif positive > negative:
        tone = "Friendly or supportive"
    elif urgent:
        tone = "Urgent"
    elif questions:
        tone = "Questioning or inquisitive"
    else:
        tone = "Neutral or mixed"

    return {
        "tone": tone,
        "warmth": warmth,
        "clarity": clarity,
        "calmness": calmness,
        "urgency": urgency,
        "positive": positive,
        "negative": negative,
        "word_count": len(words)
    }


def create_rewrite(message, style):
    clean = message.strip()

    if style == "Polite":
        return (
            "Hello,\n\n"
            "Could you please consider the following?\n\n"
            f"{clean}\n\n"
            "Thank you for your time."
        )

    if style == "Professional":
        return (
            "Hello,\n\n"
            "I would like to discuss the following:\n\n"
            f"{clean}\n\n"
            "Please let me know your thoughts.\n\n"
            "Best regards"
        )

    if style == "Encouraging":
        return (
            "I believe we can work through this together.\n\n"
            f"{clean}\n\n"
            "Thank you for your effort and support!"
        )

    if style == "Simple":
        sentences = re.split(
            r"(?<=[.!?])\s+",
            clean
        )
        return "\n".join(sentences)

    return clean


def update_chart(scores):
    chart.delete("all")

    metrics = [
        ("Warmth", scores["warmth"], GREEN),
        ("Clarity", scores["clarity"], BLUE),
        ("Calmness", scores["calmness"], PURPLE),
        ("Urgency", scores["urgency"], ORANGE)
    ]

    width = 320

    for i, (label, value, color) in enumerate(metrics):
        y = 18 + i * 63

        chart.create_text(
            16, y + 13,
            text=label,
            anchor="w",
            fill=TEXT,
            font=("Segoe UI", 11, "bold")
        )

        chart.create_rectangle(
            115, y,
            115 + width, y + 26,
            fill="#27475f",
            outline=""
        )

        chart.create_rectangle(
            115, y,
            115 + width * value / 100,
            y + 26,
            fill=color,
            outline=""
        )

        chart.create_text(
            450, y + 13,
            text=f"{value}/100",
            anchor="w",
            fill=TEXT,
            font=("Segoe UI", 10, "bold")
        )


def analyze():
    message = message_input.get("1.0", "end").strip()

    if not message:
        messagebox.showwarning(
            "DOOM AI",
            "Please enter a message first."
        )
        return

    scores = analyze_message(message)

    result_var.set(
        f"Estimated tone: {scores['tone']}\n"
        f"Words: {scores['word_count']}  |  "
        f"Positive cues: {scores['positive']}  |  "
        f"Negative cues: {scores['negative']}"
    )

    update_chart(scores)

    reactions.delete("1.0", "end")

    if scores["warmth"] >= 65:
        friend = "May interpret the message as friendly."
    elif scores["warmth"] <= 35:
        friend = "May perceive the wording as harsh."
    else:
        friend = "May interpret the tone as neutral."

    if scores["clarity"] >= 70:
        student = "May find the wording relatively clear."
    else:
        student = "May benefit from a simpler explanation."

    if scores["calmness"] < 45:
        teacher = "May suggest a calmer, more respectful tone."
    else:
        teacher = "May appreciate the measured tone."

    if scores["urgency"] >= 60:
        coworker = "May prioritize the request as urgent."
    else:
        coworker = "May treat it as a routine message."

    reactions.insert(
        "1.0",
        "👫 FRIEND\n"
        f"{friend}\n\n"
        "🎓 STUDENT\n"
        f"{student}\n\n"
        "👩‍🏫 TEACHER\n"
        f"{teacher}\n\n"
        "💼 COWORKER\n"
        f"{coworker}\n\n"
        "These are illustrative possibilities, "
        "not verified predictions."
    )


def rewrite():
    message = message_input.get("1.0", "end").strip()

    if not message:
        messagebox.showwarning(
            "DOOM AI",
            "Please enter a message first."
        )
        return

    style = tone_choice.get()

    rewritten = create_rewrite(message, style)

    rewrite_output.delete("1.0", "end")

    rewrite_output.insert(
        "1.0",
        rewritten
        + "\n\n[Template-based rewrite: review before sending.]"
    )


def copy_rewrite():
    text = rewrite_output.get("1.0", "end").strip()

    if not text:
        messagebox.showinfo(
            "DOOM AI",
            "Generate a rewrite first."
        )
        return

    root.clipboard_clear()
    root.clipboard_append(text)

    messagebox.showinfo(
        "DOOM AI",
        "Rewritten message copied!"
    )


def load_example(kind):
    examples = {
        "friendly":
            "Thank you for helping me today. "
            "I really appreciate your support!",

        "angry":
            "THIS IS TERRIBLE! You never listen! "
            "Fix this now!",

        "urgent":
            "URGENT: Please send the report ASAP. "
            "We have a deadline today!"
    }

    message_input.delete("1.0", "end")
    message_input.insert(
        "1.0",
        examples[kind]
    )

    analyze()


# ============================================================
# USER INTERFACE
# ============================================================

root = tk.Tk()
root.title(
    "DOOM AI — Communication Impact Simulator"
)
root.geometry("1080x850")
root.minsize(820, 700)
root.configure(bg=BG)

style = ttk.Style()
style.theme_use("clam")
style.configure(
    "TCombobox",
    padding=7
)

title = tk.Label(
    root,
    text="🧠 DOOM AI — COMMUNICATION IMPACT",
    font=("Segoe UI", 23, "bold"),
    bg=BG,
    fg=BLUE
)
title.pack(pady=(18, 5))

subtitle = tk.Label(
    root,
    text=(
        "Explore how different messages might "
        "influence communication"
    ),
    font=("Segoe UI", 11),
    bg=BG,
    fg=MUTED
)
subtitle.pack(pady=(0, 15))

main = tk.Frame(root, bg=BG)
main.pack(
    fill="both",
    expand=True,
    padx=24
)

tk.Label(
    main,
    text="✍️ ENTER YOUR MESSAGE",
    font=("Segoe UI", 12, "bold"),
    bg=BG,
    fg=TEXT
).pack(anchor="w")

message_input = tk.Text(
    main,
    height=4,
    bg=PANEL,
    fg=TEXT,
    insertbackground="white",
    font=("Segoe UI", 12),
    wrap="word",
    relief="flat",
    padx=12,
    pady=12
)
message_input.pack(
    fill="x",
    pady=8
)

message_input.insert(
    "1.0",
    "Please send me the report when you have time. Thank you!"
)

examples = tk.Frame(main, bg=BG)
examples.pack(
    fill="x",
    pady=5
)

for label, kind in [
    ("😊 Friendly example", "friendly"),
    ("😠 Angry example", "angry"),
    ("⚡ Urgent example", "urgent")
]:
    tk.Button(
        examples,
        text=label,
        command=lambda k=kind: load_example(k),
        bg=PANEL_2,
        fg=TEXT,
        relief="flat",
        padx=10,
        pady=7
    ).pack(
        side="left",
        padx=(0, 10)
    )

controls = tk.Frame(main, bg=BG)
controls.pack(
    fill="x",
    pady=12
)

tk.Button(
    controls,
    text="🔍 ANALYZE IMPACT",
    command=analyze,
    bg=BLUE,
    fg=BG,
    font=("Segoe UI", 11, "bold"),
    padx=14,
    pady=9
).pack(
    side="left",
    padx=(0, 12)
)

tone_choice = ttk.Combobox(
    controls,
    values=[
        "Polite",
        "Professional",
        "Encouraging",
        "Simple"
    ],
    state="readonly",
    width=17
)
tone_choice.set("Polite")
tone_choice.pack(
    side="left",
    padx=6
)

tk.Button(
    controls,
    text="✨ REWRITE",
    command=rewrite,
    bg=GREEN,
    fg=BG,
    font=("Segoe UI", 11, "bold"),
    padx=14,
    pady=9
).pack(
    side="left",
    padx=8
)

tk.Button(
    controls,
    text="📋 COPY",
    command=copy_rewrite,
    bg=PURPLE,
    fg=BG,
    font=("Segoe UI", 11, "bold"),
    padx=14,
    pady=9
).pack(
    side="left",
    padx=8
)

result_var = tk.StringVar(
    value="Click ANALYZE IMPACT to begin."
)

tk.Label(
    main,
    textvariable=result_var,
    justify="left",
    font=("Segoe UI", 11),
    bg=BG,
    fg=TEXT
).pack(
    anchor="w",
    pady=10
)

tk.Label(
    main,
    text="📊 ESTIMATED COMMUNICATION METRICS",
    font=("Segoe UI", 12, "bold"),
    bg=BG,
    fg=BLUE
).pack(
    anchor="w",
    pady=(8, 5)
)

chart = tk.Canvas(
    main,
    width=530,
    height=270,
    bg=PANEL,
    highlightthickness=0
)
chart.pack(
    anchor="w",
    pady=5
)

lower = tk.Frame(main, bg=BG)
lower.pack(
    fill="both",
    expand=True,
    pady=10
)

left = tk.Frame(lower, bg=BG)
left.pack(
    side="left",
    fill="both",
    expand=True,
    padx=(0, 8)
)

right = tk.Frame(lower, bg=BG)
right.pack(
    side="left",
    fill="both",
    expand=True,
    padx=(8, 0)
)

tk.Label(
    left,
    text="👥 POSSIBLE AUDIENCE REACTIONS",
    font=("Segoe UI", 11, "bold"),
    bg=BG,
    fg=BLUE
).pack(
    anchor="w",
    pady=5
)

reactions = tk.Text(
    left,
    height=11,
    bg=PANEL,
    fg=TEXT,
    font=("Segoe UI", 10),
    wrap="word",
    relief="flat",
    padx=12,
    pady=12
)
reactions.pack(
    fill="both",
    expand=True
)

tk.Label(
    right,
    text="✨ REWRITTEN MESSAGE",
    font=("Segoe UI", 11, "bold"),
    bg=BG,
    fg=BLUE
).pack(
    anchor="w",
    pady=5
)

rewrite_output = tk.Text(
    right,
    height=11,
    bg=PANEL,
    fg=TEXT,
    font=("Segoe UI", 10),
    wrap="word",
    relief="flat",
    padx=12,
    pady=12
)
rewrite_output.pack(
    fill="both",
    expand=True
)

tk.Label(
    root,
    text=(
        "Educational simulation • Rule-based estimates "
        "• No guaranteed emotional prediction "
        "• No external API required"
    ),
    bg=BG,
    fg=MUTED,
    font=("Segoe UI", 9)
).pack(pady=12)

analyze()

root.mainloop()
