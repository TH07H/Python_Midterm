import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
from matplotlib.widgets import Button


def animate_drop(ax, fig, board, color_map, col, final_row, symbol):
    """Animate a piece falling by temporarily placing it in each row,
    top to bottom."""
    for row in range(0, final_row + 1):
        board.rows[row][col] = symbol   # temporarily place it here
        draw_pieces(ax, board, color_map, col)
        fig.canvas.draw_idle()
        plt.pause(0.01)
        board.rows[row][col] = ' '      # clear it before the next frame


def draw_board_full(ax, board, color_map):
    ax.clear()
    ax.set_xlim(-0.5, board.num_cols - 0.3)
    ax.set_ylim(-0.5, board.num_rows - 0.2)
    ax.set_aspect('equal')
    ax.axis('off')

    rectback = Rectangle((-1.25, -1.25), board.num_cols + 2,
                         board.num_rows + 2, color='#01115e')
    rect = Rectangle((-1.25, -1.25), board.num_cols + 0.8,
                     board.num_rows + 0.92, color='#002aff')
    circlecorner = Circle((-10, 16.16), radius=14.14, color='white')
    circlecornerl = Circle((16.16, -10), radius=13.5, color='white')
    ax.add_patch(rectback)
    ax.add_patch(rect)
    ax.add_patch(circlecorner)
    ax.add_patch(circlecornerl)

    for row in range(board.num_rows):
        for col in range(board.num_cols):
            symbol = board.rows[row][col]
            main_color, shadow_color = color_map[symbol]

            x_shadow = col - 0.04
            y_shadow = board.num_rows - 1 - row
            shadow = Circle((x_shadow, y_shadow), radius=0.4,
                            facecolor=shadow_color, edgecolor='black')
            ax.add_patch(shadow)

            x_main = col
            y_main = board.num_rows - 0.95 - row
            main = Circle((x_main, y_main), radius=0.4, color=main_color)
            ax.add_patch(main)


def draw_board(ax, board, color_map):
    ax.set_xlim(-0.5, board.num_cols - 0.3)
    ax.set_ylim(-0.5, board.num_rows - 0.2)
    ax.set_aspect('equal')
    ax.axis('off')

    rectback = Rectangle((-1.25, -1.25), board.num_cols + 2,
                         board.num_rows + 2, color='#01115e')
    rect = Rectangle((-1.25, -1.25), board.num_cols + 0.8,
                     board.num_rows + 0.92, color='#002aff')
    circlecorner = Circle((-10, 16.16), radius=14.14, color='white')
    circlecornerl = Circle((16.16, -10), radius=13.5, color='white')
    ax.add_patch(rectback)
    ax.add_patch(rect)
    ax.add_patch(circlecorner)
    ax.add_patch(circlecornerl)


def draw_pieces(ax, board, color_map, col):
    ax.set_xlim(-0.5, board.num_cols - 0.3)
    ax.set_ylim(-0.5, board.num_rows - 0.2)
    ax.set_aspect('equal')
    ax.axis('off')

    for row in range(board.num_rows):

        symbol = board.rows[row][col]
        main_color, shadow_color = color_map[symbol]
        x_shadow = col - 0.04
        y_shadow = board.num_rows - 1 - row
        shadow = Circle((x_shadow, y_shadow), radius=0.4,
                        facecolor=shadow_color, edgecolor='black')
        ax.add_patch(shadow)
        x_main = col
        y_main = board.num_rows - 0.95 - row
        main = Circle((x_main, y_main), radius=0.4, color=main_color)
        ax.add_patch(main)


def select_display_mode():
    """Show a GUI with two buttons; return 'console' or 'matplotlib'
    based on click."""
    fig, ax = plt.subplots()
    ax.set_title("Choose display mode")
    ax.axis('off')

    choice = {'mode': None}

    def choose_console(event):
        choice['mode'] = 'console'
        plt.close(fig)

    def choose_matplotlib(event):
        choice['mode'] = 'matplotlib'
        plt.close(fig)

    ax_console = fig.add_axes([0.2, 0.4, 0.25, 0.15])
    ax_matplotlib = fig.add_axes([0.55, 0.4, 0.25, 0.15])

    btn_console = Button(ax_console, 'Console')
    btn_matplotlib = Button(ax_matplotlib, 'Matplotlib')

    btn_console.on_clicked(choose_console)
    btn_matplotlib.on_clicked(choose_matplotlib)

    plt.show()

    return choice['mode']


def select_opponent_type():
    """Show a GUI with two buttons; return 'cpu' or 'player' based on click."""
    fig, ax = plt.subplots()
    ax.set_title("Play against CPU or another player?")
    ax.axis('off')

    choice = {'mode': None}

    def choose_cpu(event):
        choice['mode'] = 'cpu'
        plt.close(fig)

    def choose_player(event):
        choice['mode'] = 'player'
        plt.close(fig)

    ax_cpu = fig.add_axes([0.2, 0.4, 0.25, 0.15])
    ax_player = fig.add_axes([0.55, 0.4, 0.25, 0.15])

    btn_cpu = Button(ax_cpu, 'CPU')
    btn_player = Button(ax_player, 'Another Player')

    btn_cpu.on_clicked(choose_cpu)
    btn_player.on_clicked(choose_player)

    plt.show()

    return choice['mode']


def select_play_again():
    """Show a GUI with two buttons; return True or False based on click."""
    fig, ax = plt.subplots()
    ax.set_title("Play again?")
    ax.axis('off')

    choice = {'again': False}

    def choose_yes(event):
        choice['again'] = True
        plt.close(fig)

    def choose_no(event):
        choice['again'] = False
        plt.close(fig)

    ax_yes = fig.add_axes([0.2, 0.4, 0.25, 0.15])
    ax_no = fig.add_axes([0.55, 0.4, 0.25, 0.15])

    btn_yes = Button(ax_yes, 'Yes')
    btn_no = Button(ax_no, 'No')

    btn_yes.on_clicked(choose_yes)
    btn_no.on_clicked(choose_no)

    plt.show()

    return choice['again']


if __name__ == "__main__":
    from board import ConnectFourBoard

    board = ConnectFourBoard(6, 7)
    board.rows[5][3] = 'X'
    board.rows[5][4] = 'O'

    color_map = {
        ' ': ('white', '#01115e'),
        'X': ('red', 'darkred'),
        'O': ('yellow', 'goldenrod')
    }

    fig, ax = plt.subplots()
    draw_board(ax, board, color_map)
    plt.show()
