# howtoplay.py
"""
How to Play Page with Slides
Requirements:
- assets/slide_frame.png (background for all slides)
- assets/button/arrow_next.png
- assets/button/arrow_back.png
- Other assets from main.py
"""
import sys
import os
import copy
import time
import random
from typing import List, Optional, Tuple, Dict
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QLabel, QWidget, QVBoxLayout, QHBoxLayout, QPushButton
# Import necessary classes and functions from main.py context
# Assuming we can access or duplicate BoardWidget, LabelWithBg, generate_puzzle, etc.
# For simplicity, we'll duplicate/minimize necessary code here.
BASE_DIR = os.path.dirname(__file__)
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
BUTTON_DIR = os.path.join(ASSETS_DIR, "button")
NUM_DIR = os.path.join(ASSETS_DIR, "numbers")
FRAME_IMG = os.path.join(ASSETS_DIR, "gameplay_frame.png")
SLIDE_FRAME_IMG = os.path.join(ASSETS_DIR, "slide_frame.png")
ARROW_NEXT = os.path.join(BUTTON_DIR, "arrow_next.png")
ARROW_BACK = os.path.join(BUTTON_DIR, "arrow_back.png")
SHORT_EMPTY = os.path.join(BUTTON_DIR, "short_empty.png")
LONG_EMPTY = os.path.join(BUTTON_DIR, "long_empty.png")
# Duplicate Sudoku logic minimally
def is_valid(grid: List[List[int]], row: int, col: int, num: int) -> bool:
    # Check row
    for i in range(9):
        if grid[row][i] == num and i != col:
            return False
    # Check column
    for i in range(9):
        if grid[i][col] == num and i != row:
            return False
    # Check 3x3 block
    sr, sc = row - row % 3, col - col % 3
    for i in range(3):
        for j in range(3):
            if grid[sr + i][sc + j] == num and (sr + i, sc + j) != (row, col):
                return False
    return True

# Helper function for generating solution without checking self-conflicts
def is_safe(grid: List[List[int]], row: int, col: int, num: int) -> bool:
    for i in range(9):
        if grid[row][i] == num: return False
        if grid[i][col] == num: return False
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
                    # Use is_safe here since we are solving an empty grid
                    if is_safe(grid, r, c, n): 
                        grid[r][c] = n
                        if solve_sudoku(grid):
                            return True
                        grid[r][c] = 0
                return False
    return True

def generate_solution() -> List[List[int]]:
    g = [[0] * 9 for _ in range(9)]
    # Use time as seed for random unique solution
    random.seed(time.time()) 
    solve_sudoku(g)
    return g

def count_solutions(grid, count=0):
    if count > 1:
        return 2
    for r in range(9):
        for c in range(9):
            if grid[r][c] == 0:
                for n in range(1, 10):
                    if is_safe(grid, r, c, n):
                        grid[r][c] = n
                        count = count_solutions(grid, count)
                        grid[r][c] = 0
                        if count > 1:
                            return 2
                return count
    return count + 1

def is_valid_puzzle(puzzle):
    for i in range(9):
        if all(puzzle[i][j] == 0 for j in range(9)):
            return False
    for j in range(9):
        if all(puzzle[i][j] == 0 for i in range(9)):
            return False
    for br in range(0, 9, 3):
        for bc in range(0, 9, 3):
            if all(puzzle[i][j] == 0 for i in range(br, br+3) for j in range(bc, bc+3)):
                return False
    return True

def generate_puzzle(level: str, cells_to_remove=None):
    if cells_to_remove is None:
        if level.lower() == "easy":
            cells_to_remove = 43
        elif level.lower() == "medium":
            cells_to_remove = 45
        else:
            cells_to_remove = 51
            
    solution = generate_solution()
    puzzle = copy.deepcopy(solution)
    all_cells = [(r, c) for r in range(9) for c in range(9)]
    random.shuffle(all_cells)
    
    removed = 0
    start_time = time.time() # Safety break for long generation
    
    for r, c in all_cells:
        if removed >= cells_to_remove or time.time() - start_time > 1:
            break
            
        backup = puzzle[r][c]
        puzzle[r][c] = 0
        
        temp = copy.deepcopy(puzzle)
        if count_solutions(temp) == 1 and is_valid_puzzle(puzzle):
            removed += 1
        else:
            puzzle[r][c] = backup
            
    return {"grid": puzzle, "solution": solution}
    
