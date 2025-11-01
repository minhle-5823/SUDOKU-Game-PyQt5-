# main.py
"""
Sudoku Game - single-file, fixed-center board artwork
Requirements:
- assets/background.png
- assets/board.png
- assets/button/*.png (about, play, easy, medium, hard, how, ranking, quit, short_empty.png, long_empty.png)
- assets/numbers/1.png ... 9.png and empty.png (optional)
- assets/gameplay_frame.png (used as board art)
- assets/announcement.png (NEW)
- assets/end_game.png (NEW)
- assets/ranking_board.png (NEW)
- assets/congrats.gif (NEW)
"""
import sys
import os
import json
import time
import random
import copy
from typing import Optional, Tuple, List, Dict, Any

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QLabel, QGraphicsDropShadowEffect, QDialog, QVBoxLayout, QPushButton, QHBoxLayout, QTextEdit

# ---------------------------
# Paths / Config
# ---------------------------
BASE_DIR = os.path.dirname(__file__)
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
BUTTON_DIR = os.path.join(ASSETS_DIR, "button")
NUM_DIR = os.path.join(ASSETS_DIR, "numbers")
PLAYER_DATA_JSON = os.path.join(BASE_DIR, "players.json") # File lưu data chi tiết người chơi
TOP10_RANKING_TXT = os.path.join(BASE_DIR, "top10_ranking.txt") # File lưu Top 10 ranking
BOARD_IMG = os.path.join(ASSETS_DIR, "board.png") # Dùng làm fallback hoặc nền
FRAME_IMG = os.path.join(ASSETS_DIR, "gameplay_frame.png")
BG_IMG = os.path.join(ASSETS_DIR, "background.png")
ANNOUNCEMENT_IMG = os.path.join(ASSETS_DIR, "announcement.png") # Khung thông báo xác nhận
END_GAME_IMG = os.path.join(ASSETS_DIR, "end_game.png") # Khung kết thúc game
RANKING_BOARD_IMG = os.path.join(ASSETS_DIR, "ranking_board.png") # Khung Ranking
ABOUT_BOARD_IMG = os.path.join(ASSETS_DIR, "about_board.png") # Khung About us
CONGRATS_GIF = os.path.join(ASSETS_DIR, "congrats.gif") # Gif nổ pháo hoa
SHORT_EMPTY = os.path.join(BUTTON_DIR, "short_empty.png")
LONG_EMPTY = os.path.join(BUTTON_DIR, "long_empty.png")

os.makedirs(ASSETS_DIR, exist_ok=True)
os.makedirs(BUTTON_DIR, exist_ok=True)
os.makedirs(NUM_DIR, exist_ok=True)
if not os.path.exists(PLAYER_DATA_JSON):
    with open(PLAYER_DATA_JSON, "w", encoding="utf-8") as f:
        json.dump({"Easy": [], "Medium": [], "Hard": []}, f)
if not os.path.exists(TOP10_RANKING_TXT):
     with open(TOP10_RANKING_TXT, "w", encoding="utf-8") as f:
        f.write("\nNo rankings yet.") # Thêm dòng trống cho đúng format

# ---------------------------
# Sudoku logic (giữ nguyên)
# ---------------------------
def is_valid(grid: List[List[int]], row: int, col: int, num: int) -> bool:
    for i in range(9):
        if grid[row][i] == num or grid[i][col] == num:
            return False
    sr, sc = row - row % 3, col - col % 3
    for i in range(3):
        for j in range(3):
            if grid[sr + i][sc + j] == num:
                return False
    return True

def solve_sudoku(grid: List[List[int]]) -> bool:
    for r in range(9):
        for c in range(9):
            if grid[r][c] == 0:
                for n in random.sample(range(1, 10), 9):
                    if is_valid(grid, r, c, n):
                        grid[r][c] = n
                        if solve_sudoku(grid):
                            return True
                        grid[r][c] = 0
                return False
    return True

def generate_solution() -> List[List[int]]:
    g = [[0] * 9 for _ in range(9)]
    solve_sudoku(g)
    return g

def count_solutions(grid, count=0):
    if count > 1:
        return 2
    
    for r in range(9):
        for c in range(9):
            if grid[r][c] == 0:
                for n in range(1, 10):
                    if is_valid(grid, r, c, n):
                        grid[r][c] = n
                        count = count_solutions(grid, count)
                        grid[r][c] = 0
                        if count > 1:
                            return 2
                return count
    return count + 1

def is_valid_puzzle(puzzle):
    # Kiểm tra hàng
    for i in range(9):
        if all(puzzle[i][j] == 0 for j in range(9)):
            return False
    # Kiểm tra cột
    for j in range(9):
        if all(puzzle[i][j] == 0 for i in range(9)):
            return False
    # Kiểm tra khối 3x3
    for br in range(0, 9, 3):
        for bc in range(0, 9, 3):
            if all(puzzle[i][j] == 0 for i in range(br, br+3) for j in range(bc, bc+3)):
                return False
    return True
    
def generate_puzzle(level: str):
    MAX_RETRIES = 5
    for attempt in range(MAX_RETRIES):
        solution = generate_solution()
        puzzle = copy.deepcopy(solution)
        
        if level.lower() == "easy":
            cells_to_remove = 43 
        elif level.lower() == "medium":
            cells_to_remove = 45 
        else:  # Hard
            cells_to_remove = 51 
        
        all_cells = [(r, c) for r in range(9) for c in range(9)]
        random.shuffle(all_cells)
        
        removed = 0
        temp_puzzle_state = copy.deepcopy(solution) 

        for r, c in all_cells:
            if removed >= cells_to_remove:
                break
                
            if temp_puzzle_state[r][c] == 0:
                continue
                
            backup = temp_puzzle_state[r][c]
            temp_puzzle_state[r][c] = 0
            
            temp_check_puzzle = copy.deepcopy(temp_puzzle_state)
            solution_count = count_solutions(temp_check_puzzle)
            valid = is_valid_puzzle(temp_puzzle_state)
            
            if solution_count == 1 and valid:
                removed += 1
            else:
                temp_puzzle_state[r][c] = backup
        
        puzzle = temp_puzzle_state 
        
        # Final conditions checks
        row_condition_met = True
        for i in range(9):
            if all(puzzle[i][j] != 0 for j in range(9)):
                row_condition_met = False
                break
        
        col_condition_met = True
        if row_condition_met:
            for j in range(9):
                if all(puzzle[i][j] != 0 for i in range(9)):
                    col_condition_met = False
                    break
        
        block_condition_met = True
        for br in range(0, 9, 3):
            for bc in range(0, 9, 3):
                removed_in_block = sum(1 for r in range(br, br+3) 
                                         for c in range(bc, bc+3) 
                                         if puzzle[r][c] == 0)
                                         
                if removed_in_block < 2:
                    block_condition_met = False
                    break
            if not block_condition_met:
                break
        
        if is_valid_puzzle(puzzle) and row_condition_met and col_condition_met and block_condition_met:
            return {"grid": puzzle, "solution": solution}
            
    return {"grid": puzzle, "solution": solution}


# ---------------------------
# Helpers
# ---------------------------
def load_pix(path: str) -> Optional[QtGui.QPixmap]:
    if path and os.path.exists(path):
        return QtGui.QPixmap(path)
    return None

