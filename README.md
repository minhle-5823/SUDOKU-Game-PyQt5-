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
