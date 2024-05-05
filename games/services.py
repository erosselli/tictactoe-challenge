from random import randint

from games.constants import PLAYER, COMPUTER, TIE
from games.exceptions import InvalidMove, InvalidPlayer


class GameLogicService:
    EMPTY_SPACE = "."

    def __init__(self, game):
        self.game = game

    @classmethod
    def get_initial_board(cls):
        """
        Returns the board in its initial state, where neither player
        or computer have made any moves.
        """
        return [
            [cls.EMPTY_SPACE, cls.EMPTY_SPACE, cls.EMPTY_SPACE],
            [cls.EMPTY_SPACE, cls.EMPTY_SPACE, cls.EMPTY_SPACE],
            [cls.EMPTY_SPACE, cls.EMPTY_SPACE, cls.EMPTY_SPACE],
        ]

    @staticmethod
    def get_player_token(player_type):
        """
        Returns the token for the given player type. For now, player always
        starts the game so they're 'X' while the computer is 'O'
        """
        if player_type == PLAYER:
            return "X"
        if player_type == COMPUTER:
            return "O"

        raise InvalidPlayer(f"Unknown player type: {player_type}")

    def get_current_board(self):
        """
        Returns the current state of the game's board
        """
        latest_move = self.game.moves.order_by("-created_at").first()
        if not latest_move:
            # No move has been made yet, return board representing initial state
            return self.get_initial_board()

        return latest_move.board_state

    def __make_move(self, x, y, board, player):
        """
        Creates a new Move instance for the Game, where the specified player
        has placed their token on the space specified by (x, y). Assumes the
        given coordinates are valid. Returns the move and the game winner, if there is one.
        For methods with validations, use make_player_move or make_computer_move instead.
        """
        new_board = [*board]
        new_board[x][y] = self.get_player_token(player_type=player)

        move = self.game.moves.create(move_by=player, board_state=new_board)
        self.__check_game_over(new_board)
        return move, self.game.game_winner

    def make_player_move(self, x, y):
        """
        Places a player's token in position (x,y). Returns the created Move instance.
        Raises InvalidMove exception if game is over or space is already occupied.
        """
        if self.game.game_winner:
            raise InvalidMove("Cannot make a move, game is already over.")

        board = self.get_current_board()
        if board[x][y] is not self.EMPTY_SPACE:
            raise InvalidMove(f"Space ({x}, {y}) is already occupied")

        return self.__make_move(x=x, y=y, board=board, player=PLAYER)

    def make_computer_move(self):
        """
        Makes a randomly-generated move for the computer. Returns the created Move instance.
        Raises InvalidMove exception if game is over.
        """
        if self.game.game_winner:
            raise InvalidMove("Cannot make a move, game is already over.")

        board = self.get_current_board()

        empty_spaces = self.__get_empty_spaces(board)
        if not empty_spaces:
            raise InvalidMove("Cannot move, all spaces are already occupied")

        move_index = randint(0, len(empty_spaces) - 1)
        move_x, move_y = empty_spaces[move_index]

        return self.__make_move(x=move_x, y=move_y, board=board, player=COMPUTER)

    def is_move_valid(self, x, y):
        """
        Returns true if the move is valid, i.e if game is not over
        and the position (x,y) is an empty space.
        """
        board = self.get_current_board()
        return not self.game.game_winner and board[x][y] is self.EMPTY_SPACE

    def __check_game_over(self, board):
        """
        Checks whether the game is over, and if so updates the game's game_winner field.
        """
        # Winning combinations
        winning_combos = [
            # Rows
            [(0, 0), (0, 1), (0, 2)],
            [(1, 0), (1, 1), (1, 2)],
            [(2, 0), (2, 1), (2, 2)],
            # Columns
            [(0, 0), (1, 0), (2, 0)],
            [(0, 1), (1, 1), (2, 1)],
            [(0, 2), (1, 2), (2, 2)],
            # Diagonal
            [(0, 0), (1, 1), (2, 2)],
            [(2, 0), (1, 1), (0, 2)],
        ]

        # Check if player won
        player_token = self.get_player_token(PLAYER)
        player_tokens = [
            [board[i][j] for (i, j) in combo if board[i][j] == player_token]
            for combo in winning_combos
        ]

        if any(len(t) == 3 for t in player_tokens):
            self.game.game_winner = PLAYER
            self.game.save()
            return

        # Check if computer won
        computer_token = self.get_player_token(COMPUTER)
        computer_tokens = [
            [board[i][j] for (i, j) in combo if board[i][j] == computer_token]
            for combo in winning_combos
        ]

        if any(len(t) == 3 for t in computer_tokens):
            self.game.game_winner = COMPUTER
            self.game.save()
            return

        # If there are no empty spaces and no one won, it's a tie
        if not self.__get_empty_spaces(board):
            self.game.game_winner = TIE
            self.game.save()

    def __get_empty_spaces(self, board):
        """
        Returns a list off (x,y) coordinates that correspond to
        the empty positions of the given board
        """
        all_spaces = [(i, j) for i in range(0, 3) for j in range(0, 3)]
        empty_spaces = [
            (i, j) for (i, j) in all_spaces if board[i][j] is self.EMPTY_SPACE
        ]

        return empty_spaces
