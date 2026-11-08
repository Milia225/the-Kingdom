# dlgo/gotypes.py
import enum
from collections import namedtuple


class Player(enum.Enum):
    """定义玩家"""
    black = 1  # 黑方（国王）
    white = 2  # 白方（大臣）

    @property
    def other(self):
        return Player.black if self == Player.white else Player.white


class Point(namedtuple('Point', 'row col')):
    """
    定义棋盘坐标。
    行 (row): 0 到 8
    列 (col): 0 到 4
    """

    def neighbors(self):
        # 这个方法在下面 goboard_slow.py 中会配合邻接表覆盖使用
        pass


class Move:
    """
    定义一个动作。对于双王棋（国王与大臣棋），一个动作是：
    - 移动: 起点 start -> 终点 end（黑方普通移动/跳吃，白方布置完毕后的移动）
    - 放置: place = Point（白方在预备的 16 颗白子用完之前，
      每回合从旁边拿 1 颗白子放到任意空交叉点上）
    """

    def __init__(self, start: Point = None, end: Point = None, place: Point = None):
        self.start = start
        self.end = end
        self.place = place

    @property
    def is_placement(self):
        """是否为白方放置预备白子的动作"""
        return self.place is not None

    def __eq__(self, other):
        return (isinstance(other, Move)
                and self.start == other.start
                and self.end == other.end
                and self.place == other.place)

    def __hash__(self):
        return hash((self.start, self.end, self.place))

    def __repr__(self):
        if self.is_placement:
            return f"Move(place white @ {self.place})"
        return f"Move({self.start} -> {self.end})"