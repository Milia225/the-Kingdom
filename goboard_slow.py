# goboard_slow.py
import copy
from gotypes import Player, Point, Move

# 定义棋盘合法点集合 (9行 x 5列)
VALID_POINTS = set()
for r in range(9):
    if r == 0 or r == 8:
        for c in [0, 2, 4]:
            VALID_POINTS.add(Point(r, c))
    elif r == 1 or r == 7:
        for c in [1, 2, 3]:
            VALID_POINTS.add(Point(r, c))
    else:  # r in 2,3,4,5,6
        for c in range(5):
            VALID_POINTS.add(Point(r, c))


def _build_adjacency():
    adj = {p: [] for p in VALID_POINTS}

    def add_edge(p1, p2):
        if p1 in VALID_POINTS and p2 in VALID_POINTS:
            adj[p1].append(p2)
            adj[p2].append(p1)

    # ================= 中间 5x5 主盘区域 =================
    # 1. 所有的横线和竖线
    for r in range(2, 7):
        for c in range(5):
            p = Point(r, c)
            if c < 4: add_edge(p, Point(r, c + 1))  # 横线
            if r < 6: add_edge(p, Point(r + 1, c))  # 竖线

    # 2. 主盘内部的斜线（根据你的精确指正，完全没有跨区块的对角线）
    # 左上角区域 (只有指向(3,1)的斜线)
    add_edge(Point(2, 0), Point(3, 1))
    add_edge(Point(2, 2), Point(3, 1))
    add_edge(Point(4, 0), Point(3, 1))
    add_edge(Point(4, 2), Point(3, 1))

    # 右上角区域 (只有指向(3,3)的斜线)
    add_edge(Point(2, 2), Point(3, 3))
    add_edge(Point(2, 4), Point(3, 3))
    add_edge(Point(4, 2), Point(3, 3))
    add_edge(Point(4, 4), Point(3, 3))

    # 左下角区域 (只有指向(5,1)的斜线)
    add_edge(Point(4, 0), Point(5, 1))
    add_edge(Point(4, 2), Point(5, 1))
    add_edge(Point(6, 0), Point(5, 1))
    add_edge(Point(6, 2), Point(5, 1))

    # 右下角区域 (只有指向(5,3)的斜线)
    add_edge(Point(4, 2), Point(5, 3))
    add_edge(Point(4, 4), Point(5, 3))
    add_edge(Point(6, 2), Point(5, 3))
    add_edge(Point(6, 4), Point(5, 3))

    # 正中心的米字格 (只有这四个点形成真正的中心X)
    # 其实上面的连入已经涵盖了这四条，但为了清晰单独列出：
    # (3,2)-(4,1), (3,2)-(4,3), (4,2)-(3,1), (4,2)-(3,3) 已经在上面连过了

    # ================= 上三角形区域 =================
    add_edge(Point(0, 0), Point(0, 2))
    add_edge(Point(0, 2), Point(0, 4))
    add_edge(Point(1, 1), Point(1, 2))
    add_edge(Point(1, 2), Point(1, 3))
    add_edge(Point(0, 2), Point(1, 2))
    add_edge(Point(1, 2), Point(2, 2))
    add_edge(Point(0, 0), Point(1, 1))
    add_edge(Point(0, 4), Point(1, 3))
    add_edge(Point(1, 1), Point(2, 2))
    add_edge(Point(1, 3), Point(2, 2))

    # ================= 下三角形区域 =================
    add_edge(Point(8, 0), Point(8, 2))
    add_edge(Point(8, 2), Point(8, 4))
    add_edge(Point(7, 1), Point(7, 2))
    add_edge(Point(7, 2), Point(7, 3))
    add_edge(Point(8, 2), Point(7, 2))
    add_edge(Point(7, 2), Point(6, 2))
    add_edge(Point(8, 0), Point(7, 1))
    add_edge(Point(8, 4), Point(7, 3))
    add_edge(Point(7, 1), Point(6, 2))
    add_edge(Point(7, 3), Point(6, 2))

    # 去重
    for p in adj:
        adj[p] = list(set(adj[p]))
    return adj


ADJACENCY = _build_adjacency()


