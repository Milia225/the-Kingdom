# main.py
import random
import tkinter as tk
from gotypes import Player, Point, Move
from goboard_slow import Board, VALID_POINTS, ADJACENCY
from gui import KingdomGUI


def print_board(board):
    """
    在控制台打印棋盘，方便调试规则。
    K = 国王 (黑方)
    M = 大臣 (白方)
    . = 空位
    (空格表示该位置没有交叉点)
    """
    print("\n   0 1 2 3 4  <- 列(Col)")
    for r in range(9):
        row_str = f"{r}  "
        for c in range(5):
            p = Point(r, c)
            if p not in VALID_POINTS:
                row_str += "  "  # 无效点留空
            else:
                piece = board.get(p)
                if piece is None:
                    row_str += ". "
                elif piece == Player.black:
                    row_str += "K "
                elif piece == Player.white:
                    row_str += "M "
        print(row_str)
    print("----------------------")


def test_console():
    """保留你原来的控制台测试逻辑"""
    print("=== 国王与大臣棋 规则引擎测试 ===")

    # 1. 初始化棋盘
    board = Board()
    print("\n[1] 初始布局 (图2-1):")
    print_board(board)

    # 2. 测试获取合法动作
    current_player = board.current_player
    legal_moves = board.get_legal_moves(current_player)
    print(f"[2] 当前玩家: {current_player.name}")
    print(f"    共有 {len(legal_moves)} 种合法走法。")

    if len(legal_moves) > 0:
        print(f"    示例走法: {legal_moves[0]}")

    # 3. 模拟双方随机走子
    print("\n[3] 开始模拟随机对弈 (最多 10 步):")
    step = 1
    while step <= 10:
        is_over, winner = board.is_game_over()
        if is_over:
            print(f"\n游戏结束！赢家是: {winner.name if winner else '平局'}")
            break

        current_player = board.current_player
        legal_moves = board.get_legal_moves(current_player)

        if not legal_moves:
            print(f"{current_player.name} 无路可走，游戏结束。")
            break

        move = random.choice(legal_moves)
        print(f"步骤 {step} ({current_player.name}): {move}")
        board.do_move(move)
        print_board(board)
        step += 1
    print("\n[4] 测试结束。底层规则引擎运行正常！")


if __name__ == '__main__':
    # 如果你想测试控制台，可以把下面这行取消注释，注释掉 GUI 的三行
    # test_console() 
    
    # 默认启动图形界面
    root = tk.Tk()
    app = KingdomGUI(root)
    root.mainloop()