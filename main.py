import tkinter as tk
from tkinter import messagebox
import time
import copy
from itertools import product
import os
import sys

class OthelloGUI:
    def __init__(self):
        self.game = None
        self.window = tk.Tk()
        self.window.title("Othello")
        
        # Create color selection buttons
        self.color_frame = tk.Frame(self.window)
        self.color_frame.pack(pady=10)
        self.black_button = tk.Button(self.color_frame, text="Play as Black", 
                                    command=lambda: self.start_game('B'))
        self.black_button.pack(side=tk.LEFT, padx=10)
        self.white_button = tk.Button(self.color_frame, text="Play as White",
                                    command=lambda: self.start_game('W'))
        self.white_button.pack(side=tk.LEFT, padx=10)
        
        # Create score labels
        self.score_frame = tk.Frame(self.window)
        self.score_frame.pack(pady=10)
        self.black_score = tk.Label(self.score_frame, text="Black: 2")
        self.black_score.pack(side=tk.LEFT, padx=20)
        self.white_score = tk.Label(self.score_frame, text="White: 2") 
        self.white_score.pack(side=tk.LEFT, padx=20)
        
        # Create game board
        self.board_frame = tk.Frame(self.window)
        self.board_frame.pack()
        
        self.buttons = []
        for i in range(8):
            row = []
            for j in range(8):
                button = tk.Button(self.board_frame, width=4, height=2,
                                 command=lambda x=i, y=j: self.handle_click(x, y))
                button.grid(row=i, column=j, padx=1, pady=1)
                row.append(button)
            self.buttons.append(row)
            
        # Start game as black by default
        self.start_game('B')
            
    def update_board(self):
        valid_moves = self.game.valid_moves(self.game.current_player)
        
        for i in range(8):
            for j in range(8):
                cell = self.game.board[i][j]
                if cell == 'B':
                    self.buttons[i][j].configure(bg='black', fg='white', text='●')
                elif cell == 'W':
                    self.buttons[i][j].configure(bg='white', fg='black', text='○')
                else:
                    self.buttons[i][j].configure(bg='green', text='', fg='black')
                    if (i,j) in valid_moves:
                        self.buttons[i][j].configure(text='✗', fg='red')
                    
        b_count, w_count = self.game.score()
        self.black_score.configure(text=f"Black: {b_count}")
        self.white_score.configure(text=f"White: {w_count}")
        
    def handle_click(self, x, y):
        if self.game.current_player != self.player_color:
            return
            
        valid_moves = self.game.valid_moves(self.game.current_player)
        if (x, y) in valid_moves:
            self.game.make_move((x, y))
            self.update_board()
            self.game.current_player = self.game.opponent()
            
            if not self.game.game_over():
                self.window.after(500, self.make_computer_move)
            else:
                self.game_over()
                
    def make_computer_move(self):
        move = self.game.best_move()
        if move:
            self.game.make_move(move)
            self.update_board()
            self.game.current_player = self.game.opponent()
            
            if self.game.game_over():
                self.game_over()
                
    def game_over(self):
        b_count, w_count = self.game.score()
        winner = "Black" if b_count > w_count else "White" if w_count > b_count else "Draw"
        message = f"Game Over!\nBlack: {b_count}\nWhite: {w_count}\n"
        message += f"Winner: {winner}" if winner != "Draw" else "It's a Draw!"
        messagebox.showinfo("Game Over", message)
        
    def start_game(self, color):
        self.player_color = color
        self.game = Othello()
        self.update_board()
        # If player chose white, make computer's first move as black
        if color == 'W':
            self.window.after(500, self.make_computer_move)
            
    def run(self):
        self.window.mainloop()

class Othello:
    def __init__(self, time_limit=5):
        self.board = [[None] * 8 for _ in range(8)]
        self.board[3][3], self.board[4][4] = 'W', 'W'
        self.board[3][4], self.board[4][3] = 'B', 'B'
        self.current_player = 'B'  # Black always starts
        self.time_limit = time_limit

    def opponent(self):
        return 'W' if self.current_player == 'B' else 'B'

    def valid_moves(self, player):
        moves = []
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

        for x, y in product(range(8), repeat=2):
            if self.board[x][y]:
                continue

            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 0 <= nx < 8 and 0 <= ny < 8 and self.board[nx][ny] == self.opponent():
                    while 0 <= nx < 8 and 0 <= ny < 8:
                        if not self.board[nx][ny]:
                            break
                        if self.board[nx][ny] == player:
                            moves.append((x, y))
                            break
                        nx, ny = nx + dx, ny + dy

        return list(set(moves))

    def make_move(self, move):
        x, y = move
        self.board[x][y] = self.current_player
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            flip_positions = []
            while 0 <= nx < 8 and 0 <= ny < 8:
                if not self.board[nx][ny]:
                    break
                if self.board[nx][ny] == self.current_player:
                    for fx, fy in flip_positions:
                        self.board[fx][fy] = self.current_player
                    break
                flip_positions.append((nx, ny))
                nx, ny = nx + dx, ny + dy

    def game_over(self):
        return not self.valid_moves('B') and not self.valid_moves('W')

    def score(self):
        b_count = sum(row.count('B') for row in self.board)
        w_count = sum(row.count('W') for row in self.board)
        return b_count, w_count

    def minimax(self, board, depth, alpha, beta, maximizing_player, start_time):
        if depth == 0 or time.time() - start_time > self.time_limit:
            return self.evaluate(board)

        valid_moves = self.valid_moves(self.current_player if maximizing_player else self.opponent())
        if not valid_moves:
            return self.evaluate(board)

        if maximizing_player:
            max_eval = float('-inf')
            for move in valid_moves:
                temp_board = copy.deepcopy(self.board)
                self.make_move(move)
                eval = self.minimax(temp_board, depth - 1, alpha, beta, False, start_time)
                self.board = temp_board
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for move in valid_moves:
                temp_board = copy.deepcopy(self.board)
                self.make_move(move)
                eval = self.minimax(temp_board, depth - 1, alpha, beta, True, start_time)
                self.board = temp_board
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval

    def best_move(self):
        valid_moves = self.valid_moves(self.current_player)
        best_score = float('-inf')
        best_move = None
        start_time = time.time()

        for move in valid_moves:
            temp_board = copy.deepcopy(self.board)
            self.make_move(move)
            score = self.minimax(temp_board, 3, float('-inf'), float('inf'), False, start_time)
            self.board = temp_board
            if score > best_score:
                best_score = score
                best_move = move

        return best_move

    def evaluate(self, board):
        b_count, w_count = self.score()
        return b_count - w_count if self.current_player == 'B' else w_count - b_count

if __name__ == "__main__":
    gui = OthelloGUI()
    gui.run()