# Duplicate LabelWithBg
class LabelWithBg(QLabel):
    def __init__(self, pix_path: str, text: str = "", parent=None, text_color: str = "white"):
        super().__init__(parent)
        self._pix = QtGui.QPixmap(pix_path) if pix_path and os.path.exists(pix_path) else None
        self.setText(text)
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setStyleSheet(f"color: {text_color}; font-weight: bold; font-size: 16px;")
        
    def set_text_style(self, style: str):
        self.setStyleSheet(style)

    def paintEvent(self, event):
        qp = QtGui.QPainter(self)
        if self._pix:
            qp.drawPixmap(self.rect(), self._pix.scaled(self.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        super().paintEvent(event)
        
# Duplicate BoardWidget with modifications for demo
class DemoBoardWidget(QtWidgets.QWidget):
    cell_clicked = QtCore.pyqtSignal(int, int)
    number_clicked = QtCore.pyqtSignal(int)
    
    def __init__(self, parent, grid: List[List[int]], solution: List[List[int]], player_name: str, level: str, last_score: int, demo_mode=False, highlights: Optional[Dict[str, QColor]] = None, wrong_cells: Optional[set] = None, correct_mark: Optional[Tuple[int, int]] = None):
        super().__init__(parent)
        self.grid0 = [row[:] for row in grid]
        self.grid = [row[:] for row in grid]
        self.solution = solution
        self.selected = (None, None)
        self.hover = (None, None)
        self.wrong_cells = wrong_cells or set()
        self.revealed = set()
        self.player_name = player_name
        self.level = level
        self.last_score = last_score
        self.demo_mode = demo_mode
        self.highlights = highlights or {} 
        self.correct_mark = correct_mark 
        self.board_pix = QtGui.QPixmap(FRAME_IMG) if os.path.exists(FRAME_IMG) else None
        self.num_pix = {}
        for n in range(1, 10):
            p = QtGui.QPixmap(os.path.join(NUM_DIR, f"{n}.png")) if os.path.exists(os.path.join(NUM_DIR, f"{n}.png")) else None
            if p:
                self.num_pix[n] = p
        self.setMouseTracking(True)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        
    def sizeHint(self):
        return QtCore.QSize(800, 800) 

    def paintEvent(self, event):
        qp = QtGui.QPainter(self)
        qp.setRenderHint(QtGui.QPainter.Antialiasing)
        W, H = self.width(), self.height()
        
        # 1. Draw Board Frame Background
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
            qp.setBrush(QColor(50, 50, 50))
            qp.setPen(QtGui.QPen(QColor(0, 0, 0), 2))
            qp.drawRoundedRect(board_rect, 10, 10)
            
        # Determine Grid Area
        gs = min(board_rect.width(), board_rect.height()) * 0.76 # Estimate grid size relative to frame
        gs = int(gs)
        grid_rect = QtCore.QRect(
            board_rect.left() + (board_rect.width() - gs) // 2,
            board_rect.top() + (board_rect.height() - gs) // 2, 
            gs, gs
        )
        
        # Player info area estimate (consistent with original logic)
        player_info_height = int(grid_rect.height() * 0.12)
        player_info_rect = QtCore.QRect(grid_rect.left(), grid_rect.top() - player_info_height - 15,
                                         grid_rect.width(), player_info_height)

        # 2. Player Info Text
        f = qp.font()
        f.setPixelSize(max(14, int(player_info_rect.height() * 0.2)))
        f.setBold(True)
        qp.setFont(f)
        line_height = player_info_rect.height() // 3
        text_color = QColor(0, 0, 0)
        qp.setPen(QtGui.QPen(text_color, 2))
        
        qp.drawText(player_info_rect.left(), player_info_rect.top() + line_height - 2, f"Player: {self.player_name}")
        qp.drawText(player_info_rect.left(), player_info_rect.top() + line_height * 2 - 2, f"Level: {self.level}")
        qp.drawText(player_info_rect.left(), player_info_rect.top() + line_height * 3 - 2, f"Last Score: {self.last_score}")

        # 3. Highlights
        if 'grid' in self.highlights:
            qp.setPen(QtCore.Qt.NoPen)
            qp.setBrush(self.highlights['grid'])
            qp.drawRect(grid_rect)
        if 'player_info' in self.highlights:
            qp.setPen(QtCore.Qt.NoPen)
            qp.setBrush(self.highlights['player_info'])
            qp.drawRect(player_info_rect)

        # 4. Grid Lines and Numbers
        cs = grid_rect.width() / 9.0
        
        for r in range(9):
            for c in range(9):
                v = self.grid[r][c]
                cell_x = grid_rect.left() + int(c * cs)
                cell_y = grid_rect.top() + int(r * cs)
                rect = QtCore.QRect(cell_x, cell_y, int(cs), int(cs))

                # Highlight wrong/correct fills
                if (r, c) in self.wrong_cells:
                    qp.setBrush(QColor(255, 0, 0, 100))
                    qp.setPen(QtCore.Qt.NoPen)
                    qp.drawRect(rect)
                elif self.correct_mark == (r, c):
                    qp.setBrush(QColor(0, 255, 0, 100))
                    qp.setPen(QtCore.Qt.NoPen)
                    qp.drawRect(rect)
                    # Draw checkmark
                    qp.setPen(QtGui.QPen(QColor(0, 160, 0), 4))
                    qp.drawLine(rect.left() + int(cs*0.2), rect.top() + int(cs*0.5), rect.left() + int(cs*0.4), rect.top() + int(cs*0.7))
                    qp.drawLine(rect.left() + int(cs*0.4), rect.top() + int(cs*0.7), rect.left() + int(cs*0.8), rect.top() + int(cs*0.3))

                if v == 0: continue
                
                # Draw numbers
                if v in self.num_pix:
                    pix = self.num_pix[v]
                    target = pix.scaled(int(cs * 0.85), int(cs * 0.85), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
                    qp.drawPixmap(rect.left() + (rect.width() - target.width()) // 2,
                                  rect.top() + (rect.height() - target.height()) // 2, target)
                else:
                    f = qp.font()
                    f.setPixelSize(max(10, int(cs * 0.55)))
                    qp.setFont(f)
                    if self.grid0[r][c] != 0:
                        qp.setPen(QtGui.QPen(QColor(30, 30, 30)))
                    else:
                        qp.setPen(QtGui.QPen(QColor(0, 70, 160)))
                    qp.drawText(rect, QtCore.Qt.AlignCenter, str(v))

        # Draw Grid Lines
        qp.setPen(QtGui.QPen(QColor(0, 0, 0, 50), 1))
        for i in range(10):
            y = grid_rect.top() + int(i * cs)
            qp.drawLine(grid_rect.left(), y, grid_rect.right(), y)
        for j in range(10):
            x = grid_rect.left() + int(j * cs)
            qp.drawLine(x, grid_rect.top(), x, grid_rect.bottom())

        # Draw Bold Lines for 3x3 Blocks
        qp.setPen(QtGui.QPen(QColor(0, 0, 0, 160), 2))
        for i in range(0, 10, 3):
            y = grid_rect.top() + int(i * cs)
            qp.drawLine(grid_rect.left(), y, grid_rect.right(), y)
        for j in range(0, 10, 3):
            x = grid_rect.left() + int(j * cs)
            qp.drawLine(x, grid_rect.top(), x, grid_rect.bottom())
            
        # 5. Number pad
        number_pad_width = int(grid_rect.width() * 0.105)
        number_pad_rect = QtCore.QRect(grid_rect.right() + 40, grid_rect.top(), number_pad_width, grid_rect.height())
        qp.setPen(QtCore.Qt.NoPen)
        qp.setBrush(QColor(240, 240, 240, 200))
        qp.drawRoundedRect(number_pad_rect, 5, 5)
        ncs = number_pad_rect.height() / 9.0
        
        for i in range(9):
            num = i + 1
            cell_rect = QtCore.QRect(number_pad_rect.left(), number_pad_rect.top() + int(i * ncs),
                                     number_pad_rect.width(), int(ncs))
            qp.setPen(QtGui.QPen(QColor(100, 100, 100), 1))
            qp.setBrush(QColor(255, 255, 255, 230))
            qp.drawRect(cell_rect)
            
            if num in self.num_pix:
                pix = self.num_pix[num]
                target = pix.scaled(int(number_pad_rect.width() * 0.85), int(ncs * 0.85),
                                     QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
                qp.drawPixmap(cell_rect.left() + (cell_rect.width() - target.width()) // 2,
                              cell_rect.top() + (cell_rect.height() - target.height()) // 2, target)
            else:
                f = qp.font()
                f.setPixelSize(max(12, int(ncs * 0.6)))
                qp.setFont(f)
                qp.setPen(QtGui.QPen(QColor(30, 30, 30)))
                qp.drawText(cell_rect, QtCore.Qt.AlignCenter, str(num))
                
    def mousePressEvent(self, event):
        if not self.demo_mode:
            # Handle as in main (only for slide 11)
            pass
            
    def get_random_empty_cell(self) -> Optional[Tuple[int, int]]:
        """Helper for Slide 11 Hint logic"""
        empty_cells = []
        for r in range(9):
            for c in range(9):
                if self.grid[r][c] == 0:
                    empty_cells.append((r, c))
        return random.choice(empty_cells) if empty_cells else None
        
# HowToPlayPage class
class HowToPlayPage(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.current_slide = 0
        self.total_slides = 11
        
        # State for coupling Slide 9 and 10
        self.s9_solution: Optional[List[List[int]]] = None
        self.s9_wrong_pos: Optional[Tuple[int, int]] = None
        self.s9_initial_grid: Optional[List[List[int]]] = None
        
        self.slide_bg_pix = QtGui.QPixmap(SLIDE_FRAME_IMG) if os.path.exists(SLIDE_FRAME_IMG) else None
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(50, 50, 50, 50) # Added padding to fit content better
        
        self.content_container = QWidget(self)
        content_layout = QVBoxLayout(self.content_container)
        content_layout.setAlignment(QtCore.Qt.AlignCenter)
        main_layout.addWidget(self.content_container, 1) # Stretch factor 1
        
        nav_layout = QHBoxLayout()
        nav_layout.addStretch()
        
        self.back_btn = QPushButton()
        self.back_btn.setIcon(QtGui.QIcon(ARROW_BACK))
        self.back_btn.setFixedSize(50, 50) 
        self.back_btn.clicked.connect(self.prev_slide)
        nav_layout.addWidget(self.back_btn)
        
        # Slide Counter
        self.slide_label = QLabel("1/11")
        self.slide_label.setAlignment(QtCore.Qt.AlignCenter)
        self.slide_label.setStyleSheet("font-size: 18px; font-weight: bold; color: black;")
        nav_layout.addWidget(self.slide_label)
        
        self.next_btn = QPushButton()
        self.next_btn.setIcon(QtGui.QIcon(ARROW_NEXT))
        self.next_btn.setFixedSize(50, 50)
        self.next_btn.clicked.connect(self.next_slide)
        nav_layout.addWidget(self.next_btn)
        
        nav_layout.addStretch()
        main_layout.addLayout(nav_layout)
        
        self.update_slide()
        
    def paintEvent(self, event):
        qp = QtGui.QPainter(self)
        if self.slide_bg_pix:
            qp.drawPixmap(self.rect(), self.slide_bg_pix.scaled(self.size(), QtCore.Qt.IgnoreAspectRatio, QtCore.Qt.SmoothTransformation))

    def update_slide(self):
        # Clear content
        if self.content_container.layout() is not None:
            while self.content_container.layout().count():
                child = self.content_container.layout().takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
                    
        # Create slide content
        slide_widget = self.create_slide(self.current_slide + 1)
        self.content_container.layout().addWidget(slide_widget)
        
        # Update buttons and counter
        self.back_btn.setEnabled(self.current_slide > 0)
        self.next_btn.setEnabled(self.current_slide < self.total_slides - 1)
        self.slide_label.setText(f"{self.current_slide + 1}/{self.total_slides}")
        
    def next_slide(self):
        if self.current_slide < self.total_slides - 1:
            self.current_slide += 1
            self.update_slide()
            
    def prev_slide(self):
        if self.current_slide > 0:
            self.current_slide -= 1
            self.update_slide()

    def create_slide(self, slide_num):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setAlignment(QtCore.Qt.AlignCenter)
        
        expl_style = "font-size: 20px; color: black; font-weight: 500;"
        
        if slide_num == 1:
            # Slide 1: Theory (Vietnamese)
            title = QLabel("HƯỚNG DẪN CHƠI SUDOKU")
            title.setStyleSheet("font-size: 28px; color: black; font-weight: bold; margin-bottom: 20px;")
            title.setAlignment(QtCore.Qt.AlignCenter)
            
            text = QLabel("Luật chơi Sudoku:\n\n"
                          "1. Điền các số từ **1 đến 9** vào lưới 9x9.\n"
                          "2. Đảm bảo **mỗi hàng** chỉ chứa các số 1-9 và **không bị trùng**.\n"
                          "3. Đảm bảo **mỗi cột** chỉ chứa các số 1-9 và **không bị trùng**.\n"
                          "4. Đảm bảo **mỗi khối 3x3** chỉ chứa các số 1-9 và **không bị trùng**.")
            text.setStyleSheet("font-size: 22px; color: black;")
            text.setWordWrap(True)
            
            layout.addWidget(title)
            layout.addStretch()
            layout.addWidget(text)
            layout.addStretch()
            
        elif slide_num in range(2, 11):
            # Generate sample puzzle for demo
            puzzle = generate_puzzle("easy")
            grid = puzzle["grid"]
            solution = puzzle["solution"]
            
            wrong_cells = set()
            correct_mark = None
            highlights = {}
            hints_count = 3 # Default for Easy/Medium demo
            
            # Default HUD elements
            hud_time = LabelWithBg(LONG_EMPTY, "Time: 00:00"); hud_time.setFixedSize(220, 46)
            hud_score = LabelWithBg(SHORT_EMPTY, "Score: 0"); hud_score.setFixedSize(140, 46)
            hud_hints = LabelWithBg(SHORT_EMPTY, f"Hints: {hints_count}"); hud_hints.setFixedSize(140, 46)
            
            # Default control buttons
            btn_hint = LabelWithBg(SHORT_EMPTY, "Hint"); btn_hint.setFixedSize(140, 40)
            btn_reset = LabelWithBg(SHORT_EMPTY, "Reset"); btn_reset.setFixedSize(140, 40)
            btn_menu = LabelWithBg(SHORT_EMPTY, "Main Menu"); btn_menu.setFixedSize(140, 40)
            
            expl_text = ""
            
            if slide_num == 2:
                expl_text = "Đây là **Giao diện trò chơi** chính."
            
            elif slide_num == 3:
                highlights['grid'] = QColor(255, 0, 0, 100) # Grid highlight
                expl_text = "Đây là **Lưới Sudoku (Grid)**, khu vực điền số."
            
            elif slide_num == 4:
                highlights['player_info'] = QColor(255, 0, 0, 100) # Player Info highlight
                expl_text = "Đây là **Thông tin người chơi**: Gồm Tên, Độ khó (Level) và Điểm số gần nhất (Last Score)."
            
            elif slide_num == 5:
                hud_time.setText("Time: 20:00")
                hud_time.set_text_style("color: red; font-weight: bold; font-size: 16px;") 
                expl_text = ("**Thời gian** (Time) đếm ngược:\n"
                             "- Dễ: 20 phút. Trung bình: 15 phút. Khó: 10 phút.\n"
                             "- Hết giờ là thua. Hoàn thành sớm sẽ có **điểm thưởng**.")
            
            elif slide_num == 6:
                hud_score.setText("Score: 100")
                hud_score.set_text_style("color: red; font-weight: bold; font-size: 16px;") 
                expl_text = "**Điểm số (Score)**: Được cộng khi điền đúng. Hoàn thành nhanh sẽ nhận thêm điểm thưởng."
            
            elif slide_num == 7:
                hints_count = 0 # Show 0 hints for Hard level example
                hud_hints.setText(f"Hints: {hints_count}")
                hud_hints.set_text_style("color: red; font-weight: bold; font-size: 16px;")
                btn_hint.set_text_style("color: white; font-weight: bold; font-size: 16px; background-color: #ff0000;")
                
                expl_text = ("**Gợi ý (Hint)**: Dễ/TB: 3 lần, Khó: 0 lần.\n"
                             "- Nhấn nút **Hint** để điền ngẫu nhiên 1 ô trống (trừ 50 điểm).\n"
                             "- Khi Gợi ý = 0, nút **Hint** sẽ bị **vô hiệu hóa** (như hình - tô đỏ).")

            elif slide_num == 8:
                btn_reset.set_text_style("color: white; font-weight: bold; font-size: 16px; background-color: #ff0000;")
                
                expl_text = ("**Đặt lại (Reset)**:\n"
                             "- Tạo ván mới cho độ khó hiện tại. **Điểm và Thời gian sẽ bị reset**.\n"
                             "- Mọi tiến trình trước đó **không được lưu**.")
            
            elif slide_num == 9:
                # Store the initial grid state for slide 10 to use a clean slate
                self.s9_initial_grid = copy.deepcopy(grid)
                self.s9_solution = solution
                
                # Logic to find a wrong fill
                empty_cells = [(r, c) for r in range(9) for c in range(9) if grid[r][c] == 0]
                if empty_cells:
                    r, c = random.choice(empty_cells)
                    # Find a number that conflicts in the row (simplest conflict)
                    wrong_num = -1
                    c_conflict = -1
                    for n in range(1, 10):
                        if n in grid[r]:
                            wrong_num = n
                            c_conflict = grid[r].index(wrong_num)
                            break
                    if wrong_num == -1: wrong_num = 1; c_conflict = 0 # Fallback 
                    
                    grid[r][c] = wrong_num
                    wrong_cells = {(r, c), (r, c_conflict)}
                    self.s9_wrong_pos = (r, c)
                    
                    expl_text = f"**Điền sai**: Số **{wrong_num}** (tô đỏ) bị điền sai do đã trùng với ô đã có số **{wrong_num}** trong **cùng một hàng**. Mọi trùng lặp (hàng, cột, khối 3x3) đều là sai."
                else:
                    expl_text = "Không tìm thấy ô trống để tạo ví dụ sai."


            elif slide_num == 10:
                # Correct Example Logic (using state from Slide 9)
                if self.s9_solution and self.s9_wrong_pos and self.s9_initial_grid:
                    r, c = self.s9_wrong_pos
                    correct_val = self.s9_solution[r][c]
                    
                    # Re-use the initial grid from S9
                    grid = self.s9_initial_grid
                    
                    # Apply the correct number
                    grid[r][c] = correct_val
                    correct_mark = (r, c)
                    
                    expl_text = f"**Điền đúng**: Ô (tích xanh) đã được điền số **{correct_val}** một cách chính xác, không có bất kỳ trùng lặp nào trong hàng, cột, và khối 3x3."
                else:
                    # Fallback
                    r, c = 0, 0
                    while grid[r][c] != 0:
                        r = random.randint(0, 8)
                        c = random.randint(0, 8)
                        
                    grid[r][c] = solution[r][c]
                    correct_mark = (r, c)
                    expl_text = f"**Điền đúng**: Ô (tích xanh) đã được điền số **{grid[r][c]}** một cách chính xác, không có bất kỳ trùng lặp nào."

            # Create Board Widget
            board = DemoBoardWidget(self, grid, solution, "DemoPlayer", "Easy", 0,
                                     demo_mode=True, highlights=highlights,
                                     wrong_cells=wrong_cells, correct_mark=correct_mark)
            board.setFixedSize(800, 800)
            
            # --- Assemble Layout for Slides 2-10 ---
            top_hud = QHBoxLayout()
            top_hud.addWidget(hud_time)
            top_hud.addWidget(hud_score)
            top_hud.addWidget(hud_hints)
            layout.addLayout(top_hud)
            
            mid = QHBoxLayout()
            mid.addWidget(board)
            
            ctrl = QVBoxLayout()
            ctrl.addWidget(btn_hint)
            ctrl.addWidget(btn_reset)
            ctrl.addWidget(btn_menu)
            mid.addLayout(ctrl)
            layout.addLayout(mid)
            
            expl_label = QLabel(expl_text)
            expl_label.setStyleSheet(expl_style)
            expl_label.setWordWrap(True)
            layout.addWidget(expl_label)
            
        elif slide_num == 11:
            # Interactive Practice Slide (Slide 11)
            cells_to_remove = 28 
            puzzle = generate_puzzle("easy", cells_to_remove=cells_to_remove)
            grid = puzzle["grid"]
            solution = puzzle["solution"]
            
            board = DemoBoardWidget(self, grid, solution, "Practice", "Practice", 0, demo_mode=False) 
            board.setFixedSize(800, 800)
            
            # HUD for Practice
            hud_time = LabelWithBg(LONG_EMPTY, "Time: 00:00"); hud_time.setFixedSize(220, 46)
            hud_score = LabelWithBg(SHORT_EMPTY, "Score: 0"); hud_score.setFixedSize(140, 46)
            hud_hints = LabelWithBg(SHORT_EMPTY, f"Hints: {cells_to_remove}"); hud_hints.setFixedSize(140, 46) 
            
            top_hud = QHBoxLayout()
            top_hud.addWidget(hud_time)
            top_hud.addWidget(hud_score)
            top_hud.addWidget(hud_hints)
            layout.addLayout(top_hud)
            
            mid = QHBoxLayout()
            mid.addWidget(board)
            
            ctrl = QVBoxLayout()
            btn_hint = LabelWithBg(SHORT_EMPTY, "Hint"); btn_hint.setFixedSize(140, 40)
            btn_reset = LabelWithBg(SHORT_EMPTY, "Reset"); btn_reset.setFixedSize(140, 40)
            btn_menu = LabelWithBg(SHORT_EMPTY, "Main Menu"); btn_menu.setFixedSize(140, 40)
            
            # Interactive Hint Logic
            def use_hint(event):
                hints_left = int(hud_hints.text().split(": ")[1])
                if hints_left > 0:
                    # Uses the helper method from DemoBoardWidget
                    cell = board.get_random_empty_cell() 
                    
                    if cell:
                        r, c = cell
                        val = solution[r][c]
                        
                        board.grid[r][c] = val
                        
                        new_hints_left = hints_left - 1
                        hud_hints.setText(f"Hints: {new_hints_left}")
                        
                        # Visual cue for correct fill
                        board.correct_mark = (r, c)
                        board.update()

            # Override mousePressEvent for the LabelWithBg 'button'
            btn_hint.mousePressEvent = use_hint 
            
            ctrl.addWidget(btn_hint)
            ctrl.addWidget(btn_reset)
            ctrl.addWidget(btn_menu)
            
            mid.addLayout(ctrl)
            layout.addLayout(mid)
            
            status = QLabel("Chế độ **Luyện tập**: Sử dụng Hint để điền. Thử điền tay nếu bạn muốn!")
            status.setStyleSheet("font-size: 20px; color: black; font-weight: bold;")
            layout.addWidget(status)

        return w