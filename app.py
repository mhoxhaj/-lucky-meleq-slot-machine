from flask import Flask, render_template, session, request, redirect, url_for
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

SYMBOLS = ["🍒", "🍋", "🍇", "🍉", "🔔", "⭐", "💎", "7️⃣"]

SPIN_COST = 10
STARTING_COINS = 1000
WIN_AMOUNT = 100


def make_result_symbols(is_win, level, win_number=1):
    if is_win:
        symbol = SYMBOLS[(level + win_number - 1) % len(SYMBOLS)]
        return [symbol, symbol, symbol]

    return [
        SYMBOLS[level % len(SYMBOLS)],
        SYMBOLS[(level + 2) % len(SYMBOLS)],
        SYMBOLS[(level + 4) % len(SYMBOLS)],
    ]


def wins_after_losses(losses_needed):
    if losses_needed <= 10:
        return 1

    return losses_needed - 9


def initialize_player():
    if "coins" not in session:
        session["coins"] = STARTING_COINS
        session["username"] = "Player"
        session["history"] = []

        session["first_spin"] = True

        session["losses_needed"] = 2
        session["losses_done"] = 0

        session["wins_needed"] = 1
        session["wins_done"] = 0

        session["last_reels"] = ["🍒", "⭐", "💎"]
        session["last_message"] = "Welcome! Your first spin will be a win."
        session["last_was_win"] = False


def move_to_next_round():
    if session["losses_needed"] >= 15:
        session["losses_needed"] = 2
    else:
        session["losses_needed"] += 1

    session["losses_done"] = 0
    session["wins_needed"] = wins_after_losses(session["losses_needed"])
    session["wins_done"] = 0


@app.route("/")
def index():
    initialize_player()

    return render_template(
        "index.html",
        coins=session["coins"],
        username=session["username"],
        history=session.get("history", []),
        spin_cost=SPIN_COST,
        starting_coins=STARTING_COINS,
        last_reels=session["last_reels"],
        last_message=session["last_message"],
        last_was_win=session["last_was_win"],
    )


@app.route("/spin", methods=["POST"])
def spin():
    initialize_player()

    if session["coins"] < SPIN_COST:
        session.clear()
        initialize_player()

        session["last_reels"] = ["💎", "💎", "💎"]
        session["last_message"] = (
            "Out of coins. Your balance was reset to 1000 free coins. "
            "Your next spin will be a win."
        )
        session["last_was_win"] = False
        session.modified = True

        return redirect(url_for("index"))

    session["coins"] -= SPIN_COST

    if session["first_spin"]:
        is_win = True
        level = 1
        win_number = 1

        session["first_spin"] = False
        session["coins"] += WIN_AMOUNT

        message = f"Welcome win! You won {WIN_AMOUNT} free coins!"

    elif session["losses_done"] >= session["losses_needed"]:
        is_win = True
        level = session["losses_needed"]

        session["wins_done"] += 1
        win_number = session["wins_done"]

        session["coins"] += WIN_AMOUNT

        message = (
            f"Winner! Win {session['wins_done']} of {session['wins_needed']} "
            f"after {session['losses_needed']} losses. "
            f"You won {WIN_AMOUNT} free coins!"
        )

        if session["wins_done"] >= session["wins_needed"]:
            move_to_next_round()

    else:
        is_win = False
        level = session["losses_needed"]
        win_number = 0

        session["losses_done"] += 1
        remaining = session["losses_needed"] - session["losses_done"]

        if remaining == 0:
            message = (
                f"No win this spin. The next {session['wins_needed']} "
                f"spin(s) will be win(s)!"
            )
        else:
            message = (
                f"No win this spin. {remaining} loss/losses remain before "
                f"the next winning round."
            )

    reels = make_result_symbols(is_win, level, win_number)

    session["last_reels"] = reels
    session["last_message"] = message
    session["last_was_win"] = is_win

    reels_text = " | ".join(reels)

    session["history"].append(
        (reels_text, message, session["coins"])
    )

    session["history"] = session["history"][-10:]

    session.modified = True

    return redirect(url_for("index"))


@app.route("/reset", methods=["POST"])
def reset():
    session.clear()
    initialize_player()
    session.modified = True

    return redirect(url_for("index"))


@app.route("/set_username", methods=["POST"])
def set_username():
    initialize_player()

    username = request.form.get("username", "Player").strip()

    if username:
        session["username"] = username[:20]
    else:
        session["username"] = "Player"

    session.modified = True

    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)