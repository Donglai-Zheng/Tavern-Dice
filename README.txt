Project Title: Tavern Dice
Student: Donglai Zheng
Course: COMP9001 - Introduction to Programming
Tutorial: 18

PROJECT OVERVIEW
Tavern Dice is a local two-player dice game inspired by the dice minigame
in Kingdom Come: Deliverance II. Two players share one computer and take
turns choosing between rolling for more points and banking their turn score.
The game uses a simple medieval tavern style and runs offline.

REQUIREMENTS
- Python 3 with Tkinter and Tcl/Tk support, in a desktop environment.
- Tested on macOS. Windows has not been tested.
- No third-party packages, image downloads, API keys or internet connection
  are needed. Graphics are drawn in code using Tkinter Canvas.
- The window has a fixed 960 by 600 content area.

HOW TO RUN
Keep main.py, rules.py and view.py in the same folder. Open a terminal in
that folder and run main.py.

On the tested macOS setup:
    python3 main.py

On Windows, the usual command is:
    py main.py
If Python is installed without the py launcher, try:
    python main.py

If tkinter is missing, use a Python installation that includes Tcl/Tk support.
Run this desktop GUI application outside the Ed terminal environment.

HOW TO PLAY
1. Choose Play, then select a preset target or enter a whole number from
   1 to 999,999. Start Match rolls Player 1's first six dice automatically.
2. Click dice to select or deselect them. The selected score updates as you
   choose. Every selected die must score exactly once, using only dice from
   the current roll. An invalid selection shows 0 and cannot be confirmed.
3. Roll Again adds the selection to your unbanked turn points and rolls the
   remaining dice. Dim dice marked KEPT have already scored and cannot be
   selected again. If all six dice score, you may roll six fresh dice;
   all points earned during that turn remain at risk.
4. Bank Points adds both the turn points and current valid selection to
   your banked total and ends your turn.
5. If a roll has no scoring selection, BUST removes all unbanked points
   from that turn. Earlier banked totals stay safe. After the transition,
   the next player chooses Roll 6 Dice to begin.
6. The first player to bank at least the chosen target wins. Play Again
   starts a new match with the same target; Main Menu allows a new setup.

SCORING
- Single 1: 100 points. Single 5: 50 points.
- Three 1s: 1,000 points. Other triples: face value multiplied by 100.
- Each additional matching die doubles that group's score.
- Straights: 1-5 scores 500; 2-6 scores 750; 1-6 scores 1,500.
- Valid separate groups can be combined without counting any die twice.
  For example, 1115 scores 1,050 and 123455 scores 550.

CONTROLS AND NOTES
Click dice or use keys 1-6 to select their current positions. Tab moves
through buttons; Enter or Space activates the focused button. Esc goes
back or opens the leave-match confirmation during play.
Rules opens the scoring guide. Rules and leave confirmation pause any
animation until you return. Leaving a match or closing the program clears
its progress; there is no save file.

FILE STRUCTURE
main.py             Starts the program and manages players, game state,
                    navigation, scoring actions and animation timing.
rules.py            Generates dice rolls and calculates valid scores.
view.py             Draws screens and dice, and handles Canvas interaction.
README.txt          Project overview, requirements and playing instructions.
AI_DECLARATION.txt  Student contributions and AI assistance by file.
