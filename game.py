from board import ConnectFourBoard, InvalidMoveError
from player import ConsolePlayer, CPUPlayer, MatplotlibPlayer
from board_gui import draw_board, select_display_mode, select_opponent_type, select_play_again, animate_drop, draw_board_full, draw_pieces
import matplotlib.pyplot as plt

class ConnectFourGame:
    def __init__(self, display_mode, rows=6, cols=7, p1_type=ConsolePlayer, p2_type=ConsolePlayer):
        self.board = ConnectFourBoard(rows, cols)
        self.display_mode = display_mode

        if self.display_mode == 'matplotlib':
            p1_symbol = 'X'
            p2_symbol = 'O'
        else:
            p1_symbol = self.get_player_symbol("Player 1")
            p2_symbol = self.get_player_symbol("Player 2")
            while p2_symbol == p1_symbol:
                print("Player 2 can't have the same symbol as Player 1!")
                p2_symbol = self.get_player_symbol("Player 2")

        self.fig = None
        self.ax = None
        self.color_map = None

        if self.display_mode == 'matplotlib':
            self.fig, self.ax = plt.subplots()
            self.color_map = {
                ' ': ('white', '#01115e'),
                p1_symbol: ('red', 'darkred'),
                p2_symbol: ('yellow', 'goldenrod')
            }
            if p1_type is not CPUPlayer:
                p1_type = MatplotlibPlayer
            if p2_type is not CPUPlayer:
                p2_type = MatplotlibPlayer

        def make_player(p_type, name, symbol):
            if p_type is MatplotlibPlayer:
                return p_type(name=name, symbol=symbol, fig=self.fig, ax=self.ax, color_map=self.color_map)
            else:
                return p_type(name=name, symbol=symbol)

        self.player_1 = make_player(p1_type, 'Player 1', p1_symbol)
        self.player_2 = make_player(p2_type, 'Player 2', p2_symbol)

        self.turn = 0

    def start(self):
        self.board.clear()
        self.turn = 0

        if self.display_mode == 'matplotlib':
            plt.close(self.fig)
            self.fig, self.ax = plt.subplots()

            # Update the Matplotlib players to use the new figure/axes
            self.player_1.fig = self.fig
            self.player_1.ax = self.ax
            self.player_2.fig = self.fig
            self.player_2.ax = self.ax

        winner = None

        while not self.board.is_full():
            match self.turn % 2:
                case 0:
                    current_player = self.player_1
                case 1:
                    current_player = self.player_2
            print(f"{current_player.name}'s turn.")

            if self.display_mode == 'console':
                self.board.display()
            else:
                draw_board_full(self.ax, self.board, self.color_map)
                self.ax.set_title(f"{current_player.name}'s turn")
                self.fig.canvas.draw_idle()

            move_is_invalid = True
            while move_is_invalid:
                col = current_player.move(board=self.board)
                landing_row = self.board.get_landing_row(col)
            
                if landing_row is not None and self.display_mode == 'matplotlib':
                    animate_drop(self.ax, self.fig, self.board, self.color_map, col, landing_row, current_player.symbol)
                    draw_pieces(self.ax, self.board, self.color_map, col)
            
                try:
                    self.board.add_piece(col, current_player.symbol)
                    move_is_invalid = False
                except InvalidMoveError as err:
                    print(str(err))

            self.turn += 1

            if self.board.check_winner():
                winner = current_player
                print(f'{current_player.name} wins!')
                break
        else:
            print('No winner!')

        if self.display_mode == 'matplotlib':
            #draw_board(self.ax, self.board, self.color_map)
            if winner:
                self.ax.set_title(f"{winner.name} wins!")
            else:
                self.ax.set_title("No winner!")
            self.fig.canvas.draw_idle()

    def get_player_symbol(self, player_name):
        symbol_is_invalid = True
        while symbol_is_invalid:
            symbol = input(f'Enter a character to use as a symbol for {player_name}: ')
            symbol = symbol.strip()
            symbol = symbol[0]
            if not symbol:
                print('Symbol must not be a whitespace character!')
            else:
                confirmation = input(f'Use "{symbol}" for {player_name}? (y/N): ')
                symbol_is_invalid = not confirmation.lower().startswith('y')
        return symbol


if __name__ == "__main__":
    display_mode = select_display_mode()

    if display_mode == 'matplotlib':
        opponent = select_opponent_type()
    else:
        while True:
            game_mode = input("Play against CPU or another player? \nFor CPU enter 1. \nFor another player enter 2): \n").lower()
            if game_mode == "1":
                opponent = 'cpu'
                break
            elif game_mode == "2":
                opponent = 'player'
                break
            else:
                print("Please enter 1 or 2")

    if opponent == 'cpu':
        game = ConnectFourGame(display_mode=display_mode, p2_type=CPUPlayer)
    else:
        game = ConnectFourGame(display_mode=display_mode)

    keep_playing = True
    while keep_playing:
        game.start()
        plt.close(game.fig)
        if display_mode == 'matplotlib':
            keep_playing = select_play_again()


        else:
            keep_playing = input('Play again? (y/N): ').lower().startswith('y')