class Defines:
    GRID_NUM=21          # Number of the board, 19*19 plus edges.
    GRID_COUNT=361         # Sum of the points in the board.
    BLACK=1           # Black flag in the board.
    WHITE=2           # White flag in the board.
    BORDER=3          # Border flag in the board.
    NOSTONE=0           # Empty flag.
    MSG_LENGTH=512 #Tamaño del mensaje
    GRID_NUM=21 #Number of the board, 19*19 plus edges.
    GRID_COUNT=361 #Sum of the points in the board.
    LOG_FILE="tia-matmrm-engine.log"
    ENGINE_NAME="matmrm"
    # Max values in the evaluation.
    MAXINT=20000
    MININT=-20000


class StonePosition:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        if not isinstance(other, StonePosition):
            return False
        return self.x == other.x and self.y == other.y

    def __ne__(self, other_StonePosition):
        if not isinstance(other_StonePosition, StonePosition):
            return False
        return self.x != other_StonePosition.x or self.y != other_StonePosition.y

    def __hash__(self):
        return hash(f'{self.x}{self.y}')

class StoneMove:
    def __init__(self, positions=[StonePosition(0, 0), StonePosition(0, 0)]):
        self.positions = positions
        self.score = 0

class Chess:
    def __init__(x,y,score):
        self.x = x
        self.y = y
        self.score = score
