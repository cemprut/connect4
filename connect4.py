import curses as c
from itertools import cycle

class Connect4:
    def __init__(self):
        self.row_count = 6
        self.column_count = 7
        #make the board
        self.board = []
        for i in range(6):
            row_list = [0] * 7
            self.board.append(row_list)
        #players setup
        self.player_cycle = cycle([1, 2])
        self.active_player = next(self.player_cycle)
        #cursor starts in middle
        self.cursor_position = 3
        self.is_game_over = False
        self.winning_player = None
        self.message = ""
        self.should_update_screen = True

    def place_piece(self, column):
        if self.is_game_over or column < 0 or column >= self.column_count:
            return False
        #find lowest empty spot
        for r in range(self.row_count-1, -1, -1):
            if self.board[r][column] == 0:
                self.board[r][column] = self.active_player
                return True
        return False
    
    def check_win_condition(self):
        player = self.active_player
        #look for horizontal wins
        for r in range(self.row_count):
            for c in range(self.column_count - 3):
                if (self.board[r][c] == player and 
                    self.board[r][c+1] == player and 
                    self.board[r][c+2] == player and 
                    self.board[r][c+3] == player):
                    return True
        #look for vertical wins
        for r in range(self.row_count - 3):
            for c in range(self.column_count):
                if (self.board[r][c] == player and 
                    self.board[r+1][c] == player and 
                    self.board[r+2][c] == player and 
                    self.board[r+3][c] == player):
                    return True
        #look for diagonal down-right
        for r in range(self.row_count - 3):
            for c in range(self.column_count - 3):
                if (self.board[r][c] == player and 
                    self.board[r+1][c+1] == player and 
                    self.board[r+2][c+2] == player and 
                    self.board[r+3][c+3] == player):
                    return True
        #look for diagonal down-left
        for r in range(self.row_count - 3):
            for c in range(3, self.column_count):
                if (self.board[r][c] == player and 
                    self.board[r+1][c-1] == player and 
                    self.board[r+2][c-2] == player and 
                    self.board[r+3][c-3] == player):
                    return True
        return False
    
    def is_board_completely_full(self):
        for row in self.board:
            for slot in row:
                if slot == 0:
                    return False
        return True
    
    def attempt_move(self, column):
        if self.place_piece(column):
            if self.check_win_condition():
                self.is_game_over = True
                self.winning_player = self.active_player
                self.message = f"Player {self.winning_player} wins!"
            elif self.is_board_completely_full():
                self.is_game_over = True
                self.winning_player = 0
                self.message = "Game Over - It's a draw!"
            else:
                self.active_player = next(self.player_cycle)
                self.message = f"Player {self.active_player}'s turn"
            self.should_update_screen = True
            return True
        else:
            self.message = f"Player {self.active_player}'s turn | Column full!"
            self.should_update_screen = True
            return False

def draw_screen(stdscr, game):
    stdscr.clear()
    screen_height, screen_width = stdscr.getmaxyx()
    
    #figure out where to put everything
    needed_height = 16
    start_y_position = max(1, (screen_height - needed_height) // 2)
    start_x_position = max(2, (screen_width - 30) // 2)
    
    if screen_height < 20 or screen_width < 40:
        stdscr.addstr(0, 0, "Terminal too small")
        stdscr.refresh()
        return
    
    #title
    stdscr.addstr(start_y_position, start_x_position, "CONNECT 4", c.A_BOLD)
    
    #game status
    if game.is_game_over:
        stdscr.addstr(start_y_position + 1, start_x_position, game.message, c.color_pair(3))
    else:
        stdscr.addstr(start_y_position + 1, start_x_position, game.message)
    
    #column numbers at top
    column_display = " "
    for i in range(game.column_count):
        if i == game.cursor_position and not game.is_game_over:
            column_display += f"[{i}] "
        else:
            column_display += f" {i}  "
    stdscr.addstr(start_y_position + 3, start_x_position, column_display.rstrip())
    
    #draw top of game board
    stdscr.addstr(start_y_position + 4, start_x_position, "+---" * game.column_count + "+")
    
    #draw the actual board with pieces
    for row_index in range(game.row_count):
        #left side of board
        stdscr.addstr(start_y_position + 5 + row_index, start_x_position, "|")
        
        for col_index in range(game.column_count):
            cell_value = game.board[row_index][col_index]
            piece_x_pos = start_x_position + 1 + col_index * 4
            
            if cell_value == 1:
                piece_char = "●"
                piece_color = c.color_pair(1)
            elif cell_value == 2:
                piece_char = "●"
                piece_color = c.color_pair(2)
            else:
                piece_char = " "
                piece_color = 0
            
            #highlight where piece will drop
            if col_index == game.cursor_position and row_index == game.row_count - 1 and not game.is_game_over:
                stdscr.addstr(start_y_position + 5 + row_index, piece_x_pos, "[", c.color_pair(3))
                stdscr.addstr(start_y_position + 5 + row_index, piece_x_pos + 1, piece_char, piece_color)
                stdscr.addstr(start_y_position + 5 + row_index, piece_x_pos + 2, "]", c.color_pair(3))
            else:
                stdscr.addstr(start_y_position + 5 + row_index, piece_x_pos, f" {piece_char} ", piece_color)
            
            #right side of each cell
            stdscr.addstr(start_y_position + 5 + row_index, piece_x_pos + 3, "|")
        
        #lines between rows
        if row_index < game.row_count - 1:
            stdscr.addstr(start_y_position + 6 + row_index, start_x_position, "+---" * game.column_count + "+")
    
    #bottom of board
    stdscr.addstr(start_y_position + 5 + game.row_count, start_x_position, "+---" * game.column_count + "+")
    
    #instructions for player
    stdscr.addstr(start_y_position + 7 + game.row_count, start_x_position, "CONTROLS: ARROWS MOVE, SPACE/ENTER DROP, Q QUIT, R RESTART", c.color_pair(3))
    
    stdscr.addstr(start_y_position + 8 + game.row_count, start_x_position, "Note: Press R if the board isn't centered properly", c.color_pair(3))
    
    stdscr.refresh()

def main(stdscr):
    #curses setup stuff
    c.curs_set(0)
    stdscr.nodelay(1)
    stdscr.keypad(True)
    
    #setup colors if possible
    if c.has_colors():
        c.start_color()
        c.init_pair(1, c.COLOR_RED, c.COLOR_BLACK)
        c.init_pair(2, c.COLOR_YELLOW, c.COLOR_BLACK)
        c.init_pair(3, c.COLOR_CYAN, c.COLOR_BLACK)
    
    game_instance = Connect4()
    game_instance.message = f"Player {game_instance.active_player}'s turn"

    #main game loop
    while True:
        if game_instance.should_update_screen:
            draw_screen(stdscr, game_instance)
            game_instance.should_update_screen = False
        key_pressed = stdscr.getch()
        if key_pressed == ord('q'):
            break
        elif key_pressed == ord('r'):
            game_instance = Connect4()
            game_instance.message = f"Player {game_instance.active_player}'s turn"
            game_instance.should_update_screen = True
        elif not game_instance.is_game_over:
            if key_pressed == c.KEY_LEFT:
                game_instance.cursor_position = max(0, game_instance.cursor_position - 1)
                game_instance.should_update_screen = True
            elif key_pressed == c.KEY_RIGHT:
                game_instance.cursor_position = min(game_instance.column_count - 1, game_instance.cursor_position + 1)
                game_instance.should_update_screen = True
            elif key_pressed in [ord(' '), 10, 13]:
                game_instance.attempt_move(game_instance.cursor_position)

if __name__ == "__main__":
    c.wrapper(main)
