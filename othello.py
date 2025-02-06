import numpy as np
import math

# Constants
BLACK, WHITE, EMPTY = 0, 1, 2
DIRECTIONS = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

# Grid score
SCORES = [
    [100, -20, 10,  5,  5, 10, -20, 100],
    [-20, -50, -2, -2, -2, -2, -50, -20],
    [ 10,  -2,  5,  1,  1,  5,  -2,  10],
    [  5,  -2,  1,  2,  2,  1,  -2,   5],
    [  5,  -2,  1,  2,  2,  1,  -2,   5],
    [ 10,  -2,  5,  1,  1,  5,  -2,  10],
    [-20, -50, -2, -2, -2, -2, -50, -20],
    [100, -20, 10,  5,  5, 10, -20, 100]
]

class Othello:
    def __init__(self):
        self.board = self.initialize_board()
        self.current_player = BLACK
        self.human_player = None

    def initialize_board(self):
        board = np.full((8, 8), EMPTY)
        board[3, 3], board[4, 4] = WHITE, WHITE
        board[3, 4], board[4, 3] = BLACK, BLACK
        return board

    def is_valid_move(self, board, row, col, player):
        if board[row, col] != EMPTY:
            return False
        
        opponent = WHITE if player == BLACK else BLACK
        for dr, dc in DIRECTIONS:
            r, c = row + dr, col + dc
            found_opponent = False
            
            while 0 <= r < 8 and 0 <= c < 8 and board[r, c] == opponent:
                found_opponent = True
                r, c = r + dr, c + dc
                
            if found_opponent and 0 <= r < 8 and 0 <= c < 8 and board[r, c] == player:
                return True
        return False

    def get_valid_moves(self, board, player):
        return [(r, c) for r in range(8) for c in range(8) 
                if self.is_valid_move(board, r, c, player)]

    def apply_move(self, board, row, col, player):
        board[row, col] = player
        opponent = WHITE if player == BLACK else BLACK
        
        for dr, dc in DIRECTIONS:
            r, c = row + dr, col + dc
            cells_to_flip = []
            
            while 0 <= r < 8 and 0 <= c < 8 and board[r, c] == opponent:
                cells_to_flip.append((r, c))
                r, c = r + dr, c + dc
                
            if cells_to_flip and 0 <= r < 8 and 0 <= c < 8 and board[r, c] == player:
                for flip_r, flip_c in cells_to_flip:
                    board[flip_r, flip_c] = player

    def heuristic(self, board, player):
        opponent = BLACK if player == WHITE else WHITE
        score = 0

        # Positional values from SCORES matrix
        for i in range(8):
            for j in range(8):
                if board[i][j] == BLACK:
                    score += SCORES[i][j]
                elif board[i][j] == WHITE:
                    score -= SCORES[i][j]

        # Number of possible moves for both players
        player_moves = len(self.get_valid_moves(board, player))
        opponent_moves = len(self.get_valid_moves(board, opponent))
        score += (player_moves - opponent_moves) * 5 # Weighted difference

        return score if player == BLACK else -score

    def minimax(self, board, depth, alpha, beta, maximizing_player, player):
        if depth == 0:
            return self.heuristic(board, player), None

        valid_moves = self.get_valid_moves(board, player)
        if not valid_moves:
            opponent = WHITE if player == BLACK else BLACK
            if not self.get_valid_moves(board, opponent):  # If opponent also has no moves, return heuristic
                return self.heuristic(board, player), None
            return self.minimax(board, depth - 1, alpha, beta, not maximizing_player, opponent)

        best_move = None
        if maximizing_player:
            max_eval = -math.inf
            for move in valid_moves:
                new_board = board.copy()
                self.apply_move(new_board, move[0], move[1], player)
                eval, _ = self.minimax(new_board, depth - 1, alpha, beta, False, 
                                     WHITE if player == BLACK else BLACK)
                if eval > max_eval:
                    max_eval = eval
                    best_move = move
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval, best_move
        else:
            min_eval = math.inf
            for move in valid_moves:
                new_board = board.copy()
                self.apply_move(new_board, move[0], move[1], player)
                eval, _ = self.minimax(new_board, depth - 1, alpha, beta, True, 
                                     WHITE if player == BLACK else BLACK)
                if eval < min_eval:
                    min_eval = eval
                    best_move = move
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval, best_move

    def print_board(self):
        symbols = {BLACK: '⚫', WHITE: '⚪', EMPTY: '· '}
        # Código de color ANSI para rojo
        RED = '\033[91m'
        # Código para resetear el color
        RESET = '\033[0m'
        
        print("  " + " ".join(str(i) + " " for i in range(8)))
        
        # Obtener movimientos válidos para el jugador actual
        valid_moves = self.get_valid_moves(self.board, self.current_player)
        
        for i, row in enumerate(self.board):
            print(f"{i} ", end='')
            for j, cell in enumerate(row):
                if (i, j) in valid_moves:
                    print(f'{RED}X {RESET}', end=' ')
                else:
                    print(symbols[cell], end=' ')
            print()
        
        black_count = np.sum(self.board == BLACK)
        white_count = np.sum(self.board == WHITE)
        print(f"Score -> Black: {black_count}, White: {white_count}\n")

    def play_game(self):
        print("Welcome to Othello!")
        self.human_player = BLACK if input("Play as Black (B) or White (W)? ").upper() == 'B' else WHITE

        while True:
            self.print_board()
            valid_moves = self.get_valid_moves(self.board, self.current_player)
            
            if not valid_moves:
                if not self.get_valid_moves(self.board, WHITE if self.current_player == BLACK else BLACK):
                    break
                print(f"No valid moves for {'Black' if self.current_player == BLACK else 'White'}")
                self.current_player = WHITE if self.current_player == BLACK else BLACK
                continue

            if self.current_player == self.human_player:
                print("Valid moves:", valid_moves)
                while True:
                    try:
                        row, col = map(int, input("Enter move (row col): ").split())
                        if (row, col) in valid_moves:
                            break
                        print("Invalid move")
                    except ValueError:
                        print("Invalid input")
                self.apply_move(self.board, row, col, self.current_player)
            else:
                print("AI thinking...")
                _, move = self.minimax(self.board, 4, -math.inf, math.inf, True, self.current_player)
                if move:
                    print(f"AI plays: {move}")
                    self.apply_move(self.board, move[0], move[1], self.current_player)

            self.current_player = WHITE if self.current_player == BLACK else BLACK

        # Game over
        self.print_board()
        black_count = np.sum(self.board == BLACK)
        white_count = np.sum(self.board == WHITE)
        print(f"Game Over! Black: {black_count}, White: {white_count}")
        if black_count > white_count:
            print("Black wins!")
        elif white_count > black_count:
            print("White wins!")
        else:
            print("Draw!")

if __name__ == "__main__":
    game = Othello()
    game.play_game() 