from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from games.models import Game
from games.services import GameLogicService


class CreateGameSerializer(serializers.ModelSerializer):

    class Meta:
        model = Game
        fields = ["id"]

    def create(self, validated_data):
        request = self.context["request"]
        # We get the player from the logged in user
        player = request.user
        return super().create({**validated_data, "player": player})


class RetrieveGameSerializer(serializers.ModelSerializer):
    board = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Game
        fields = ["id", "board", "game_winner"]

    def get_board(self, obj):
        game_logic = GameLogicService(obj)
        return game_logic.get_current_board()


class MakeMoveSerializer(serializers.Serializer):
    x = serializers.IntegerField()
    y = serializers.IntegerField()

    def validate_coordinate(self, coordinate_name, coordinate_value):
        if coordinate_value < 0 or coordinate_value > 2:
            raise ValidationError(
                f"{coordinate_name} coordinate must be an integer between 0 and 2"
            )
        return coordinate_value

    def validate_x(self, value):
        return self.validate_coordinate("X", value)

    def validate_y(self, value):
        return self.validate_coordinate("Y", value)

    def validate(self, attrs):
        x_coordinate = attrs["x"]
        y_coordinate = attrs["y"]

        game = self.context["game"]
        game_logic = GameLogicService(game)

        if not game_logic.is_move_valid(x=x_coordinate, y=y_coordinate):
            raise ValidationError(
                f"Space ({x_coordinate}, {y_coordinate}) is already occupied"
            )

        return attrs

    def save(self):
        game = self.context["game"]
        game_logic = GameLogicService(game)

        player_move, winner = game_logic.make_player_move(
            x=self.validated_data["x"], y=self.validated_data["y"]
        )
        if winner:
            return player_move, winner
        computer_move, winner = game_logic.make_computer_move()
        return computer_move, winner
