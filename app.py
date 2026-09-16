"""
Simple Slot Machine Web App (Flask)
------------------------------------
Free coins only. No real money. For demo/learning purposes.

How to run:
1) Install Python (if you don't have it).
2) In a terminal/command prompt, run:
   pip install flask
3) Save this file as `app.py` in a folder.
4) In the same folder, create a folder named `templates`.
5) Save the HTML code (slot_machine_template.html) as `templates/index.html`.
6) In the terminal, in that folder, run:
   python app.py
7) Open the link shown (usually http://127.0.0.1:5000) in your browser.

To share with others on your local network:
- Make sure they are on the same Wi‑Fi.
- Find your local IP (e.g., 192.168.x.x).
- They can open: http://YOUR_IP:5000

For public sharing online, you would later deploy to a hosting service
(e.g., Render, Railway, PythonAnywhere). This file is ready for that later.
"""

from flask import Flask, render_template, session, request, redirect, url_for
import random
import os

app = Flask(__name__)
# Secret key for session cookies (for demo only; use a random string in production)
app.secret_key = os.urandom(24)

# Slot machine configuration
SYMBOLS = ["🍒", "🍋", "🍇", "🍉", "🔔", "⭐", "💎", "7️⃣"]
SPIN_COST = 10
STARTING_COINS = 1000

# Payout multipliers (based on 3 reels)
# 2 matching = small win, 3 matching = big win
PAYOUTS = {
    "🍒": {"2": 5, "3": 20},
    "🍋": {"2": 5, "3": 20},
    "🍇": {"2": 10, "3": 30},
    "🍉": {"2": 10, "3": 30},
    "🔔": {"2": 15, "3": 50},
    "⭐": {"2": 20, "3": 75},
    "💎": {"2": 25, "3": 100},
    "7️⃣": {"2": 50, "3": 200},
}


def spin_reels():
    """Generate 3 random symbols for the slot machine."""
    return [random.choice(SYMBOLS) for _ in range(3)]


def calculate_winnings(reels):
    """
    Calculate winnings based on the 3 reels.
    Returns (win_amount, message).
    """
    # Count occurrences of each symbol
    counts = {}
    for s in reels:
        counts[s] = counts.get(s, 0) + 1

    # Check for 3 of a kind
    for symbol, count in counts.items():
        if count == 3:
            payout = PAYOUTS[symbol]["3"] * SPIN_COST
            return payout, f"Jackpot! 3 {symbol} — You won {payout} coins!"

    # Check for 2 of a kind
    for symbol, count in counts.items():
        if count == 2:
            payout = PAYOUTS[symbol]["2"] * SPIN_COST
            return payout, f"Nice! 2 {symbol} — You won {payout} coins!"

    # No win
    return 0, "No luck this time. Try again!"


@app.route("/")
def index():
    # Initialize session if needed
    if "coins" not in session:
        session["coins"] = STARTING_COINS
        session["username"] = "Player"
        session["history"] = []

    return render_template("index.html",
                           coins=session["coins"],
                           username=session["username"],
                           history=session.get("history", []),
                           spin_cost=SPIN_COST,
                           starting_coins=STARTING_COINS)


@app.route("/spin", methods=["POST"])
def spin():
    if "coins" not in session:
        session["coins"] = STARTING_COINS
        session["history"] = []

    if session["coins"] < SPIN_COST:
        # Not enough coins — reset
        session["coins"] = STARTING_COINS
        session["history"] = [("System", "Out of coins! Reset to starting balance.", STARTING_COINS)]
        return redirect(url_for("index"))

    # Deduct spin cost
    session["coins"] -= SPIN_COST

    # Spin the reels
    reels = spin_reels()
    win_amount, message = calculate_winnings(reels)

    # Add winnings
    session["coins"] += win_amount

    # Record history
    reels_str = " | ".join(reels)
    session["history"].append((reels_str, message, session["coins"]))
    # Keep only last 10 spins
    session["history"] = session["history"][-10:]

    session.modified = True
    return redirect(url_for("index"))


@app.route("/reset", methods=["POST"])
def reset():
    session["coins"] = STARTING_COINS
    session["history"] = [("System", "Balance reset.", STARTING_COINS)]
    session.modified = True
    return redirect(url_for("index"))


@app.route("/set_username", methods=["POST"])
def set_username():
    username = request.form.get("username", "Player").strip()
    if not username:
        username = "Player"
    session["username"] = username[:20]  # limit length
    return redirect(url_for("index"))


if __name__ == "__main__":
    # debug=True is fine for local development, not for production
    app.run(host="0.0.0.0", port=5000, debug=True)