# ---------------------------
# Custom Dialog (Frameless/Translucent)
# ---------------------------
class CustomDialog(QDialog):
    def __init__(self, parent: QtWidgets.QWidget, title: str, content: str, buttons: List[Tuple[str, Any]], background_img: str, content_v_padding: Tuple[int, int] = (80, 40)):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedSize(650, 600) 
        
        # YÊU CẦU: Bỏ khung trắng ngoài (Frameless)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint) 
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self._bg_pix = load_pix(background_img)

        # Layout chính
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Widget chứa nội dung
        content_widget = QtWidgets.QWidget(self)
        content_widget.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        # Layout nội dung (căn giữa)
        content_layout = QVBoxLayout(content_widget)
        content_layout.setAlignment(QtCore.Qt.AlignCenter)
        content_layout.setSpacing(10)
        # Căn chỉnh để tránh đè lên khung ảnh
        content_layout.setContentsMargins(30, content_v_padding[0], 30, content_v_padding[1]) 

        # Tiêu đề
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("font-size: 28px; font-weight: bold; color: #5a0099;")
        self.title_label.setAlignment(QtCore.Qt.AlignCenter)
        content_layout.addWidget(self.title_label)
        
        # Nội dung
        self.content_label = QLabel(content)
        # Sử dụng multi-line text alignment
        self.content_label.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignTop) 
        self.content_label.setStyleSheet("font-size: 16px; color: black;")
        content_layout.addWidget(self.content_label)
        
        content_layout.addSpacing(20)

        # Vùng nút
        button_layout = QHBoxLayout()
        button_layout.setAlignment(QtCore.Qt.AlignCenter)
        
        self.results = {}
        for btn_text, result_key in buttons:
            btn = QPushButton(btn_text)
            btn.setFixedSize(120, 36)
            # YÊU CẦU: Sử dụng short_empty.png cho nút
            btn.setStyleSheet(
                f'border-image: url("{SHORT_EMPTY.replace(os.sep, "/")}");'
                'color:white; font-weight:700; font-size:14px;'
            )
            btn.clicked.connect(lambda _, key=result_key: self.accept_with_result(key))
            button_layout.addWidget(btn)

        content_layout.addLayout(button_layout)
        
        main_layout.addWidget(content_widget)
        
        # GIF Overlay (Chỉ dùng cho End Game)
        self.gif_label = QLabel(self)
        self.gif_label.setGeometry(0, 0, self.width(), self.height())
        self.gif_label.setAlignment(QtCore.Qt.AlignCenter)
        self.gif_label.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        self.gif_label.setVisible(False)
        self.gif_movie = QtGui.QMovie(CONGRATS_GIF)
        self.gif_label.setMovie(self.gif_movie)
        
    def paintEvent(self, event):
        qp = QtGui.QPainter(self)
        qp.setRenderHint(QtGui.QPainter.Antialiasing)
        if self._bg_pix:
            # Vẽ hình nền (duy nhất)
            qp.drawPixmap(self.rect(), self._bg_pix.scaled(self.size(), QtCore.Qt.IgnoreAspectRatio, QtCore.Qt.SmoothTransformation))
        # Không gọi super().paintEvent(event) để đảm bảo không có khung QDialog mặc định

    def accept_with_result(self, result_key: Any):
        self.results['result'] = result_key
        self.accept()

    def play_gif(self, duration_ms: int = 2000):
        if self.gif_movie.isValid():
            self.gif_movie.setScaledSize(self.size()) 
            self.gif_label.setGeometry(0, 0, self.width(), self.height())
            self.gif_label.setVisible(True)
            self.gif_movie.start()
            
            QtCore.QTimer.singleShot(duration_ms, self.stop_gif)

    def stop_gif(self):
        self.gif_movie.stop()
        self.gif_label.setVisible(False)

