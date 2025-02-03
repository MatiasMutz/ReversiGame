import numpy as np
import math

# Constants
BLACK, WHITE, EMPTY = 0, 1, 2
DIRECTIONS = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

SCORES = [
    [100, -25, 10,  5,  5, 10, -25, 100],
    [-25, -50,  0,  0,  0,  0, -50, -25],
    [10,   0,  5,  1,  1,  5,  0,  10],
    [ 5,   0,  1,  2,  2,  1,  0,   5],
    [ 5,   0,  1,  2,  2,  1,  0,   5],
    [10,   0,  5,  1,  1,  5,  0,  10],
    [-25, -50,  0,  0,  0,  0, -50, -25],
    [100, -25, 10,  5,  5, 10, -25, 100]
]

class Othello:
    def __init__(self):
        self.board = self.initialize_board()
        self.current_player = BLACK
        self.human_player = None

    def initialize_board(self):
        board = np.full((8, 8), EMPTY)
        board[3, 3], board[4, 4] = WHITE, WHITE # Initial positions of white pieces
        board[3, 4], board[4, 3] = BLACK, BLACK # Initial positions of black pieces
        return board

    def is_valid_move(self, board, row, col, player):
        if board[row, col] != EMPTY: # If the cell is not empty, it's not a valid move
            return False
        opponent = not player # The opponent is the other player

        for dr, dc in DIRECTIONS: # Check in all directions
            r = row + dr
            c = col + dc
            found_opponent = False

            while 0 <= r < 8 and 0 <= c < 8 and board[r, c] == opponent: # Keep going in the direction of opponent's pieces
                found_opponent = True
                r = r + dr
                c = c + dc

            if found_opponent and 0 <= r < 8 and 0 <= c < 8 and board[r, c] == player: # If we found opponent's pieces followed by player's piece
                return True # This is the only case where the move is valid

        return False

    def get_valid_moves(self, board, player): # The game will print on screen the valid moves for the player
        moves = [(r, c) for r in range(8) for c in range(8) if self.is_valid_move(board, r, c, player)]
        return moves

    def apply_move(self, board, row, col, player):
        board[row, col] = player
        opponent = not player

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

    def get_scores(self, valid_moves):
        scores = []
        for move in valid_moves:
            score = SCORES[move[0]][move[1]]
            scores.append(score)
        return scores

    def min_player(self, board, depth, alpha, beta, color):
        valid_moves = self.get_valid_moves(board, color)
        if not valid_moves:
            return -math.inf, None

        best_move = None

        min_score = math.inf

        for move in valid_moves:
            new_board = board.copy()
            self.apply_move(new_board, move[0], move[1], color)
            if depth == 0:
                return SCORES[move[0]][move[1]], move
            score, best_move = self.max_player(new_board, depth - 1, alpha, beta, color)
            if score < min_score:
                min_score = score
                best_move = move
            if score < alpha:
                break
            beta = min(beta, score)
        return min_score, best_move

    def max_player(self, board, depth, alpha, beta, color):
        valid_moves = self.get_valid_moves(board, color)
        if not valid_moves:
            return math.inf, None

        best_move = None

        max_score = -math.inf

        for move in valid_moves:
            new_board = board.copy()
            self.apply_move(new_board, move[0], move[1], color)
            if depth == 0:
                return SCORES[move[0]][move[1]], move
            score, best_move = self.min_player(new_board, depth - 1, alpha, beta, color)
            if score > max_score:
                max_score = score
                best_move = move
            if score > beta:
                break
            alpha = max(alpha, score)
        return max_score, best_move

    def minimax(self, board, depth, alpha, beta, maximizing_player, color):
        valid_moves = self.get_valid_moves(board, color)
        print("valid_moves", valid_moves)
        if not valid_moves:
            return self.minimax(board, depth - 1, alpha, beta, not maximizing_player, not color), None

        best_move = None

        max_score = -math.inf
        min_score = math.inf

        for move in valid_moves:
            new_board = board.copy()
            self.apply_move(new_board, move[0], move[1], color)
            if maximizing_player:
                score, _ = self.min_player(new_board, depth, alpha, beta, color)
                if score is None:
                    continue
                if score > max_score:
                    max_score = score
                    best_move = move
            else:
                score, _ = self.max_player(new_board, depth, alpha, beta, color)
                if score is None:
                    continue
                if score < min_score:
                    min_score = score
                    best_move = move

        return max_score if maximizing_player else min_score, best_move

    def print_board(self):
        symbols = {BLACK: 'B', WHITE: 'W', EMPTY: '.'}
        print("  " + " ".join(map(str, range(8))))
        for i, row in enumerate(self.board):
            print(f"{i} " + ' '.join(symbols[cell] for cell in row))
        black_score, white_score = self.score(self.board)
        print(f"Score -> Black: {black_score}, White: {white_score}")
        print()

    def play_game(self):
        print("Welcome to Othello!")
        self.human_player = BLACK if input(
            "Do you want to play as Black (B) or White (W)? ").strip().upper() == 'B' else WHITE # The player can choose to play as Black or White

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
                _, move = self.minimax(self.board, 2, -math.inf, math.inf, True, not self.human_player)
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