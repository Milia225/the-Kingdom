# gui.py
import tkinter as tk
from tkinter import messagebox
from gotypes import Player, Point, Move
from goboard_slow import Board, VALID_POINTS


class KingdomGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Kingdom - 国王与大臣棋")
        self.root.resizable(False, False)

        # ================= 顶部按钮区域 =================
        button_frame = tk.Frame(root, bg="#F0F0F0")
        button_frame.pack(fill=tk.X, pady=5)

        # 重新开始按钮
        self.btn_restart = tk.Button(button_frame, text="重新开始", font=("Arial", 12), command=self.reset_game)
        self.btn_restart.pack(side=tk.LEFT, padx=20)

        # 悔棋按钮
        self.btn_undo = tk.Button(button_frame, text="悔棋", font=("Arial", 12), command=self.undo_move)
        self.btn_undo.pack(side=tk.LEFT, padx=20)
        # =======================================================

        self.CANVAS_WIDTH = 450
        self.CANVAS_HEIGHT = 720  # 稍微缩短了一点，给上面的按钮腾地方
        self.BG_COLOR = "#CFA065"
        self.BORDER_COLOR = "#5A3A22"
        self.LINE_COLOR = "black"

        self.canvas = tk.Canvas(root, width=self.CANVAS_WIDTH, height=self.CANVAS_HEIGHT, bg=self.BG_COLOR)
        self.canvas.pack()

        # 网格参数
        self.STEP = 60
        self.CENTER_X = self.CANVAS_WIDTH // 2
        self.CENTER_Y = self.CANVAS_HEIGHT // 2
        self.START_Y = self.CENTER_Y - 4 * self.STEP
        self.RADIUS = 15

        # 核心状态
        self.board = Board()
        self.selected_point = None  # 记录当前选中的起点
        self.history = []  # 用于保存历史棋盘状态，实现悔棋

        # 绑定鼠标左键点击事件
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        # 首次渲染
        self.refresh()

    def get_xy(self, row, col):
        """根据行列获取画布上的像素坐标"""
        x = self.CENTER_X + (col - 2) * self.STEP
        y = self.START_Y + row * self.STEP
        return x, y

    def get_row_col(self, x, y):
        """根据像素坐标反推最接近的行列 (用于鼠标点击)"""
        col = round((x - self.CENTER_X) / self.STEP + 2)
        row = round((y - self.START_Y) / self.STEP)
        return row, col

    def draw_board_lines(self):
        """绘制静态的棋盘线条和背景"""
        self.canvas.delete("all")
        lw = 3

        # 边框
        self.canvas.create_rectangle(25, 30, self.CANVAS_WIDTH - 25, self.CANVAS_HEIGHT - 30,
                                     outline=self.BORDER_COLOR, width=5)

        # 中间网格线
        for r in range(2, 7):
            self.canvas.create_line(*self.get_xy(r, 0), *self.get_xy(r, 4), fill=self.LINE_COLOR, width=lw)
        for c in range(0, 5):
            self.canvas.create_line(*self.get_xy(2, c), *self.get_xy(6, c), fill=self.LINE_COLOR, width=lw)

        # 对角线
        self.canvas.create_line(*self.get_xy(2, 0), *self.get_xy(6, 4), fill=self.LINE_COLOR, width=lw)
        self.canvas.create_line(*self.get_xy(2, 4), *self.get_xy(6, 0), fill=self.LINE_COLOR, width=lw)

        # 米字格的四根斜线
        self.canvas.create_line(*self.get_xy(2, 2), *self.get_xy(4, 0), fill=self.LINE_COLOR, width=lw)
        self.canvas.create_line(*self.get_xy(2, 2), *self.get_xy(4, 4), fill=self.LINE_COLOR, width=lw)
        self.canvas.create_line(*self.get_xy(6, 2), *self.get_xy(4, 0), fill=self.LINE_COLOR, width=lw)
        self.canvas.create_line(*self.get_xy(6, 2), *self.get_xy(4, 4), fill=self.LINE_COLOR, width=lw)

        # 中轴线
        self.canvas.create_line(*self.get_xy(0, 2), *self.get_xy(8, 2), fill=self.LINE_COLOR, width=lw)

        # 上倒三角
        self.canvas.create_line(*self.get_xy(0, 0), *self.get_xy(0, 4), fill=self.LINE_COLOR, width=lw)
        self.canvas.create_line(*self.get_xy(0, 0), *self.get_xy(2, 2), fill=self.LINE_COLOR, width=lw)
        self.canvas.create_line(*self.get_xy(0, 4), *self.get_xy(2, 2), fill=self.LINE_COLOR, width=lw)
        self.canvas.create_line(*self.get_xy(1, 1), *self.get_xy(1, 3), fill=self.LINE_COLOR, width=lw)

        # 下正三角
        self.canvas.create_line(*self.get_xy(8, 0), *self.get_xy(8, 4), fill=self.LINE_COLOR, width=lw)
        self.canvas.create_line(*self.get_xy(8, 0), *self.get_xy(6, 2), fill=self.LINE_COLOR, width=lw)
        self.canvas.create_line(*self.get_xy(8, 4), *self.get_xy(6, 2), fill=self.LINE_COLOR, width=lw)
        self.canvas.create_line(*self.get_xy(7, 1), *self.get_xy(7, 3), fill=self.LINE_COLOR, width=lw)

        # 绘制当前回合提示
        if self.board.current_player == Player.black:
            turn_text = f"当前回合: 黑方 (国王)   已吃白子: {self.board.white_captured} / 11"
        elif self.board.white_reserve > 0:
            turn_text = f"当前回合: 白方 (大臣) 布置阶段   剩余预备白子: {self.board.white_reserve} / 16"
        else:
            turn_text = "当前回合: 白方 (大臣)"
        self.canvas.create_text(self.CENTER_X, 50, text=turn_text, font=("Arial", 16, "bold"), fill=self.BORDER_COLOR)

    def draw_pieces(self):
        """根据逻辑层的 board.grid 绘制棋子"""
        for r in range(9):
            for c in range(5):
                piece = self.board.grid[r][c]
                if piece is not None:
                    x, y = self.get_xy(r, c)
                    color = "black" if piece == Player.black else "white"
                    # 如果当前点被选中，外圈变红
                    outline = "red" if self.selected_point == Point(r, c) else color
                    outline_width = 3 if self.selected_point == Point(r, c) else 1

                    self.canvas.create_oval(
                        x - self.RADIUS, y - self.RADIUS, x + self.RADIUS, y + self.RADIUS,
                        fill=color, outline=outline, width=outline_width, tags="piece"
                    )

    def refresh(self):
        """刷新画布"""
        self.draw_board_lines()
        self.draw_pieces()
        self.root.update_idletasks()
        self.root.update()

    def on_canvas_click(self, event):
        """处理鼠标点击事件"""
        row, col = self.get_row_col(event.x, event.y)
        clicked_point = Point(row, col)

        if clicked_point not in VALID_POINTS:
            return

        player = self.board.current_player

        # 规则 5/6：白方布置阶段，点击任意空交叉点放置 1 颗预备白子
        if player == Player.white and self.board.white_reserve > 0:
            move = Move(place=clicked_point)
            if move in self.board.get_legal_moves(player):
                self.history.append(self.board.clone())
                self.board.do_move(move)
                self.refresh()
                self.check_game_over()
            return

        if self.selected_point is None:
            # 还没选子，尝试选中当前玩家的棋子
            if self.board.get(clicked_point) == player:
                self.selected_point = clicked_point
                self.refresh()
        else:
            # 已经选过子了
            if clicked_point == self.selected_point:
                self.selected_point = None
                self.refresh()
            else:
                move = Move(self.selected_point, clicked_point)
                legal_moves = self.board.get_legal_moves(player)

                if move in legal_moves:
                    # 走子前，把当前整个棋盘状态深拷贝存入历史记录
                    self.history.append(self.board.clone())

                    self.board.do_move(move)
                    self.selected_point = None
                    self.refresh()
                    self.check_game_over()
                else:
                    if self.board.get(clicked_point) == player:
                        self.selected_point = clicked_point
                        self.refresh()

    def check_game_over(self):
        """检查游戏是否结束"""
        is_over, winner = self.board.is_game_over()
        if is_over:
            winner_name = "黑方(国王)" if winner == Player.black else "白方(大臣)"
            messagebox.showinfo("游戏结束", f"游戏结束！赢家是: {winner_name}")
            self.reset_game()  # 游戏结束后自动重新开始

    # 重新开始功能
    def reset_game(self):
        self.board = Board()
        self.selected_point = None
        self.history.clear()  # 清空历史记录
        self.refresh()

    # 悔棋功能
    def undo_move(self):
        if self.history:
            # 弹出历史记录中的最后一步，恢复到那个状态
            self.board = self.history.pop()
            self.selected_point = None
            self.refresh()
        else:
            messagebox.showwarning("提示", "没有可悔棋的步骤了！")


if __name__ == "__main__":
    root = tk.Tk()
    app = KingdomGUI(root)
    root.mainloop()