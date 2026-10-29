"""
Core gameplay and GUI controller for Tavern Dice.

The basic player management, dice selection and scoring
logic were written by Donglai Zheng.

ChatGPT assisted with GUI event handling, animations
and screen transitions.

See AI_DECLARATION.txt for details.
"""
import tkinter as tk
import view
from rules import roll_dice, has_scoring_dice, score_selection


game = {}
ui = {}
MAX_TARGET = 999999
ROLL_FRAMES = 24
ROLL_INTERVAL = 25


def player_name():
    """Return the display name for the current player's zero-based index."""
    return "Player " + str(game["player"] + 1)


def cancel_pending():
    """Cancel the scheduled step and invalidate callbacks from older steps."""
    ui["generation"] = ui.get("generation", 0) + 1
    job = ui.get("job")
    if job is not None:
        ui["window"].after_cancel(job)
    ui["job"] = None
    ui["pending"] = None


def schedule(delay, callback, *args):
    """Schedule one callback after delay milliseconds without blocking the GUI.

    The saved generation number prevents an old callback from changing
    a paused, restarted or closed game.
    """
    cancel_pending()
    generation = ui["generation"]
    ui["pending"] = (delay, callback, args)

    def run_next():
        if generation != ui["generation"]:
            return
        ui["job"] = None
        ui["pending"] = None
        callback(*args)

    ui["job"] = ui["window"].after(delay, run_next)


def pause_pending():
    """Pause for rules or leave confirmation, keeping the next step to resume."""
    pending = ui.get("pending")
    cancel_pending()
    ui["pending"] = pending


def resume_pending():
    """Reschedule a paused step using its full original delay."""
    pending = ui.get("pending")
    if pending is not None:
        delay, callback, args = pending
        schedule(delay, callback, *args)


def refresh_ui():
    view.render(game, ui)


def empty_match(target=4000):
    """Reset match data with fresh lists so no previous scores or dice remain."""
    game.clear()
    game.update({
        "scores": [0, 0], "player": 0, "target": target,
        "turn_score": 0, "dice": [], "kept": [], "selected": [],
        "last_dice": [], "last_available": 0, "phase": "ready",
        "message": "", "lost": 0, "banked": 0
    })


def show_menu():
    cancel_pending()
    empty_match()
    ui.update(screen="menu", error="", frame=None, shake=0)
    refresh_ui()


def show_setup():
    cancel_pending()
    ui.update(screen="setup", error="")
    refresh_ui()


def choose_preset(target):
    if ui["screen"] != "setup":
        return
    ui["target_var"].set(str(target))
    ui["error"] = ""
    refresh_ui()


def parse_target(text):
    """Return a target from 1 to MAX_TARGET, or raise ValueError for bad input."""
    text = text.strip()
    if not text or not text.isascii() or not text.isdecimal():
        raise ValueError("Enter a whole number from 1 to 999,999.")
    text = text.lstrip("0") or "0"
    if len(text) > 6 or not 1 <= int(text) <= MAX_TARGET:
        raise ValueError("Choose a target between 1 and 999,999.")
    return int(text)


def start_match():
    """Validate the setup input and show an error or start the match."""
    if ui["screen"] != "setup":
        return
    try:
        target = parse_target(ui["target_var"].get())
    except ValueError as error:
        ui["error"] = str(error)
        refresh_ui()
        ui["entry"].focus_set()
        return
    new_match(target)


def new_match(target):
    """Clear the previous match and automatically start Player 1's first roll."""
    cancel_pending()
    empty_match(target)
    ui.update(screen="game", error="", frame=None, shake=0)
    ui["window"].focus_set()
    start_turn()


def play_again():
    if ui["screen"] == "victory":
        new_match(game["target"])


def show_rules():
    """Open the rules page without losing the match or its paused animation."""
    if ui["screen"] not in ("menu", "game"):
        return
    pause_pending()
    ui["return_screen"] = ui["screen"]
    ui["screen"] = "rules"
    refresh_ui()


def return_from_panel():
    """Return from rules or leave confirmation and resume any paused step."""
    if ui["screen"] not in ("rules", "confirm"):
        return
    ui["screen"] = ui["return_screen"]
    refresh_ui()
    resume_pending()


def request_menu():
    if ui["screen"] != "game":
        return
    pause_pending()
    ui.update(screen="confirm", return_screen="game")
    refresh_ui()


def escape_key(event=None):
    screen = ui["screen"]
    if screen in ("rules", "confirm"):
        return_from_panel()
    elif screen == "game":
        request_menu()
    elif screen in ("setup", "victory"):
        show_menu()
    return "break"


def selected_dice():
    """Return the current roll's face values at the selected positions."""
    values = []
    for index in game["selected"]:
        values.append(game["dice"][index])
    return values


def on_die_click(index):
    """Toggle a zero-based die position only while selecting the current roll."""
    if ui["screen"] != "game" or game["phase"] != "selecting":
        return
    if index < 0 or index >= len(game["dice"]):
        return
    if index in game["selected"]:
        game["selected"].remove(index)
    else:
        game["selected"].append(index)
    refresh_ui()


def number_key(event):
    if event.char in "123456" and event.char:
        if ui["screen"] == "game":
            on_die_click(int(event.char) - 1)
            return "break"