# ---------------------------
# BoardWidget
# ---------------------------
class BoardWidget(QtWidgets.QWidget):
    cell_clicked = QtCore.pyqtSignal(int, int)
    number_clicked = QtCore.pyqtSignal(int)

    def __init__(self, parent, grid: List[List[int]], solution: List[List[int]], player_name: str, level: str, last_score: int):
        super().__init__(parent)
        self.grid0 = [row[:] for row in grid]
        self.grid = [row[:] for row in grid]
        self.solution = solution
        self.selected = (None, None)
        self.hover = (None, None)
        self.wrong_cells = set()
        self.revealed = set()
        
        self.player_name = player_name
        self.level = level
        self.last_score = last_score # Last Score

        self.board_pix = load_pix(FRAME_IMG)
        self.num_pix = {}
        for n in range(1, 10):
            p = load_pix(os.path.join(NUM_DIR, f"{n}.png"))
            if p:
                self.num_pix[n] = p
        self.empty_pix = load_pix(os.path.join(NUM_DIR, "empty.png"))

        self.grid_inset_frac = 0.12
        self.number_pad_width_frac = 0.105
        self.setMouseTracking(True)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        self._board_rect = QtCore.QRect()
        self._grid_rect = QtCore.QRect()
        self._number_pad_rect = QtCore.QRect()
        self._cell_size = 0.0
        self._number_cell_size = 0.0

    def sizeHint(self):
        if self.board_pix:
            return self.board_pix.size()
        return QtCore.QSize(420, 420)

    def paintEvent(self, event):
        qp = QtGui.QPainter(self)
        qp.setRenderHint(QtGui.QPainter.Antialiasing)

        W, H = self.width(), self.height()
        # draw board image 
        if self.board_pix:
            bw, bh = self.board_pix.width(), self.board_pix.height()
            scale = min(W / bw, H / bh, 1.0)
            disp_w, disp_h = int(bw * scale), int(bh * scale)
            bx = (W - disp_w) // 2
            by = (H - disp_h) // 2
            board_rect = QtCore.QRect(bx, by, disp_w, disp_h)
            qp.drawPixmap(board_rect, self.board_pix.scaled(disp_w, disp_h, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        else:
            side = int(min(W, H) * 0.8)
            bx = (W - side) // 2
            by = (H - side) // 2
            board_rect = QtCore.QRect(bx, by, side, side)
            qp.setBrush(QtGui.QColor(50, 50, 50))
            qp.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0), 2))
            qp.drawRoundedRect(board_rect, 10, 10)

        # inner grid rect (square) by insetting board_rect
        inset_x = int(board_rect.width() * self.grid_inset_frac)
        inset_y = int(board_rect.height() * self.grid_inset_frac)
        grid_rect = QtCore.QRect(board_rect.left() + inset_x,
                                board_rect.top() + inset_y,
                                board_rect.width() - inset_x * 2,
                                board_rect.height() - inset_y * 2)
        gs = min(grid_rect.width(), grid_rect.height())
        grid_rect = QtCore.QRect(
            board_rect.left() + (board_rect.width() - gs) // 2,
            board_rect.top() + (board_rect.height() - gs) // 2,
            gs, gs
        )
        cs = grid_rect.width() / 9.0
        
        COLOR_HOVER_RC = QtGui.QColor(120, 255, 120, 60)
        COLOR_HOVER_BLOCK = QtGui.QColor(120, 255, 120, 60)
        COLOR_SELECTED_CELL = QtGui.QColor(110, 200, 120, 120)
        COLOR_SAME_VALUE = QtGui.QColor(0, 120, 255, 120)

        # Draw Player Info on the TOP side of the grid (3 lines)
        player_info_height = int(grid_rect.height() * 0.12) 
        player_info_rect = QtCore.QRect(
            grid_rect.left(),
            grid_rect.top() - player_info_height - 15,  
            grid_rect.width(),
            player_info_height
        )

        f = qp.font()
        f.setPixelSize(max(14, int(player_info_height * 0.2))) 
        f.setBold(True)
        f.setWeight(QtGui.QFont.Bold)
        qp.setFont(f)

        line_height = player_info_rect.height() // 3
        text_color = QtGui.QColor(0, 0, 0)
        
        qp.setPen(QtGui.QPen(text_color, 2))
        
        # Dòng 1: Player Name
        qp.drawText(player_info_rect.left(), player_info_rect.top() + line_height - 2, 
                    f"Player: {self.player_name}")
        # Dòng 2: Level
        qp.drawText(player_info_rect.left(), player_info_rect.top() + line_height * 2 - 2, 
                    f"Level: {self.level}")
        # Dòng 3: Last Score (YÊU CẦU: Last Score nằm dưới Level)
        qp.drawText(player_info_rect.left(), player_info_rect.top() + line_height * 3 - 2, 
                    f"Last Score: {self.last_score}")

        # Highlight các ô có cùng giá trị với ô được chọn
        sr, sc = self.selected
        if sr is not None and sc is not None:
            selected_value = self.grid[sr][sc]
            if selected_value != 0:
                qp.setPen(QtCore.Qt.NoPen)
                qp.setBrush(COLOR_SAME_VALUE)
                for r in range(9):
                    for c in range(9):
                        if self.grid[r][c] == selected_value and (r, c) != (sr, sc):
                            qp.drawRect(int(grid_rect.left() + c * cs), 
                                    int(grid_rect.top() + r * cs), 
                                    int(cs), int(cs))

        # hover highlight (row & col & block)
        hr, hc = self.hover
        if hr is not None and hc is not None:
            qp.setPen(QtCore.Qt.NoPen)
            
            # Highlight khối 3x3
            qp.setBrush(COLOR_HOVER_BLOCK)
            sr, sc = hr - hr % 3, hc - hc % 3
            block_rect = QtCore.QRect(
                grid_rect.left() + int(sc * cs),
                grid_rect.top() + int(sr * cs),
                int(cs * 3),
                int(cs * 3)
            )
            qp.drawRect(block_rect)
            
            # Highlight hàng
            qp.setBrush(COLOR_HOVER_RC)
            qp.drawRect(grid_rect.left(), int(grid_rect.top() + hr * cs), grid_rect.width(), int(cs))
            # Highlight cột
            qp.drawRect(int(grid_rect.left() + hc * cs), grid_rect.top(), int(cs), grid_rect.height())

        # selected cell highlight (stronger)
        sr, sc = self.selected
        if sr is not None and sc is not None:
            qp.setPen(QtCore.Qt.NoPen)
            qp.setBrush(COLOR_SELECTED_CELL)
            qp.drawRect(int(grid_rect.left() + sc * cs), int(grid_rect.top() + sr * cs), int(cs), int(cs))

        # subtle grid lines
        qp.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0, 50), 1))
        for i in range(10):
            y = grid_rect.top() + int(i * cs)
            qp.drawLine(grid_rect.left(), y, grid_rect.right(), y)
        for j in range(10):
            x = grid_rect.left() + int(j * cs)
            qp.drawLine(x, grid_rect.top(), x, grid_rect.bottom())

        # 3x3 separators thicker
        qp.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0, 160), 2))
        for i in range(0, 10, 3):
            y = grid_rect.top() + int(i * cs)
            qp.drawLine(grid_rect.left(), y, grid_rect.right(), y)
        for j in range(0, 10, 3):
            x = grid_rect.left() + int(j * cs)
            qp.drawLine(x, grid_rect.top(), x, grid_rect.bottom())

        # draw numbers 
        for r in range(9):
            for c in range(9):
                v = self.grid[r][c]
                if v == 0:
                    continue
                cell_x = grid_rect.left() + int(c * cs)
                cell_y = grid_rect.top() + int(r * cs)
                rect = QtCore.QRect(cell_x, cell_y, int(cs), int(cs))
                if v in self.num_pix:
                    pix = self.num_pix[v]
                    target = pix.scaled(int(cs * 0.85), int(cs * 0.85), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
                    qp.drawPixmap(rect.left() + (rect.width() - target.width()) // 2,
                                rect.top() + (rect.height() - target.height()) // 2,
                                target)
                else:
                    f = qp.font()
                    f.setPixelSize(max(10, int(cs * 0.55)))
                    qp.setFont(f)
                    if self.grid0[r][c] != 0:
                        qp.setPen(QtGui.QPen(QtGui.QColor(30, 30, 30)))
                    else:
                        qp.setPen(QtGui.QPen(QtGui.QColor(0, 70, 160))) 
                    qp.drawText(rect, QtCore.Qt.AlignCenter, str(v))

                # Viền đỏ cho ô sai (nếu có)
                if (r, c) in self.wrong_cells:
                    qp.setPen(QtGui.QPen(QtGui.QColor(255, 0, 0), 3))  # Viền đỏ, độ dày 3
                    qp.setBrush(QtCore.Qt.NoBrush)
                    qp.drawRect(rect)

        # Draw number pad on the RIGHT side of the grid
        number_pad_width = int(grid_rect.width() * self.number_pad_width_frac)
        number_pad_rect = QtCore.QRect(
            grid_rect.right() + 40,
            grid_rect.top(),
            number_pad_width,
            grid_rect.height()
        )
        
        qp.setPen(QtCore.Qt.NoPen)
        qp.setBrush(QtGui.QColor(240, 240, 240, 200))
        qp.drawRoundedRect(number_pad_rect, 5, 5)
        
        ncs = number_pad_rect.height() / 9.0
        for i in range(9):
            num = i + 1
            cell_rect = QtCore.QRect(
                number_pad_rect.left(),
                number_pad_rect.top() + int(i * ncs),
                number_pad_rect.width(),
                int(ncs)
            )
            
            qp.setPen(QtGui.QPen(QtGui.QColor(100, 100, 100), 1))
            qp.setBrush(QtGui.QColor(255, 255, 255, 230))
            qp.drawRect(cell_rect)
            
            if num in self.num_pix:
                pix = self.num_pix[num]
                target = pix.scaled(int(number_pad_rect.width() * 0.85), int(ncs * 0.85), 
                                  QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
                qp.drawPixmap(cell_rect.left() + (cell_rect.width() - target.width()) // 2,
                            cell_rect.top() + (cell_rect.height() - target.height()) // 2,
                            target)
            else:
                f = qp.font()
                f.setPixelSize(max(12, int(ncs * 0.6)))
                qp.setFont(f)
                qp.setPen(QtGui.QPen(QtGui.QColor(30, 30, 30)))
                qp.drawText(cell_rect, QtCore.Qt.AlignCenter, str(num))

        self._board_rect = board_rect
        self._grid_rect = grid_rect
        self._number_pad_rect = number_pad_rect
        self._cell_size = cs
        self._number_cell_size = ncs

    # ... (các hàm còn lại của BoardWidget giữ nguyên)
    def pos_to_cell(self, pos: QtCore.QPoint) -> Tuple[Optional[int], Optional[int]]:
        if not self._grid_rect or self._cell_size == 0:
            return None, None
        x = pos.x() - self._grid_rect.left()
        y = pos.y() - self._grid_rect.top()
        if x < 0 or y < 0 or x >= self._grid_rect.width() or y >= self._grid_rect.height():
            return None, None
        c = int(x // self._cell_size)
        r = int(y // self._cell_size)
        if 0 <= r < 9 and 0 <= c < 9:
            return r, c
        return None, None

    def pos_to_number(self, pos: QtCore.QPoint) -> Optional[int]:
        if not self._number_pad_rect or self._number_cell_size == 0:
            return None
        x = pos.x() - self._number_pad_rect.left()
        y = pos.y() - self._number_pad_rect.top()
        if x < 0 or y < 0 or x >= self._number_pad_rect.width() or y >= self._number_pad_rect.height():
            return None
        idx = int(y // self._number_cell_size)
        if 0 <= idx < 9:
            return idx + 1
        return None

    def mouseMoveEvent(self, event):
        r, c = self.pos_to_cell(event.pos())
        if (r, c) != self.hover:
            self.hover = (r, c)
            self.update()

    def leaveEvent(self, event):
        if self.hover != (None, None):
            self.hover = (None, None)
            self.update()

    def mousePressEvent(self, event):
        number = self.pos_to_number(event.pos())
        if number is not None:
            self.number_clicked.emit(number)
            return
            
        r, c = self.pos_to_cell(event.pos())
        if r is not None:
            self.selected = (r, c)
            self.cell_clicked.emit(r, c)
        else:
            self.selected = (None, None)
        self.update()

    def is_fixed(self, r: int, c: int) -> bool:
        return self.grid0[r][c] != 0

    def set_value(self, r: int, c: int, val: int, correct: bool = True, revealed: bool = False):
        self.grid[r][c] = val
        if not correct:
            self.wrong_cells.add((r, c))
            QtCore.QTimer.singleShot(700, lambda: (self.wrong_cells.discard((r, c)), self.update()))
        if revealed:
            self.revealed.add((r, c))
        self.update()

    def is_solved(self) -> bool:
        for r in range(9):
            for c in range(9):
                if self.grid[r][c] != self.solution[r][c]:
                    return False
        return True

    def get_random_empty_cell(self):
        empties = [(r, c) for r in range(9) for c in range(9) if self.grid[r][c] == 0]
        return random.choice(empties) if empties else None
# ---------------------------
# LabelWithBg: HUD boxes (Giữ nguyên)
# ---------------------------
class LabelWithBg(QtWidgets.QLabel):
    def __init__(self, pix_path: Optional[str], text: str = "", parent=None):
        super().__init__(text, parent)
        self.pix = load_pix(pix_path) if pix_path else None
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setMinimumHeight(44)
        self.setStyleSheet("font-size: 18px; font-weight:600; color: white;")
    def paintEvent(self, ev):
        qp = QtGui.QPainter(self)
        qp.setRenderHint(QtGui.QPainter.SmoothPixmapTransform)
        if self.pix:
            qp.drawPixmap(self.rect(), self.pix.scaled(self.size(), QtCore.Qt.KeepAspectRatioByExpanding, QtCore.Qt.SmoothTransformation))
        super().paintEvent(ev)

# ---------------------------
# Main Window 
# ---------------------------
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sudoku - Pro")
        self.resize(1200, 740)

        central = QtWidgets.QWidget()
        self.setCentralWidget(central)

        self.bg_label = QtWidgets.QLabel(central)
        self.bg_label.setGeometry(0, 0, self.width(), self.height())
        self.bg_label.setScaledContents(True)
        if os.path.exists(BG_IMG):
            self.bg_label.setPixmap(load_pix(BG_IMG))
        else:
            self.bg_label.setStyleSheet("background-color: #0a0a0a;")

        self.ui_overlay = QtWidgets.QWidget(central)
        self.ui_overlay.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.ui_overlay.setGeometry(0, 0, self.width(), self.height())

        self.main_layout = QtWidgets.QVBoxLayout(self.ui_overlay)
        self.main_layout.setContentsMargins(18, 18, 18, 18)

        self.msg = QtWidgets.QLabel("")
        self.msg.setAlignment(QtCore.Qt.AlignCenter)
        self.msg.setStyleSheet("color: white; font-weight:600;")
        self.main_layout.addWidget(self.msg)

        self.stack = QtWidgets.QStackedWidget()
        self.main_layout.addWidget(self.stack, 1)

        self.pages = {}
        self._create_pages()
        self.goto("main_menu")

        self._last_score_fetched = 0 
        self._current_puzzle = None 

    def resizeEvent(self, ev):
        self.bg_label.setGeometry(0, 0, self.width(), self.height())
        self.ui_overlay.setGeometry(0, 0, self.width(), self.height())
        if self.bg_label.pixmap():
            self.bg_label.setPixmap(load_pix(BG_IMG).scaled(self.bg_label.size(), QtCore.Qt.KeepAspectRatioByExpanding, QtCore.Qt.SmoothTransformation))
        super().resizeEvent(ev)

    def keyPressEvent(self, event):
        key = event.key()
        if QtCore.Qt.Key_1 <= key <= QtCore.Qt.Key_9:
            num = key - QtCore.Qt.Key_0
            gw = self.pages.get("game", None)
            if gw and self.stack.currentWidget() == gw:
                board: BoardWidget = gw._board
                self._on_number_click(board, num)
        elif key == QtCore.Qt.Key_Escape:
            gw = self.pages.get("game", None)
            if gw and self.stack.currentWidget() == gw:
                self._back_to_main_menu(gw)
            else:
                 self.goto("main_menu")
        else:
            super().keyPressEvent(event)

    def _back_to_main_menu(self, gw):
        # Dừng timer TẠM THỜI
        if hasattr(gw, "_timer"):
            gw._timer.stop()
            
        # YÊU CẦU: Hỏi xác nhận bằng tiếng Anh
        dialog = CustomDialog(
            parent=self, 
            title="Confirm Exit", 
            content="Do you want to exit and save the current score?",
            buttons=[("Yes", True), ("No", False)], 
            background_img=ANNOUNCEMENT_IMG
        )
        
        if dialog.exec_() == QDialog.Accepted:
            result = dialog.results.get('result')
            
            if result is True:
                # Yes: Hiện bảng kết thúc sớm (end_game.png)
                time_spent = int(time.time() - gw._start_time) - (gw._countdown if gw._countdown is not None else 0)
                time_spent = max(0, time_spent)
                
                # SỬA LỖI: Gọi đúng hàm _handle_end_game_dialog và truyền thêm 2 tham số
                self._handle_end_game_dialog(
                    player_name=gw._player, 
                    score=gw._score, 
                    level=gw._level, 
                    time_spent=time_spent, 
                    is_completed=False, # Kết thúc sớm
                    last_score=self._last_score_fetched,
                    title="You almost had it!", # Thêm tham số
                    content_prefix="Better try next time!" # Thêm tham số
                )
            else:
                # No: Quay lại game và tiếp tục timer
                if hasattr(gw, "_timer"):
                    gw._timer.start()
        else:
            # Nếu dialog bị đóng (Esc): Tiếp tục game
            if hasattr(gw, "_timer"):
                gw._timer.start()


    def _create_pages(self):
        self.pages["main_menu"] = self._page_main_menu()
        self.stack.addWidget(self.pages["main_menu"])
        self.pages["level_select"] = self._page_level_select()
        self.stack.addWidget(self.pages["level_select"])
        self.pages["player_setup"] = self._page_player_setup()
        self.stack.addWidget(self.pages["player_setup"])
        self.pages["ranking"] = self._page_ranking()
        self.stack.addWidget(self.pages["ranking"])
        self.pages["howto"] = self._page_howto()
        self.stack.addWidget(self.pages["howto"])
        self.pages["about"] = self._page_about()
        self.stack.addWidget(self.pages["about"])

    # pages (giữ nguyên, trừ _page_ranking)
    def _page_main_menu(self):
        w = QtWidgets.QWidget()
        lay = QtWidgets.QVBoxLayout(w)
        lay.setAlignment(QtCore.Qt.AlignCenter)
        title = QtWidgets.QLabel("MAIN MENU\n") 
        title.setStyleSheet("font-size:45px; font-weight:800; color: black;")
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(0)
        shadow.setColor(QColor("purple"))
        shadow.setOffset(2, 3)
        title.setGraphicsEffect(shadow)
        title.setAlignment(QtCore.Qt.AlignCenter) 
        lay.addWidget(title)
        btns = [
            ("", os.path.join(BUTTON_DIR, "play.png"), lambda: self.goto("level_select")),
            ("", os.path.join(BUTTON_DIR, "ranking.png"), lambda: self.goto("ranking")),
            ("", os.path.join(BUTTON_DIR, "how.png"), lambda: self.goto("howto")),
            ("", os.path.join(BUTTON_DIR, "about.png"), lambda: self.goto("about")),
            ("", os.path.join(BUTTON_DIR, "quit.png"), lambda: QtWidgets.qApp.quit())
        ]
        for text, img, cb in btns:
            btn = QtWidgets.QPushButton(text)
            btn.setFixedWidth(300)
            if os.path.exists(img):
                btn.setStyleSheet(f"border-image: url('{img.replace(os.sep, '/')}'); color: white; font-weight:700; height:70px;")
            else:
                btn.setStyleSheet('background:#2f86e6; color:white; font-weight:700; height:70px;')
            btn.clicked.connect(cb)
            lay.addWidget(btn)
        return w

    def _page_level_select(self):
        w = QtWidgets.QWidget()
        lay = QtWidgets.QVBoxLayout(w)
        lay.setAlignment(QtCore.Qt.AlignCenter)
        
        title = QtWidgets.QLabel("Select Difficulty")
        title.setStyleSheet("font-size:25px; font-weight:800; color: black;")
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(0)
        shadow.setColor(QColor("purple"))
        shadow.setOffset(1, 1)
        title.setGraphicsEffect(shadow)
        title.setAlignment(QtCore.Qt.AlignCenter) 
        lay.addWidget(title)
        lay.addSpacing(20)
        
        levels = ["easy", "medium", "hard"]
        for lvl in levels:
            img_path = os.path.join(BUTTON_DIR, f"{lvl}.png")
            btn = QtWidgets.QPushButton()
            btn.setFixedSize(220, 44)
            if os.path.exists(img_path):
                btn.setStyleSheet(
                    f'border-image: url("{img_path.replace(os.sep, "/")}");'
                    'color: white; font-weight:700;'
                )
            else:
                btn.setStyleSheet(
                    "background:#2f86e6; color:white; font-weight:700;"
                )
            btn.clicked.connect(lambda _, l=lvl: self._open_player_setup(l))
            lay.addWidget(btn)
            lay.addSpacing(10)
        
        back = QtWidgets.QPushButton("Back")
        back.setFixedSize(120, 36)
        back.setStyleSheet(
            f'border-image: url("{SHORT_EMPTY.replace(os.sep, "/")}");'
            'color:white; font-weight:700; font-size:14px;'
        )
        back.clicked.connect(lambda: self.goto("main_menu"))
        lay.addSpacing(15)
        lay.addWidget(back, alignment=QtCore.Qt.AlignCenter)

        return w


    def _page_player_setup(self):
        w = QtWidgets.QWidget()
        lay = QtWidgets.QVBoxLayout(w)
        lay.setAlignment(QtCore.Qt.AlignCenter)
        t = QtWidgets.QLabel("Enter Player Name")
        t.setStyleSheet("font-size:22px; font-weight:800; color: black;")
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(0)
        shadow.setColor(QColor("purple"))
        shadow.setOffset(1, 1)
        t.setGraphicsEffect(shadow)
        t.setAlignment(QtCore.Qt.AlignCenter)
        lay.addWidget(t)

        self.name_edit = QtWidgets.QLineEdit()
        self.name_edit.setFixedSize(340, 50)
        self.name_edit.setStyleSheet("""
            QLineEdit {
                font-size: 18px;
                font-weight: 600;
                padding: 8px 12px;
                border: 2px solid #2f86e6;
                border-radius: 8px;
                background-color: white;
                color: black;
            }
            QLineEdit:focus {
                border-color: #1e5fb0;
                background-color: #f0f8ff;
            }
        """)
        lay.addWidget(self.name_edit)
        
        self.name_msg_label = QLabel("")
        self.name_msg_label.setStyleSheet("color: red; font-size: 14px; font-weight: bold;")
        self.name_msg_label.setAlignment(QtCore.Qt.AlignCenter)
        lay.addWidget(self.name_msg_label)

        hl = QtWidgets.QHBoxLayout()
        btn_back = QtWidgets.QPushButton("Back")
        btn_back.setFixedSize(120, 36)
        btn_back.setStyleSheet(
            f'border-image: url("{SHORT_EMPTY.replace(os.sep, "/")}");'
            'color:white; font-weight:700; font-size:14px;'
        )
        btn_back.clicked.connect(lambda: self.goto("level_select"))
        hl.addWidget(btn_back)

        btn_start = QtWidgets.QPushButton("Start Game")
        btn_start.setFixedSize(160, 36)
        btn_start.setStyleSheet(
            f'border-image: url("{SHORT_EMPTY.replace(os.sep, "/")}");'
            'color:white; font-weight:700; font-size:14px;'
        )
        btn_start.clicked.connect(lambda: self._check_player_name(self.name_edit.text().strip(), self._pending_level))
        hl.addWidget(btn_start)

        self.name_edit.returnPressed.connect(lambda: self._check_player_name(self.name_edit.text().strip(), self._pending_level))

        lay.addLayout(hl)
        return w


    def _page_ranking(self):
        w = QtWidgets.QWidget()
        lay = QtWidgets.QVBoxLayout(w)
        lay.setAlignment(QtCore.Qt.AlignCenter)
        
        # Ranking board uses ranking_board.png
        bg_label = QLabel(w)
        bg_pix = load_pix(RANKING_BOARD_IMG)
        
        if bg_pix:
            # Use a size proportional to the game board (~420x420 pixels)
            target_width = 800  # Match game board’s minimum size
            target_height = 800  # Adjust if needed
            original_size = bg_pix.size()
            # Calculate scale factor to fit target_width while preserving aspect ratio
            scale_factor = min(target_width / original_size.width(), target_height / original_size.height())
            scaled_size = QtCore.QSize(int(original_size.width() * scale_factor), 
                                    int(original_size.height() * scale_factor))
            bg_label.setFixedSize(scaled_size)
            scaled_pix = bg_pix.scaled(scaled_size, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            bg_label.setPixmap(scaled_pix)
            content_lay = QVBoxLayout(bg_label)
            # Adjust margins to align with ranking_board.png’s content area
            content_lay.setContentsMargins(50, 100, 50, 50)
            content_lay.setSpacing(10)
        else:
            # Fallback if image is missing
            bg_label.setStyleSheet("background-color: #6a00a4; border-radius: 10px;")
            bg_label.setFixedSize(420, 420)  # Match game board size
            content_lay = QVBoxLayout(bg_label)
            content_lay.setContentsMargins(20, 20, 20, 20)

        t = QtWidgets.QLabel("Top 10")
        t.setStyleSheet("font-size: 30px; font-weight: bold; color: white;")
        t.setAlignment(QtCore.Qt.AlignCenter)
        content_lay.addWidget(t)
        
        # Label to display Top 10 from text file
        self.rank_text_label = QtWidgets.QLabel("Loading rankings...")
        self.rank_text_label.setStyleSheet("font-size: 20px; font-weight: bold; color: white; font-family: Monospace;")
        self.rank_text_label.setAlignment(QtCore.Qt.AlignCenter)
        content_lay.addWidget(self.rank_text_label, 1)

        back = QtWidgets.QPushButton("Back")
        back.setFixedSize(120, 36)
        back.setStyleSheet(
            f'border-image: url("{SHORT_EMPTY.replace(os.sep, "/")}");'
            'color: white; font-weight: bold; font-size: 14px;'
        )
        back.clicked.connect(lambda: self.goto("main_menu"))
        content_lay.addWidget(back, alignment=QtCore.Qt.AlignCenter)

        lay.addWidget(bg_label, alignment=QtCore.Qt.AlignCenter)
        return w

    def _page_howto(self):
        from howtoplay import HowToPlayPage
        return HowToPlayPage(self)


    def _page_about(self):
        w = QtWidgets.QWidget()
        lay = QtWidgets.QVBoxLayout(w)
        lay.setAlignment(QtCore.Qt.AlignCenter)
        
        # About us uses ranking_board.png as background
        bg_label = QLabel(w)
        bg_pix = load_pix(ABOUT_BOARD_IMG)
        
        if bg_pix:
            # Use a size proportional to the game board (~420x420 pixels)
            target_width = 1000  # Match game board’s minimum size
            target_height = 1000  # Adjust if needed
            original_size = bg_pix.size()
            # Calculate scale factor to fit target_width while preserving aspect ratio
            scale_factor = min(target_width / original_size.width(), target_height / original_size.height())
            scaled_size = QtCore.QSize(int(original_size.width() * scale_factor), 
                                    int(original_size.height() * scale_factor))
            bg_label.setFixedSize(scaled_size)
            scaled_pix = bg_pix.scaled(scaled_size, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            bg_label.setPixmap(scaled_pix)
            content_lay = QVBoxLayout(bg_label)
            content_lay.setContentsMargins(50, 100, 50, 50)
            content_lay.setSpacing(10)
        else:
            # Fallback
            bg_label.setStyleSheet("background-color: #6a00a4; border-radius: 10px;")
            bg_label.setFixedSize(420, 420)
            content_lay = QVBoxLayout(bg_label)
            content_lay.setContentsMargins(20, 20, 20, 20)

        
        # About Us content
        about_text = """
     
    🎮 Project: Sudoku Game
        Institution: FPT University – Can Tho Campus
        Class: AI2002 – Fall Semester 2025 (FA25)
        Course: CSD203 – Data Structures and Algorithms
        Group: Group 3
        Mentor: Mr. Võ Hồng Khanh
    🧠 Who We Are
    We are a team of passionate students from FPT University Can Tho, majoring in Artificial Intelligence (AI).
    Our project, Sudoku Game, was developed as part of the CSD203 (Data Structures and Algorithms) course.
    Through this project, we aimed to apply our algorithmic knowledge to create an interactive, user-friendly, 
    and intellectually stimulating puzzle game that challenges logical thinking and problem-solving skills.
    👩‍💻 Team Members
        Lê Ngọc Minh – CE191210 (Team Leader)
        Lê Thanh Điền – CE190579 (Secretary)
        Trần Khoa Đăng – CE190256
        Lữ Phú Quý – CE190625
    🚀 Our Vision
    Our goal is to design a Sudoku experience that is both educational and entertaining, combining classical 
    puzzle-solving with modern, elegant design and well-structured algorithms.
    We believe that every line of code can create a better experience — where logic meets creativity.
    """
        about_label = QtWidgets.QLabel(about_text)
        about_label.setStyleSheet("font-size: 16px; font-weight: bold; color: white; font-family: Monospace;")
        about_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        about_label.setWordWrap(True)
        content_lay.addWidget(about_label, 1)

        back = QtWidgets.QPushButton("Back")
        back.setFixedSize(120, 36)
        back.setStyleSheet(
            f'border-image: url("{SHORT_EMPTY.replace(os.sep, "/")}");'
            'color: white; font-weight: bold; font-size: 14px;'
        )
        back.clicked.connect(lambda: self.goto("main_menu"))
        content_lay.addWidget(back, alignment=QtCore.Qt.AlignCenter)

        lay.addWidget(bg_label, alignment=QtCore.Qt.AlignCenter)
        return w

    # navigation
    def goto(self, key: str):
        if key not in self.pages and key != "game":
            return
        if key == "game":
            widget = self.pages.get("game")
            if widget:
                self.stack.setCurrentWidget(widget)
        else:
            self.stack.setCurrentWidget(self.pages[key])
            if key == "ranking":
                self._load_rankings()
            if key == "player_setup":
                self.name_msg_label.setText("") 
        self.msg.setText("")

    def _open_player_setup(self, level: str):
        self._pending_level = level
        self.name_edit.setText("")
        self._last_score_fetched = 0 
        self.goto("player_setup")

    # -------------------------
    # Player Check & Start Game
    # -------------------------
    def _check_player_name(self, name: str, level: str):
        self.name_msg_label.setText("") 
        name = name.strip()
        if not name:
            self.name_msg_label.setText("Please enter a non-empty name!")
            return

        last_score = self._get_last_score(name)
        
        if last_score > 0:
            # Tên trùng: Hỏi xác nhận (tiếng Anh)
            dialog = CustomDialog(
                parent=self, 
                title="Player Found", 
                content=f"A player named {name} has a last recorded score of {last_score}.\n\nIs this you?",
                buttons=[("Yes", True), ("No", False)], 
                background_img=ANNOUNCEMENT_IMG
            )
            
            if dialog.exec_() == QDialog.Accepted:
                result = dialog.results.get('result')
                
                if result is True:
                    self._last_score_fetched = last_score
                    self._start_game(level, name)
                else:
                    # No, new player: Quay lại giao diện đặt tên và thông báo
                    self.name_edit.setText("")
                    self.name_msg_label.setText("Name already exists, please choose another one!")
            
        else:
            # Tên mới
            self._last_score_fetched = 0
            self._start_game(level, name)

    def _get_last_score(self, name: str) -> int:
        """Tìm điểm cao nhất của người chơi này (bất kể level)"""
        max_score = 0
        all_entries = []

        try:
            with open(PLAYER_DATA_JSON, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            raw_data = {"Easy": [], "Medium": [], "Hard": []}
            
        if isinstance(raw_data, dict):
            for level_entries in raw_data.values():
                if isinstance(level_entries, list):
                    all_entries.extend(level_entries)
        
        for entry in all_entries:
            if isinstance(entry, dict) and entry.get("name", "").strip() == name.strip():
                max_score = max(max_score, entry.get("score", 0)) 
                    
        return max_score

    def _start_game(self, level: str, name: str):
        # Tạo puzzle mới
        self._current_puzzle = generate_puzzle(level) 
        
        game_page = self._create_game_page(name, level)
        if "game" in self.pages:
            old = self.pages["game"]
            self.stack.removeWidget(old)
            old.deleteLater()
        self.pages["game"] = game_page
        self.stack.addWidget(game_page)
        self.goto("game")

    def _create_game_page(self, player_name: str, level: str) -> QtWidgets.QWidget:
        w = QtWidgets.QWidget()
        v = QtWidgets.QVBoxLayout(w)

        # --- Top HUD --- (Bỏ thanh last score ở đây)
        top = QtWidgets.QHBoxLayout()
        top.addStretch()

        hud = QtWidgets.QHBoxLayout()
        self.hud_time = LabelWithBg(LONG_EMPTY, "Time: 00:00"); self.hud_time.setFixedSize(220, 46)
        self.hud_score = LabelWithBg(SHORT_EMPTY, "Score: 0"); self.hud_score.setFixedSize(140, 46)
        self.hud_hints = LabelWithBg(SHORT_EMPTY, "Hints: 0"); self.hud_hints.setFixedSize(140, 46)
        hud.addWidget(self.hud_time)
        hud.addWidget(self.hud_score)
        hud.addWidget(self.hud_hints)
        top.addLayout(hud)
        v.addLayout(top)

        # --- Middle: Board + Controls ---
        mid = QtWidgets.QHBoxLayout()
        
        puzzle = self._current_puzzle 
        # Truyền last_score_fetched vào BoardWidget
        board = BoardWidget(self, puzzle["grid"], puzzle["solution"], player_name, level, self._last_score_fetched)
        board.setMinimumSize(420, 420)
        mid.addWidget(board, 0)

        ctrl = QtWidgets.QVBoxLayout()
        ctrl.addStretch()

        btn_hint = LabelWithBg(SHORT_EMPTY, "Hint"); btn_hint.setFixedSize(140, 40)
        btn_reset = LabelWithBg(SHORT_EMPTY, "Reset"); btn_reset.setFixedSize(140, 40)
        btn_menu = LabelWithBg(SHORT_EMPTY, "Main Menu"); btn_menu.setFixedSize(140, 40)

        btn_hint.mousePressEvent = lambda e: self._use_hint(w)
        btn_reset.mousePressEvent = lambda e: self._reset_board_with_penalty(w) # Đổi tên hàm reset
        btn_menu.mousePressEvent = lambda e: self._back_to_main_menu(w) 

        ctrl.addWidget(btn_hint)
        ctrl.addWidget(btn_reset)
        ctrl.addWidget(btn_menu)
        mid.addLayout(ctrl)
        v.addLayout(mid, 1)

        status = QtWidgets.QLabel("Select a cell and enter a number")
        status.setStyleSheet("color:white;")
        v.addWidget(status)

        # --- Game state ---
        w._board = board
        w._player = player_name
        w._level = level
        w._start_time = time.time()
        w._time_elapsed = 0
        w._score = 0
        w._mistakes = 0
        w._original_puzzle = copy.deepcopy(puzzle) # Lưu puzzle gốc 

        if level.lower() == "easy":
            w._hints_left = 5
            w._mistakes_left = 5
            w._countdown = 15 * 60
        elif level.lower() == "medium":
            w._hints_left = 3
            w._mistakes_left = 3
            w._countdown = 20 * 60
        else: # Hard
            w._hints_left = 0
            w._mistakes_left = 0
            w._countdown = 30 * 60
        
        w._status = status
        w._timer = QtCore.QTimer(w)
        w._timer.setInterval(1000)

        def tick():
            if w._countdown is not None:
                w._countdown -= 1
                if w._countdown <= 0:
                    w._timer.stop()
                    
                    # Time Up: sử dụng CustomDialog
                    time_spent = int(time.time() - w._start_time)
                    self._handle_end_game_dialog(
                        player_name=w._player, 
                        score=w._score, 
                        level=w._level, 
                        time_spent=time_spent, 
                        is_completed=False, # Không hoàn thành
                        last_score=self._last_score_fetched,
                        title="Time Up!",
                        content_prefix="Time is up! Game over."
                    )
                    return
                # Hiển thị thời gian đếm ngược
                self.hud_time.setText("Time: " + self._fmt(w._countdown))
                w._time_elapsed = int((w._countdown + int(time.time() - w._start_time)) - w._countdown)
            else:
                w._time_elapsed = int(time.time() - w._start_time)
                self.hud_time.setText("Time: " + self._fmt(w._time_elapsed))
        w._timer.timeout.connect(tick)
        w._timer.start()

        # Initialize HUD
        self.hud_score.setText(f"Score: {w._score}")
        self.hud_hints.setText(f"Hints: {w._hints_left}")
        
        # Events
        board.cell_clicked.connect(lambda r, c: w._status.setText(f"Selected: ({r+1},{c+1})"))
        board.number_clicked.connect(lambda num: self._on_number_click(board, num))
        
        return w

    def _fmt(self, s: int) -> str:
        s = max(0, s) 
        m = s // 60; r = s % 60
        return f"{m:02d}:{r:02d}"

    # actions
    def _on_number_click(self, board: BoardWidget, number: int):
        r, c = board.selected
        gw = self.pages.get("game", self.stack.currentWidget())
        if r is None or c is None:
            self.msg.setText("Select a cell first")
            return
        if board.is_fixed(r, c):
            self.msg.setText("Cannot change a fixed cell")
            return
            
        correct = board.solution[r][c] == number
        
        if correct:
            board.set_value(r, c, number, correct=True)
            gw._score += 10
            self.hud_score.setText(f"Score: {gw._score}")
            self.msg.setText("Correct! +10 points")
            
            if board.is_solved():
                if hasattr(gw, "_timer"):
                    gw._timer.stop()
                
                time_spent = int(time.time() - gw._start_time)
                
                # Tính điểm thưởng thêm: (Thời gian giới hạn - Thời gian hoàn thành) / 10
                max_time_allowed = gw._countdown + time_spent
                time_score = max(0, (max_time_allowed - time_spent) // 10) 
                
                # 1. TÍNH TỔNG ĐIỂM GỐC
                base_score = gw._score + time_score 
                
                # 2. XÁC ĐỊNH HỆ SỐ (Sử dụng hệ số Hard là 2.0, Medium là 1.5, Easy là 1.0)
                level_key = gw._level.lower()
                
                # Định nghĩa hệ số ngay tại đây hoặc sử dụng hằng số đã định nghĩa ở Bước 1
                multiplier = 1.0
                if level_key == "medium":
                    multiplier = 1.5
                elif level_key == "hard":
                    multiplier = 2.0
                    
                # 3. ÁP DỤNG HỆ SỐ ĐỂ TÍNH ĐIỂM CUỐI CÙNG
                final = int(base_score * multiplier) # Sử dụng int() để đảm bảo điểm là số nguyên
                
                # Hiển thị bảng kết thúc (end_game.png)
                self._handle_end_game_dialog(
                    player_name=gw._player, 
                    score=final, # Dùng điểm đã nhân hệ số
                    level=gw._level, 
                    time_spent=time_spent, 
                    is_completed=True,
                    last_score=self._last_score_fetched,
                    title="Congratulations!",
                    # content_prefix=f"Multiplier: x{multiplier:.1f} (Base Score: {base_score})" # Thêm thông báo hệ số
                )
                
        else:
            board.set_value(r, c, number, correct=False)
            
            if gw._mistakes_left > 0:
                gw._mistakes_left -= 1
                gw._score = max(0, getattr(gw, "_score", 0) - 20)
                self.hud_score.setText(f"Score: {gw._score}")
                self.msg.setText(f"Wrong! -20 points. Mistakes left: {gw._mistakes_left}")
            else:
                if hasattr(gw, "_timer"):
                    gw._timer.stop()
                    
                # Game Over: sử dụng CustomDialog
                time_spent = int(time.time() - gw._start_time)
                self._handle_end_game_dialog(
                    player_name=gw._player, 
                    score=gw._score, 
                    level=gw._level, 
                    time_spent=time_spent, 
                    is_completed=False,
                    last_score=self._last_score_fetched,
                    title="You almost had it!",
                    content_prefix="Too many mistakes! Game over."
                )
                return

    def _use_hint(self, gw):
        board: BoardWidget = gw._board
        
        if gw._level.lower() == "hard":
            gw._status.setText("Hard mode does not allow hints!")
            return
            
        if gw._hints_left <= 0:
            gw._status.setText("No hints left")
            return
            
        cell = board.get_random_empty_cell()
        if not cell:
            gw._status.setText("No empty cell to hint")
            return
            
        r, c = cell
        val = board.solution[r][c]
        board.set_value(r, c, val, correct=True, revealed=True)
        gw._hints_left -= 1
        gw._score = max(0, gw._score - 50)
        self.hud_score.setText(f"Score: {gw._score}")
        self.hud_hints.setText(f"Hints: {gw._hints_left}")
        gw._status.setText(f"Hint used. Revealed ({r+1},{c+1}) = {val}. -50 points. Hints left: {gw._hints_left}")
        
        if board.is_solved():
            if hasattr(gw, "_timer"):
                gw._timer.stop()
            time_spent = int(time.time() - gw._start_time)
            max_time_allowed = gw._countdown + time_spent
            time_score = max(0, (max_time_allowed - time_spent) // 10) 
            final = gw._score + time_score
            
            self._handle_end_game_dialog(
                player_name=gw._player, 
                score=final, 
                level=gw._level, 
                time_spent=time_spent, 
                is_completed=True,
                last_score=self._last_score_fetched,
                title="Hoàn thành!",
                content_prefix=""
            )

    def _reset_board_with_penalty(self, gw):
        if hasattr(gw, "_timer"):
            gw._timer.stop()
            
        penalty = 100
            
        # 1. Lấy lại tên và level
        name_before = gw._player
        level_before = gw._level
        
        # 2. Cập nhật last_score_fetched (nếu có) và tạo puzzle mới
        self._last_score_fetched = self._get_last_score(name_before) 
        self._current_puzzle = generate_puzzle(level_before) 
        
        # 3. Tạo game page MỚI hoàn toàn
        new_game_page = self._create_game_page(name_before, level_before)
        
        # 4. Thay thế game page cũ
        if "game" in self.pages:
            old_widget = self.pages["game"]
            self.stack.removeWidget(old_widget)
            old_widget.deleteLater()

        self.pages["game"] = new_game_page
        self.stack.addWidget(new_game_page)
        
        # 5. Trừ điểm phạt 100 từ điểm khởi đầu mới
        new_game_page._score = max(0, new_game_page._score - penalty)
        self.hud_score.setText(f"Score: {new_game_page._score}")
        
        # 6. Chuyển sang page mới và thông báo
        self.goto("game")
        self.msg.setText(f"Board reset! -{penalty} points applied to new game score.")

    # -------------------------
    # End Game Handling 
    # -------------------------
    def _handle_end_game_dialog(self, player_name: str, score: int, level: str, time_spent: int, is_completed: bool, last_score: int, title: str, content_prefix: str):
        
        # 1. Cập nhật và lưu Ranking
        is_new_high_score = score > last_score
        
        if is_completed or is_new_high_score:
            self._save_ranking(player_name, score, level, time_spent)
            # Nếu là High Score mới, điểm mới sẽ là last score cho Replay
            self._last_score_fetched = score 
        else:
            # Nếu không phải High Score mới, giữ nguyên last_score
            self._last_score_fetched = last_score
        
        # 2. Tạo nội dung hiển thị
        score_text = ""
        if last_score > 0:
            if is_completed and score > last_score:
                score_text += f"New High Score: {score}\nLast Score: {last_score}"
            elif is_completed and score <= last_score:
                score_text += f"Score: {score}\nLast Score: {last_score}"
            elif not is_completed: # Kết thúc sớm/Time up/Game Over
                score_text += f"Score: {score}\nLast Score: {last_score}"
        else:
            score_text += f"Score: {score}"
            
        content = (
            (content_prefix + "\n\n" if content_prefix else "") +
            f"Player: {player_name}\n"
            f"Time: {self._fmt(time_spent)}\n"
            f"{score_text}"
        )
        
        # 3. Hiện Dialog
        dialog = CustomDialog(
            parent=self, 
            title=title, 
            content=content, 
            buttons=[("Main Menu", "main_menu"), ("Replay", "new_try")], 
            background_img=END_GAME_IMG,
            content_v_padding=(60, 40) # Căn chỉnh lại
        )
        
        # Chạy GIF pháo hoa khi hoàn thành
        if is_completed:
            dialog.play_gif(2000)

        # 4. Xử lý kết quả Dialog
        if dialog.exec_() == QDialog.Accepted:
            result = dialog.results.get('result')
            
            if result == "main_menu":
                self.goto("main_menu")
            elif result == "new_try":
                # Bắt đầu lại màn chơi hiện tại (puzzle cũ, level cũ)
                self._handle_new_try(player_name, level)

    def _handle_new_try(self, player_name: str, level: str):
        
        # Dùng lại puzzle đã tạo ra ở lần chơi trước (self._current_puzzle)
        puzzle = self._current_puzzle 
        
        # Dừng và xóa game page cũ
        if "game" in self.pages and hasattr(self.pages["game"], "_timer"):
            self.pages["game"]._timer.stop()
            old = self.pages["game"]
            self.stack.removeWidget(old)
            old.deleteLater()
        
        # Tạo game page MỚI hoàn toàn với puzzle CŨ và last score đã cập nhật
        # Dùng _create_game_page_with_existing_puzzle để tránh tạo puzzle mới
        game_page = self._create_game_page_with_existing_puzzle(
            player_name, 
            level, 
            puzzle["grid"], 
            puzzle["solution"], 
            self._last_score_fetched
        )
            
        self.pages["game"] = game_page
        self.stack.addWidget(game_page)
        
        self.goto("game")
        self.msg.setText(f"Replay! Restarting {level} mode.")


    def _create_game_page_with_existing_puzzle(self, player_name: str, level: str, grid, solution, last_score) -> QtWidgets.QWidget:
        # Hầu như copy từ _create_game_page nhưng bỏ qua generate_puzzle
        w = QtWidgets.QWidget()
        v = QtWidgets.QVBoxLayout(w)

        top = QtWidgets.QHBoxLayout()
        top.addStretch()

        hud = QtWidgets.QHBoxLayout()
        self.hud_time = LabelWithBg(LONG_EMPTY, "Time: 00:00"); self.hud_time.setFixedSize(220, 46)
        self.hud_score = LabelWithBg(SHORT_EMPTY, "Score: 0"); self.hud_score.setFixedSize(140, 46)
        self.hud_hints = LabelWithBg(SHORT_EMPTY, "Hints: 0"); self.hud_hints.setFixedSize(140, 46)
        hud.addWidget(self.hud_time)
        hud.addWidget(self.hud_score)
        hud.addWidget(self.hud_hints)
        top.addLayout(hud)
        v.addLayout(top)

        mid = QtWidgets.QHBoxLayout()
        board = BoardWidget(self, grid, solution, player_name, level, last_score)
        board.setMinimumSize(420, 420)
        mid.addWidget(board, 0)

        ctrl = QtWidgets.QVBoxLayout()
        ctrl.addStretch()

        btn_hint = LabelWithBg(SHORT_EMPTY, "Hint"); btn_hint.setFixedSize(140, 40)
        btn_reset = LabelWithBg(SHORT_EMPTY, "Reset"); btn_reset.setFixedSize(140, 40)
        btn_menu = LabelWithBg(SHORT_EMPTY, "Main Menu"); btn_menu.setFixedSize(140, 40)

        btn_hint.mousePressEvent = lambda e: self._use_hint(w)
        btn_reset.mousePressEvent = lambda e: self._reset_board_with_penalty(w)
        btn_menu.mousePressEvent = lambda e: self._back_to_main_menu(w) 

        ctrl.addWidget(btn_hint)
        ctrl.addWidget(btn_reset)
        ctrl.addWidget(btn_menu)
        mid.addLayout(ctrl)
        v.addLayout(mid, 1)

        status = QtWidgets.QLabel("Select a cell and enter a number")
        status.setStyleSheet("color:white;")
        v.addWidget(status)

        w._board = board
        w._player = player_name
        w._level = level
        w._start_time = time.time()
        w._time_elapsed = 0
        w._score = 0
        w._mistakes = 0
        
        # Dùng puzzle CŨ cho _current_puzzle và _original_puzzle
        self._current_puzzle = {"grid": grid, "solution": solution}
        w._original_puzzle = copy.deepcopy(self._current_puzzle)

        if level.lower() == "easy":
            w._hints_left = 5
            w._mistakes_left = 5
            w._countdown = 15 * 60
        elif level.lower() == "medium":
            w._hints_left = 3
            w._mistakes_left = 3
            w._countdown = 20 * 60
        else: # Hard
            w._hints_left = 0
            w._mistakes_left = 0
            w._countdown = 30 * 60
        
        w._status = status
        w._timer = QtCore.QTimer(w)
        w._timer.setInterval(1000)

        def tick():
            if w._countdown is not None:
                w._countdown -= 1
                if w._countdown <= 0:
                    w._timer.stop()
                    
                    time_spent = int(time.time() - w._start_time)
                    self._handle_end_game_dialog(
                        player_name=w._player, 
                        score=w._score, 
                        level=w._level, 
                        time_spent=time_spent, 
                        is_completed=False,
                        last_score=self._last_score_fetched,
                        title="Time Up!",
                        content_prefix="Time is up! Game over."
                    )
                    return
                self.hud_time.setText("Time: " + self._fmt(w._countdown))
                w._time_elapsed = int((w._countdown + int(time.time() - w._start_time)) - w._countdown)
            else:
                w._time_elapsed = int(time.time() - w._start_time)
                self.hud_time.setText("Time: " + self._fmt(w._time_elapsed))
        w._timer.timeout.connect(tick)
        w._timer.start()

        self.hud_score.setText(f"Score: {w._score}")
        self.hud_hints.setText(f"Hints: {w._hints_left}")

        board.cell_clicked.connect(lambda r, c: w._status.setText(f"Selected: ({r+1},{c+1})"))
        board.number_clicked.connect(lambda num: self._on_number_click(board, num))
        
        return w


    # rankings
    def _save_ranking(self, name: str, score: int, level: str, time_spent: int):
        # 1. Lưu vào file JSON (PLAYER_DATA_JSON)
        level_key = level.title()
        try:
            with open(PLAYER_DATA_JSON, "r", encoding="utf-8") as f:
                data: Dict[str, List] = json.load(f)
        except Exception:
            data = {"Easy": [], "Medium": [], "Hard": []}
            
        if not isinstance(data, dict):
            data = {"Easy": [], "Medium": [], "Hard": []}
            
        if level_key not in data or not isinstance(data[level_key], list):
            data[level_key] = []

        entry = {
            "name": name, 
            "score": score, 
            "level": level_key, 
            "time_spent": time_spent,
            "date": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # 2. Xóa các entry cũ của người chơi này trong level này nếu điểm mới cao hơn
        data[level_key] = [
            e for e in data[level_key] 
            if e.get("name", "").strip() != name.strip() or e.get("score", 0) > score
        ]
        
        # 3. Thêm entry mới
        data[level_key].append(entry)
        
        # Sắp xếp và chỉ lấy Top 10 của level đó (giữ nguyên logic cũ)
        data[level_key] = sorted(data[level_key], 
                                  key=lambda x: (x.get("score", 0), -x.get("time_spent", 0)), 
                                  reverse=True)
                                  
        with open(PLAYER_DATA_JSON, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        # 4. Cập nhật file Top 10 Text
        self._update_top10_txt(data)
        
    def _update_top10_txt(self, all_data: Dict[str, List]):
        all_entries = []
        for level_key in all_data:
            if isinstance(all_data[level_key], list):
                all_entries.extend(all_data[level_key])

        # Sắp xếp theo score giảm dần, nếu bằng thì time_spent tăng dần
        data = sorted(
            all_entries,
            key=lambda x: (x.get("score", 0), -x.get("time_spent", 0)),
            reverse=True
        )[:10]

        # Header
        output = ["Rank\tPlayer\tScore"]

        # Biểu tượng top
        medals = ["🥇", "🥈", "🥉"]
        num_emojis = ["4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]

        for i, row in enumerate(data):
            name = row.get("name", "Unknown")
            score = row.get("score", 0)

            # Chọn icon phù hợp
            if i < 3:
                rank_icon = medals[i]
            elif i < 10:
                rank_icon = num_emojis[i - 3]
            else:
                rank_icon = str(i + 1)

            # Ghi theo format bảng có tab phân cách
            line = f"{rank_icon}\t{name}\t{score}"
            output.append(line)

        # Ghi vào file
        try:
            with open(TOP10_RANKING_TXT, "w", encoding="utf-8") as f:
                f.write("\n".join(output))
            print(f"[Info] Updated ranking saved to {TOP10_RANKING_TXT}")
        except Exception as e:
            print(f"Error writing top10_ranking.txt: {e}")


    def _load_rankings(self):
        # Đọc nội dung từ file top10_ranking.txt
        try:
            with open(TOP10_RANKING_TXT, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception:
            content = "\nNo rankings yet."
            
        # Hiển thị
        self.rank_text_label.setText(content)


# ---------------------------
# Entrypoint
# ---------------------------
def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()