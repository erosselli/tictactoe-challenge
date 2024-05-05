from random import randint

# Django imports
from django.db import models
from django.contrib.auth.models import User

# Project imports
from games.constants import PLAYER_CHOICES, PLAYER, COMPUTER, WINNER_CHOICES
from games.exceptions import InvalidMove, InvalidPlayer


class Game(models.Model):
    player = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    game_winner = models.CharField(max_length=30, choices=WINNER_CHOICES, null=True)

    def __str__(self):
        return f"Game {self.id} - Player: {self.player.username}"


class Move(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="moves")
    created_at = models.DateTimeField(auto_now_add=True)
    move_by = models.CharField(max_length=30, choices=PLAYER_CHOICES)
    board_state = models.JSONField(
        help_text="Board state after executing the move. Board states are stored as a 3 x 3 matrix representing the board."
    )
