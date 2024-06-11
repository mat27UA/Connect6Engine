from tools import *

class SearchEngine():
    def __init__(self):
        self.m_board = None
        self.m_chess_type = None
        self.m_alphabeta_depth = None
        self.m_total_nodes = 0 # Número total de nodos explorados
        self.m_total_prunes = 0 # Número total de podas realizadas
        self.m_bonus_followed_busy_positions = [0, 20, 200, 1000, 4000, 10000]
        self.m_bonus_block_enemy = 10000
        self.m_bonus_center = 200
        self.transposition_table = {}

    def before_search(self, board, color, alphabeta_depth):
        self.m_board = [row[:] for row in board]
        self.m_chess_type = color
        self.m_alphabeta_depth = alphabeta_depth
        self.m_total_nodes = 0

    def alpha_beta_search(self, depth, alpha, beta, ourColor, bestMove, preMove):
        
        self.m_total_nodes += 1

        #Check game result
        if (is_win_by_premove(self.m_board, preMove)):
            if (ourColor == self.m_chess_type):
                #Opponent wins.
                return 0;
            else:
                #Self wins.
                return Defines.MININT + 1;
        
        if(self.check_first_move()):

            bestMove.positions[0].x = 10
            bestMove.positions[0].y = 10
            bestMove.positions[1].x = 10
            bestMove.positions[1].y = 10

            return Defines.MAXINT

        else:

            best_score = Defines.MININT
            best_move1, best_move2 = None

            possible_moves = find_possible_move(bestMove)
            
            for move1 in possible_moves:
                aux_move1 = StoneMove([move1, move1]) # Se define la posición de las fichas, concretamente de la primera. Haciendo inicialmente que las dos fichas se sitúen en la misma posición.
                make_move(self.m_board, aux_move1, ourColor) # Se realiza el movimiento de la primera ficha
                score1 = self.evaluate_position(ourColor, move1) # Se evalúa el valor del tablero cuando se ha situado la primera ficha

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

                        bestMove.positions[0] = move1
                        bestMove.positions[1] = move2

                        best_score = total_move_score
                        bestMove.score = best_score

                    alpha = max(alpha, best_score)
                    if beta <= alpha: # Si beta es menor o igual a alpha, se realiza una poda
                        self.m_total_prunes += 1
                        break
                
                unmake_move(self.m_board, aux_move1) # Se deshace del tablero el primer movimiento para restaurar el estado anterior

            return best_score
        
    def check_first_move(self):
        for i in range(1,len(self.m_board)-1):
            for j in range(1, len(self.m_board[i])-1):
                if(self.m_board[i][j] != Defines.NOSTONE):
                    return False
        return True
        
    def find_possible_move(self, preMove):
        
        possible_stone_moves = set()

        # Se buscan posibles movientos dentro de un área de 5x5 para cada piedra del movimiento previo.
        for stone in preMove:
            for x in range(stone.x - 2, stone.x + 3):
                for y in range(stone.y - 2, stone.y + 3):
                    if isValidPos(x, y) and self.m_board[x][y] == Defines.NOSTONE:
                        possible_stone_moves.add(StonePosition(x, y))
        
        # Añadir posiciones que tapen posibles movimientos potenciales del enemigo
         for i in range(1, len(self.m_board)-1):
            for j in range(1, len(self.m_board[i])-1):
                if self.m_board[i][j] == self.m_chess_type ^ 3:
                    for x in range(i - 1, i + 2):
                        for y in range(j - 1, j + 2):
                            if isValidPos(x, y) and self.m_board[x][y] == Defines.NOSTONE:
                                possible_stone_moves.add(StonePosition(x, y))
        
        return list(possible_stone_moves)
    
    def count_in_direction(x, y, dx, dy, ourColor):
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

    def evaluate_position(self, ourColor, move):
        
        x, y = move.x, move.y
        total_score = 0

        # Se obtiene una bonificación por la proximidad de la ficha al centro del tablero
        total_score += self.m_bonus_center / (1 + (((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5))
       
        '''
        Direcciones:
            (1, 0) --> Vertical abajo
            (0, 1) --> Horizontal derecha
            (1, 1) --> Diagonal derecha-abajo
            (-1, 1) --> Diagonal derecha-arriba

            (1, -1) --> Diagonal izquierda-abajo
            (-1, -1) --> Diagonal izquierda-arriba
            (-1, 0) --> Vertical arriba
            (0, -1) --> Horizontal izquieda
        ''' 

        for dx, dy in [(1, 0), (0, 1), (1, 1), (-1, 1), (1, -1), (-1, -1), (-1, 0), (0, -1)]:
            our_followed_busy_positions, our_open_ends = count_in_direction(x + dx, y + dy, dx, dy, ourColor)
            enemy_followed_busy_positions, enemy_open_ends = count_in_direction(x + dx, y + dy, dx, dy, ourColor ^ 3)
            
            # Se comprueba si la máquina o el enemigo tienen 6 fichas o más en dicha dirección y por tanto, habrían ganado la partida.
            if our_followed_busy_positions >= 6: 
                return Defines.MAXINT
            else if enemy_followed_busy_positions >= 6:
                return Defines.MININT

            # A continuación, si ninguno de los dos jugadores ha ganado.
            # Se obtiene la puntuación únicamente si tenemos extremos abiertos.
            if our_open_ends != 0:
                total_score += self.m_bonus_followed_busy_positions[our_followed_busy_positions]
            
            # Se comprueba si el oponente tiene líneas fuertes para bloquearlas.
            if enemy_open_ends != 0 and enemy_followed_busy_positions > 3:
                total_score += self.m_bonus_block_enemy * (enemy_followed_busy_positions - 3)

        return total_score

def flush_output():
    import sys
    sys.stdout.flush()
