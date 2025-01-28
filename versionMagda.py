import numpy as np
import math

# Constants
EMPTY, BLACK, WHITE = 0, 1, 2
DIRECTIONS = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]


class Othello:
    def __init__(self):
        self.board = self.initialize_board()
        self.current_player = BLACK
        self.human_player = None

    def initialize_board(self):
        board = np.zeros((8, 8), dtype=int)
        board[3, 3], board[4, 4] = WHITE, WHITE
        board[3, 4], board[4, 3] = BLACK, BLACK
        return board

    def is_valid_move(self, board, row, col, player):
        if board[row, col] != EMPTY: # If the cell is not empty, it's not a valid move
            return False
        opponent = BLACK if player == WHITE else WHITE

        for dr, dc in DIRECTIONS: # Check in all directions
            r = row + dr
            c = col + dc
            found_opponent = False

            while 0 <= r < 8 and 0 <= c < 8 and board[r, c] == opponent: # Keep going in the direction of opponent's pieces
                found_opponent = True
                r = r + dr
                c = c + dc

            if found_opponent and 0 <= r < 8 and 0 <= c < 8 and board[r, c] == player: # If we found opponent's pieces followed by player's piece
                return True

        return False

    def get_valid_moves(self, board, player): # The game will print on screen the valid moves for the player
        moves = [(r, c) for r in range(8) for c in range(8) if self.is_valid_move(board, r, c, player)]
        return moves

    def apply_move(self, board, row, col, player):
        board[row, col] = player
        opponent = BLACK if player == WHITE else WHITE

        for dr, dc in DIRECTIONS:
            r = row + dr
            c = col + dc
            cells_to_flip = []

            while 0 <= r < 8 and 0 <= c < 8 and board[r, c] == opponent:
                cells_to_flip.append((r, c))
                r = r + dr
                c = c + dc

            if cells_to_flip and 0 <= r < 8 and 0 <= c < 8 and board[r, c] == player:
                for rr, cc in cells_to_flip:
                    board[rr, cc] = player

    def score(self, board):
        black_score = np.sum(board == BLACK)
        white_score = np.sum(board == WHITE)
        return black_score, white_score

    def is_terminal(self, board):
        return not self.get_valid_moves(board, BLACK) and not self.get_valid_moves(board, WHITE)

    def minimax(self, board, depth, alpha, beta, maximizing_player):
        if depth == 0 or self.is_terminal(board):
            return self.score(board)[0] - self.score(board)[1], None

        valid_moves = self.get_valid_moves(board, BLACK if maximizing_player else WHITE)
        if not valid_moves:
            return self.minimax(board, depth - 1, alpha, beta, not maximizing_player)[0], None

        best_move = None

        if maximizing_player:
            max_eval = -math.inf
            for move in valid_moves:
                new_board = board.copy()
                self.apply_move(new_board, move[0], move[1], BLACK)
                eval, _ = self.minimax(new_board, depth - 1, alpha, beta, False)
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
                self.apply_move(new_board, move[0], move[1], WHITE)
                eval, _ = self.minimax(new_board, depth - 1, alpha, beta, True)
                if eval < min_eval:
                    min_eval = eval
                    best_move = move
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval, best_move

    def print_board(self):
        symbols = {EMPTY: '.', BLACK: 'B', WHITE: 'W'}
        print("  " + " ".join(map(str, range(8))))
        for i, row in enumerate(self.board):
            print(f"{i} " + ' '.join(symbols[cell] for cell in row))
        black_score, white_score = self.score(self.board)
        print(f"Score -> Black: {black_score}, White: {white_score}")
        print()

    def play_game(self):
        print("Welcome to Othello!")
        self.human_player = BLACK if input(
            "Do you want to play as Black (B) or White (W)? ").strip().upper() == 'B' else WHITE

        while not self.is_terminal(self.board):
            self.print_board()
            valid_moves = self.get_valid_moves(self.board, self.current_player)

            if not valid_moves:
                print("No valid moves available. Skipping turn.")
                self.current_player = BLACK if self.current_player == WHITE else WHITE
                continue

            if self.current_player == self.human_player:
                print("Your turn.")
                print("Valid moves: ", valid_moves)
                while True:
                    try:
                        row, col = map(int, input("Enter your move (row and column): ").split())
                        if (row, col) in valid_moves:
                            break
                        else:
                            print("Invalid move. Try again.")
                    except ValueError:
                        print("Invalid input. Enter row and column as two numbers separated by a space.")
                self.apply_move(self.board, row, col, self.human_player)
            else:
                print("AI is thinking...")
                _, move = self.minimax(self.board, 4, -math.inf, math.inf, self.current_player == BLACK)
                if move:
                    print(f"AI chose move: {move}")
                    self.apply_move(self.board, move[0], move[1], self.current_player)

            self.current_player = BLACK if self.current_player == WHITE else WHITE

        self.print_board()
        black_score, white_score = self.score(self.board)
        print("Game over!")
        print(f"Black: {black_score}, White: {white_score}")
        if black_score > white_score:
            print("Black wins!")
        elif white_score > black_score:
            print("White wins!")
        else:
            print("It's a draw!")


# Run the game
if __name__ == "__main__":
    game = Othello()
    game.play_game()