import hashlib
from tools import *

class SearchEngine:
    def __init__(self):
        self.m_board = None
        self.m_chess_type = None
        self.m_alphabeta_depth = None
        self.m_total_nodes = 0  # Número total de nodos explorados
        self.m_total_prunes = 0 # Número total de podas realizadas
        self.transposition_table = {}

    def before_search(self, board, color, alphabeta_depth):
        self.m_board = [row[:] for row in board]
        self.m_chess_type = color
        self.m_alphabeta_depth = alphabeta_depth
        self.m_total_nodes = 0
        self.m_total_prunes = 0
        self.transposition_table = {}

    def hash_board(self):
        # Se genera un unico hash para la posición actual de la tabla
        return hashlib.sha256(str(self.m_board).encode()).hexdigest()

    def alpha_beta_search(self, depth, alpha, beta, ourColor, bestMove, preMove):
        
        # Se incrementa el número de nodos explorados
        self.m_total_nodes += 1

        # Se genera el hash del estado actual de la tabla
        board_hash = self.hash_board()

        # Se comprueba si el resultado de la posicion ya está calculado
        if board_hash in self.transposition_table and self.transposition_table[board_hash]['depth'] >= depth:
            return self.transposition_table[board_hash]['score']

        # Se comprueba si es el primer movimiento
        if self.check_first_move():

            bestMove.positions[0].x = 10
            bestMove.positions[0].y = 10
            bestMove.positions[1].x = 10
            bestMove.positions[1].y = 10

            return Defines.MAXINT

        # Se comprueba si la jugada previa es ganadora
        if is_win_by_premove(self.m_board, preMove):
            return Defines.MAXINT

        possible_moves = self.find_possible_move(bestMove)

        best_score = Defines.MININT
        best_move1, best_move2 = None, None

        for move1 in possible_moves:
            # No aporta valor --> se puede quitar
            aux_move1 = StoneMove([move1, move1])
            make_move(self.m_board, aux_move1, ourColor)
            score1 = self.evaluate_position(ourColor, move1)

            for move2 in possible_moves:
                if move1 != move2:
                        aux_move2 = StoneMove([move1, move2]) # Se define la posición de las dos fichas
                        make_move(self.m_board, aux_move2, ourColor) # Se realiza el movimiento de las ficha
                        score2 = self.evaluate_position(ourColor, move2) # Se evalúa el valor del tablero cuando se ha situado las dos fichas
                        
                        if depth > 1:
                            score2 -= self.alpha_beta_search(depth - 1, -beta, -alpha, ourColor ^ 3, bestMove, aux_move2)

                        total_move_score = score1 + score2 
                        unmake_move(self.m_board, aux_move2) # Se deshace del tablero el segundo movimiento para restaurar el estado anterior

                        # Si el puntaje total del movimiento actual es mejor que el mejor puntaje encontrado hasta ahora,
                        # se actualiza el mejor movimiento y su puntuación actual.
                        if best_score < total_move_score:

                            best_score = total_move_score
                            best_move1 = move1
                            best_move2 = move2

                        alpha = max(alpha, best_score)
                        if beta <= alpha: # Si beta es menor o igual a alpha, se realiza una poda
                            self.m_total_prunes += 1
                            break
                
            unmake_move(self.m_board, StoneMove([move1, move1])) # Se deshace del tablero el primer movimiento para restaurar el estado anterior

        # Se almacena el mejor movimiento
        if best_move1 and best_move2:
            bestMove.positions[0] = best_move1
            bestMove.positions[1] = best_move2
        
        bestMove.score = best_score

        self.transposition_table[board_hash] = {'score': best_score, 'depth': depth}

        return best_score

    def find_possible_move(self, preMove):
        
        possible_stone_moves = set()

        # Se buscan posibles movientos dentro de un área de 5x5 para cada piedra del movimiento previo.
        for stone in preMove.positions:
            for x in range(stone.x - 2, stone.x + 3):
                for y in range(stone.y - 2, stone.y + 3):
                    if isValidPos(x, y) and self.m_board[x][y] == Defines.NOSTONE:
                        possible_stone_moves.add(StonePosition(x, y))
        
        # Añadir posiciones que tapen posibles movimientos potenciales del enemigo
        for i in range(len(self.m_board)):
            for j in range(len(self.m_board[i])):
                if self.m_board[i][j] == self.m_chess_type ^ 3:
                    for x in range(i - 1, i + 2):
                        for y in range(j - 1, j + 2):
                            if isValidPos(x, y) and self.m_board[x][y] == Defines.NOSTONE:
                                possible_stone_moves.add(StonePosition(x, y))
        
        return list(possible_stone_moves)
    
    def count_in_direction(self, x, y, dx, dy, ourColor):
        followed_busy_positions, open_ends = 0, 0
        
        # Se verifica el número de piezas del color seguidas en la dirección especificada
        while isValidPos(x, y) and self.m_board[x][y] == ourColor: # Añadir un and free_positions_count < 5
            followed_busy_positions += 1
            x += dx
            y += dy

        # Se verifican si los extremos están abiertos
        if isValidPos(x, y) and self.m_board[x][y] == Defines.NOSTONE:
            open_ends += 1

        return followed_busy_positions, open_ends
    
    def agrupated(self, x, y, dx, dy, ourColor):
        followed_points, open_ends = self.count_in_direction(x + dx, y + dy, dx, dy, ourColor)
        followed_points_reverse, open_ends_reverse = self.count_in_direction(x - dx, y - dy, -dx, -dy, ourColor)
        total_followed_points = followed_points + followed_points_reverse
        total_open_ends = open_ends + open_ends_reverse
        return total_followed_points, total_open_ends

    def evaluate_position(self, ourColor, preMove):
        BONUS_BUSY_POSITION = [0, 1, 10, 50, 200, 500]
        BONUS_BLOCK_ENEMY = 350
        BONUS_CENTER = 10
        
        BONUS_ATTACK = 400  # Nuevo bono para posiciones ofensivas

        x, y = preMove.x, preMove.y
        total_score = 0
        
        for dx, dy in [(1, 0), (0, 1), (1, 1), (-1, 1), (1, -1), (-1, -1), (-1, 0), (0, -1)]:
            our_total_count, our_total_open_ends = self.agrupated(x, y, dx, dy, ourColor)
            enemy_total_count,  enemy_total_open_ends = self.agrupated(x, y, dx, dy, ourColor ^ 3)

            if our_total_count >= 6:
                return float('inf') 
            if enemy_total_count >= 6:
                return float('-inf')
            
            total_score += BONUS_BUSY_POSITION[our_total_count] * our_total_open_ends
            
            # Añadir bonificaciones ofensivas
            if our_total_count > 3 and our_total_open_ends > 0:
                total_score += BONUS_ATTACK * (our_total_count - 3)

            elif enemy_total_count > 3 and enemy_total_open_ends > 0:
                total_score += BONUS_BLOCK_ENEMY * (enemy_total_count - 3)            

        distance_to_center = ((x - 9) ** 2 + (y - 9) ** 2) ** 0.5
        center_bonus = BONUS_CENTER / (1 + distance_to_center)

        return total_score + center_bonus

    def check_first_move(self):
        # Se comprueba si es el primer movimiento del juego
        for i in range(1, len(self.m_board) - 1):
            for j in range(1, len(self.m_board[i]) - 1):
                if self.m_board[i][j] != Defines.NOSTONE:
                    return False
        return True