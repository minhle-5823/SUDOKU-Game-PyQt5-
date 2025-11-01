# 🧩 Sudoku Game  

> A classic Sudoku puzzle game built with **Python (PyQt5)** — featuring a sleek GUI, multiple difficulty levels, hint system, and a detailed interactive tutorial with slides.

---

## 🎯 Overview

**Sudoku Game** challenges players to fill a 9×9 grid so that:  
- Each **row**, **column**, and **3×3 box** contains all digits from **1 to 9**.  
- No number repeats within any row, column, or region.  

The project includes a **ranking system**, **scoring mechanics**, and a **visual How-to-Play section** designed for beginners.  
Built entirely with **Python** and **PyQt5**, this game runs fully offline.

---

## 📁 Project Structure

```plaintext
SudokuGame/
│
├── main.py                   # Main executable file
├── howtoplay.py              # How-to-Play page logic
│
├── assets/                   # Game assets and images
│   ├── background.png
│   ├── about_board.png
│   ├── announcement.png
│   ├── end_game.png
│   ├── gameplay_frame.png
│   ├── ranking_board.png
│   ├── slide_frame.png
│   ├── congrats.gif
│   ├── numbers/
│   │   ├── 1.png ... 9.png
│   │   └── empty.png
│   └── button/
│       ├── about.png
│       ├── easy.png
│       ├── medium.png
│       ├── hard.png
│       ├── how.png
│       ├── play.png
│       ├── quit.png
│       ├── arrow_back.png
│       ├── arrow_next.png
│       ├── short_empty.png
│       └── long_empty.png
│
├── players.json              # Stores player data
├── top10_ranking.txt         # Stores Top 10 player scores
└── README.md                 # Project documentation
```

## 🎮 MAIN FEATURES


# 1. PLAY MODE
-------------------
Players can select a difficulty level before starting.  
Each level has a different time limit, number of hints, and allowed mistakes:
+----------------------------------------+
| Level  | Time Limit | Hints | Mistakes |
|--------|-------------|-------|----------|
| Easy   | 15 minutes  | 5     | 5        |
| Medium | 20 minutes  | 3     | 3        |
| Hard   | 30 minutes  | 0     | 0        |
+----------------------------------------+

- Time: A countdown timer based on the selected level.  
  If time runs out before the puzzle is solved, the player loses.  
  Completing the puzzle early grants bonus points.
- Score: Starts at 0. Each correct cell adds +10 points.  
  The final score is multiplied by the level factor:
    + Easy ×1.0  
    + Medium ×1.5  
    + Hard ×2.0  
    + Bonus points are also granted depending on completion time.
- Hints: The maximum number of Hint uses allowed per level.  
  When Hints = 0, the player can no longer use this feature.
- Hint: Each time the Hint button is used, the remaining Hints decrease by 1,  
  and one random empty cell is automatically filled with the correct value.
- Reset: Generates a new Sudoku map for the current level and resets both time and score  
  (player data will not be saved).
- Main Menu: Returns to the main menu.  
  Players can save scores, continue playing, or reset to start a new puzzle.


# 2. RANKING BOARD
---------------------------------
Displays the Top 10 players with the highest scores.  
Data is loaded from the file "top10_ranking.txt".


# 3. HOW TO PLAY
---------------------------------
The tutorial is presented through 11 slides.  
Each slide includes two navigation buttons:
- "arrow_next.png" → go to the next slide.
- "arrow_back.png" → return to the previous slide.

4. ABOUT US
--------------------------
Provides information about the project team and the development process behind Sudoku Game.


5. QUIT
----------------------
Exits the game and closes the application.

## ⚙️ HOW TO RUN THE GAME (BASED ON ACTUAL CODE)

# 1. System Requirements
   - Python 3.8 or newer (recommended: 3.9+)
   - PyQt5 library installed

# 2. Install Required Library
   Open your terminal or command prompt and run:
   > pip install PyQt5

   (No additional libraries are needed since all logic, graphics, and gameplay are already implemented  
   within `main.py` and `howtoplay.py`.)

# 3. Prepare the Project Directory
   Make sure the `SudokuGame` folder contains all required files and assets  
   as shown in the project structure above.

- When the game is launched for the first time, if `players.json` or `top10_ranking.txt`  
  do not exist, they will be automatically created as empty files.
- The images in the `assets` folder are mandatory for the GUI to display properly.

# 4. Run the Game
- Open the terminal (CMD or PowerShell) in the folder containing `main.py`.
- Run the following command:
  > python main.py

  (Alternatively, open the project in Visual Studio Code or similar IDEs and click “Run”.  
  If it doesn’t run, make sure to add the correct workspace folder “SudokuGame” to your IDE.)

Once launched, the main menu window will appear with the following buttons:
- Play: Select level and start a new game.  
- Ranking: View the leaderboard.  
- How to Play: Open the 11-slide tutorial.  
- About Us: View information about the development team.  
- Quit: Exit the game.

# 5. Data Saving
- Whenever a player finishes a game or returns to the main menu,  
  their data is automatically saved to `players.json`.
- If a player achieves a new high score,  
  the top 10 leaderboard in `top10_ranking.txt` will update automatically.

# 6. Exiting the Game
- You can exit via the Quit button in the main menu or by pressing the ESC key.  
- While playing, pressing ESC opens a confirmation dialog (uses image `announcement.png`)  
  asking whether to save your current progress.

# 7. Platform Notes
- Windows: You can double-click `main.py` to run if Python is associated with `.py` files.  
- macOS/Linux: Run from the terminal using `python3 main.py`.  
- If you get a “missing PyQt5” error, ensure that Python was installed from the official  
  [python.org](https://www.python.org) source and re-run `pip install PyQt5`.