def start_turn():
    if ui["screen"] == "game" and game["phase"] == "ready":
        roll_current(6)


def roll_current(amount, notice=""):
    # Generate the actual result once; animation changes only its appearance.
    result = roll_dice(amount)
    game.update(dice=result, selected=[], phase="rolling", message=notice)
    animate_roll(0)


def animate_roll(frame):
    """Display the next rolling frame, then reveal the already generated result."""
    if ui["screen"] != "game" or game["phase"] != "rolling":
        return
    ui["frame"] = frame
    if frame == ROLL_FRAMES:
        ui["frame"] = None
        finish_roll()
        return
    refresh_ui()
    schedule(ROLL_INTERVAL, animate_roll, frame + 1)


def finish_roll():
    if game["phase"] != "rolling" or ui["screen"] != "game":
        return
    if has_scoring_dice(game["dice"]):
        game["phase"] = "selecting"
        refresh_ui()
    else:
        # Let the player see the failed roll before BUST or a player change.
        game["phase"] = "settling"
        game["lost"] = game["turn_score"]
        refresh_ui()
        schedule(350, show_bust)


def show_bust():
    """Discard all unbanked turn points and start the BUST feedback."""
    if game["phase"] != "settling":
        return
    game["phase"] = "bust"
    game["turn_score"] = 0
    animate_bust(0)


def animate_bust(frame):
    """Shake the BUST text briefly, then hold it before changing players."""
    if game["phase"] != "bust":
        return
    offsets = [0, -5, 4, -3, 2, -1, 0]
    ui["shake"] = offsets[frame]
    refresh_ui()
    if frame < len(offsets) - 1:
        schedule(35, animate_bust, frame + 1)
    else:
        schedule(1150, begin_transition)


def remember_hand():
    """Keep the last hand for display only, never for the next turn's scoring."""
    game["last_dice"] = game["dice"] + game["kept"]
    game["last_available"] = len(game["dice"])


def switch_player():
    """Change players and clear turn data while keeping both banked totals."""
    remember_hand()
    game["player"] = 1 - game["player"]
    game.update(turn_score=0, dice=[], kept=[], selected=[], phase="transition")


def begin_transition():
    if game["phase"] not in ("bust", "banking"):
        return
    switch_player()
    refresh_ui()
    schedule(650, finish_transition)


def finish_transition():
    if game["phase"] != "transition":
        return
    game["phase"] = "ready"
    game["message"] = player_name() + ", roll six dice to begin."
    refresh_ui()


def score_and_roll():
    """Add a valid selection to unbanked points and roll the remaining dice.

    If all six dice have scored, roll six fresh dice while keeping the
    entire turn subtotal at risk.
    """
    if ui["screen"] != "game" or game["phase"] != "selecting":
        return
    chosen = selected_dice()
    score = score_selection(chosen)
    if score == 0:
        return
    game["turn_score"] += score
    game["kept"].extend(chosen)
    remaining = len(game["dice"]) - len(chosen)
    notice = ""
    if remaining == 0:
        remaining = 6
        game["kept"] = []
        notice = "All six scored. Six fresh dice; your turn points are still at risk."
    roll_current(remaining, notice)


def score_and_end_turn():
    """Bank the turn subtotal plus a valid selection, ending the turn.

    Enter the banking phase before the delay so repeated clicks cannot
    add the same points again.
    """
    if ui["screen"] != "game" or game["phase"] != "selecting":
        return
    score = score_selection(selected_dice())
    if score == 0:
        return
    earned = game["turn_score"] + score
    game["scores"][game["player"]] += earned
    game.update(banked=earned, turn_score=0, selected=[], phase="banking")
    refresh_ui()
    schedule(850, finish_banking)


def finish_banking():
    """After banking feedback, check for victory or begin the next turn."""
    if game["phase"] != "banking":
        return
    if game["scores"][game["player"]] >= game["target"]:
        game["phase"] = "finished"
        ui["screen"] = "victory"
        refresh_ui()
    else:
        begin_transition()


def primary_action():
    if ui["screen"] != "game":
        return
    if game["phase"] == "ready":
        start_turn()
    elif game["phase"] == "selecting":
        score_and_roll()


def close_game():
    cancel_pending()
    ui["window"].destroy()


def build_ui():
    """Create the main window and connect GUI actions and keyboard callbacks."""
    window = tk.Tk()
    window.title("Tavern Dice")
    window.geometry("960x600")
    window.resizable(False, False)
    window.configure(bg=view.COLOURS["background"])
    ui.update(window=window, screen="menu", job=None, pending=None,
              generation=0, target_var=tk.StringVar(window, "4000"),
              entry=None, error="", frame=None, shake=0)
    ui["actions"] = {
        "play": show_setup, "rules": show_rules, "quit": close_game,
        "menu": show_menu, "request_menu": request_menu,
        "back": return_from_panel, "start": start_match,
        "preset": choose_preset, "die": on_die_click,
        "roll": primary_action, "bank": score_and_end_turn,
        "replay": play_again
    }
    view.build_canvas(ui)
    window.protocol("WM_DELETE_WINDOW", close_game)
    window.bind("<Escape>", escape_key)
    window.bind("<KeyPress>", number_key)
    show_menu()


if __name__ == "__main__":
    build_ui()
    ui["window"].mainloop()