class Board:
    def __init__(self):
        self.grid = [[None for _ in range(5)] for _ in range(9)]
        self.current_player = Player.black

        # 黑棋初始位置
        self.grid[2][2] = Player.black
        self.grid[6][2] = Player.black

        # 白棋初始位置（棋盘上先摆好 8 颗，其余 16 颗放在旁边作为预备白子）
        white_positions = [(3, 1), (3, 2), (3, 3), (4, 1), (4, 3), (5, 1), (5, 2), (5, 3)]
        for r, c in white_positions:
            self.grid[r][c] = Player.white

        # 规则 3/5/6：旁边还有 16 颗预备白子未上盘
        self.white_reserve = 16
        # 规则 7：黑棋累计吃掉的白子数量
        self.white_captured = 0

    def get(self, point: Point):
        return self.grid[point.row][point.col]

    def is_on_board(self, point: Point):
        return point in VALID_POINTS

    def get_legal_moves(self, player: Player):
        moves = []

        # 规则 6：预备的 16 颗白子没有用完时，白棋不能移动盘上的棋子，
        # 每回合只能从旁边拿 1 颗放到任意空交叉点上（规则 5）
        if player == Player.white and self.white_reserve > 0:
            for point in VALID_POINTS:
                if self.get(point) is None:
                    moves.append(Move(place=point))
            return moves

        for point in VALID_POINTS:
            if self.get(point) != player:
                continue

            for neighbor in ADJACENCY[point]:
                # 1. 自由移动一步（沿线走一格）
                if self.get(neighbor) is None:
                    moves.append(Move(point, neighbor))

                # 2. 黑棋跳吃：沿棋盘连线（横、竖、对角线均可）跳过相邻白子，
                #    落到同一直线方向上其后的空点
                elif player == Player.black and self.get(neighbor) == Player.white:
                    dr = neighbor.row - point.row
                    dc = neighbor.col - point.col
                    target = Point(neighbor.row + dr, neighbor.col + dc)
                    if self.is_on_board(target) and self.get(target) is None:
                        # 确保跳吃落点与被跳过的白子之间有连线（即沿同一直线跳）
                        if target in ADJACENCY[neighbor]:
                            moves.append(Move(point, target))
        return moves

    def do_move(self, move: Move):
        if move.is_placement:
            # 规则 5：白方从旁边的预备白子中拿 1 颗放到交叉点上
            self.grid[move.place.row][move.place.col] = Player.white
            self.white_reserve -= 1
        else:
            p_start = move.start
            p_end = move.end

            piece = self.get(p_start)
            self.grid[p_start.row][p_start.col] = None
            self.grid[p_end.row][p_end.col] = piece

            dr = p_end.row - p_start.row
            dc = p_end.col - p_start.col
            # 规则 4/5：黑棋跳吃，被跳过的白子将被吃拿到旁边
            # 跳吃是沿同一直线跨两格：横、竖 (2,0)/(0,2) 或对角线 (2,2)/(2,-2)
            if piece == Player.black and (abs(dr), abs(dc)) in [(2, 0), (0, 2), (2, 2)]:
                mid_r = (p_start.row + p_end.row) // 2
                mid_c = (p_start.col + p_end.col) // 2
                if self.grid[mid_r][mid_c] == Player.white:
                    self.grid[mid_r][mid_c] = None
                    self.white_captured += 1

        self.current_player = self.current_player.other

    def is_game_over(self):
        # 规则 7：黑棋吃掉 11 颗白子，黑胜
        if self.white_captured >= 11:
            return True, Player.black

        # 规则 7：当前行棋方无任何合法动作
        #  - 黑方被困住，既不能跳吃白棋也不能移动 -> 白胜
        #  - 白方布置完毕后无子可动（无法困住黑棋） -> 黑胜
        if not self.get_legal_moves(self.current_player):
            return True, self.current_player.other

        return False, None

    def clone(self):
        new_board = Board()
        new_board.grid = copy.deepcopy(self.grid)
        new_board.current_player = self.current_player
        new_board.white_reserve = self.white_reserve
        new_board.white_captured = self.white_captured
        return new_board