from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from unittest.mock import patch
from model_bakery import baker

from games.constants import PLAYER, COMPUTER
from games.models import Game, Move


class GamesViewSetTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = baker.make(get_user_model(), username="user1")
        cls.user2 = baker.make(get_user_model(), username="user2")

        cls.game_1 = baker.make(Game, player=cls.user1)
        cls.game_2 = baker.make(Game, player=cls.user1)
        cls.game_3 = baker.make(Game, player=cls.user2)

        cls.move1_game1 = baker.make(
            Move,
            move_by=PLAYER,
            game=cls.game_1,
            board_state=[
                [".", ".", "."],
                [".", "X", "."],
                [".", ".", "."],
            ],
        )
        cls.move2_game1 = baker.make(
            Move,
            move_by=COMPUTER,
            game=cls.game_1,
            board_state=[
                ["O", ".", "."],
                [".", "X", "."],
                [".", ".", "."],
            ],
        )
        cls.move3_game1 = baker.make(
            Move,
            move_by=PLAYER,
            game=cls.game_1,
            board_state=[
                ["O", "X", "."],
                [".", "X", "."],
                [".", ".", "."],
            ],
        )
        cls.move4_game1 = baker.make(
            Move,
            move_by=COMPUTER,
            game=cls.game_1,
            board_state=[
                ["O", "X", "."],
                [".", "X", "O"],
                [".", ".", "."],
            ],
        )

        cls.move1_game2 = baker.make(
            Move,
            move_by=PLAYER,
            game=cls.game_2,
            board_state=[
                [".", ".", "X"],
                [".", ".", "."],
                [".", ".", "."],
            ],
        )
        cls.move2_game2 = baker.make(
            Move,
            move_by=COMPUTER,
            game=cls.game_2,
            board_state=[
                [".", ".", "X"],
                [".", "O", "."],
                [".", ".", "."],
            ],
        )

    def setUp(self):
        self.api_client = APIClient()

    def test_list_games_unauthenticated(self):
        response = self.api_client.get(reverse("games-list"))

        assert response.status_code == 403

    def test_lists_user_games(self):
        self.api_client.force_authenticate(self.user1)
        response = self.api_client.get(reverse("games-list"))

        assert response.status_code == 200
        # Should return only user1's games
        assert response.json() == [
            {
                "id": self.game_1.id,
                "board": [
                    ["O", "X", "."],
                    [".", "X", "O"],
                    [".", ".", "."],
                ],
                "game_winner": None,
            },
            {
                "id": self.game_2.id,
                "board": [
                    [".", ".", "X"],
                    [".", "O", "."],
                    [".", ".", "."],
                ],
                "game_winner": None,
            },
        ]

    def test_create_game_unauthenticated(self):
        response = self.api_client.post(reverse("games-list"))

        assert response.status_code == 403

    def test_create_game(self):
        self.api_client.force_authenticate(self.user1)
        response = self.api_client.post(reverse("games-list"))

        assert response.status_code == 201
        assert "id" in response.json()

    def test_game_does_not_belong_to_user(self):
        self.api_client.force_authenticate(self.user2)
        response = self.api_client.get(reverse("games-detail", args=[self.game_1.id]))

        # Should be 404 since game_1 belongs to user1
        assert response.status_code == 404

    def test_get_game_moves_unauthenticated(self):
        response = self.api_client.get(
            reverse("games-moves", kwargs={"pk": self.game_1.id})
        )

        assert response.status_code == 403

    def test_get_game_moves(self):
        self.api_client.force_authenticate(self.user1)
        response = self.api_client.get(
            reverse("games-moves", kwargs={"pk": self.game_1.id})
        )

        assert response.status_code == 200
        assert response.json() == [
            [
                [".", ".", "."],
                [".", "X", "."],
                [".", ".", "."],
            ],
            [
                ["O", ".", "."],
                [".", "X", "."],
                [".", ".", "."],
            ],
            [
                ["O", "X", "."],
                [".", "X", "."],
                [".", ".", "."],
            ],
            [
                ["O", "X", "."],
                [".", "X", "O"],
                [".", ".", "."],
            ],
        ]

    def test_get_game_moves_does_not_belong_to_user(self):
        self.api_client.force_authenticate(self.user2)
        response = self.api_client.get(
            reverse("games-moves", kwargs={"pk": self.game_1.id})
        )

        assert response.status_code == 404

    def test_get_game_moves_unauthenticated(self):
        response = self.api_client.post(
            reverse("games-move", kwargs={"pk": self.game_1.id}), data={"x": 2, "y": 1}
        )

        assert response.status_code == 403

    @patch("games.services.randint")
    def test_make_game_non_winning_move(self, randint_mock):
        # mock randint to return 3, which means position (2,2)
        randint_mock.return_value = 3
        self.api_client.force_authenticate(self.user1)
        response = self.api_client.post(
            reverse("games-move", kwargs={"pk": self.game_1.id}), data={"x": 1, "y": 0}
        )

        assert response.status_code == 200
        # Since this was a winning move, computer didn't move
        assert response.json() == {
            "board": [
                ["O", "X", "."],
                ["X", "X", "O"],
                [".", ".", "O"],
            ],
            "game_winner": None,
        }

    @patch("games.services.randint")
    def test_make_game_winning_move(self, randint_mock):
        # mock randint to return 3, which means position (2,2)
        randint_mock.return_value = 3
        self.api_client.force_authenticate(self.user1)
        response = self.api_client.post(
            reverse("games-move", kwargs={"pk": self.game_1.id}), data={"x": 2, "y": 1}
        )

        assert response.status_code == 200
        # Since this was a winning move, computer didn't move
        assert response.json() == {
            "board": [
                ["O", "X", "."],
                [".", "X", "O"],
                [".", "X", "."],
            ],
            "game_winner": "player",
        }

    @patch("games.services.randint")
    def test_make_game_winning_move_computer(self, randint_mock):
        baker.make(
            Move,
            move_by=PLAYER,
            game=self.game_1,
            board_state=[
                ["O", "X", "."],
                [".", "X", "O"],
                ["X", ".", "."],
            ],
        )
        baker.make(
            Move,
            move_by=COMPUTER,
            game=self.game_1,
            board_state=[
                ["O", "X", "O"],
                [".", "X", "O"],
                ["X", ".", "."],
            ],
        )

        # mock randint to return 2, which means position (2,2)
        randint_mock.return_value = 1
        self.api_client.force_authenticate(self.user1)
        response = self.api_client.post(
            reverse("games-move", kwargs={"pk": self.game_1.id}), data={"x": 1, "y": 0}
        )

        assert response.status_code == 200
        assert response.json() == {
            "board": [
                ["O", "X", "O"],
                ["X", "X", "O"],
                ["X", ".", "O"],
            ],
            "game_winner": "computer",
        }

    def test_make_game_move_tie(self):
        baker.make(
            Move,
            move_by=PLAYER,
            game=self.game_1,
            board_state=[
                ["O", "X", "."],
                [".", "X", "O"],
                ["X", ".", "."],
            ],
        )
        baker.make(
            Move,
            move_by=COMPUTER,
            game=self.game_1,
            board_state=[
                ["O", "X", "O"],
                [".", "X", "O"],
                ["X", ".", "."],
            ],
        )

        baker.make(
            Move,
            move_by=PLAYER,
            game=self.game_1,
            board_state=[
                ["O", "X", "O"],
                [".", "X", "O"],
                ["X", ".", "X"],
            ],
        )
        baker.make(
            Move,
            move_by=COMPUTER,
            game=self.game_1,
            board_state=[
                ["O", "X", "O"],
                [".", "X", "O"],
                ["X", "0", "X"],
            ],
        )

        self.api_client.force_authenticate(self.user1)
        response = self.api_client.post(
            reverse("games-move", kwargs={"pk": self.game_1.id}), data={"x": 1, "y": 0}
        )

        assert response.status_code == 200
        assert response.json() == {
            "board": [
                ["O", "X", "O"],
                ["X", "X", "O"],
                ["X", "0", "X"],
            ],
            "game_winner": "tie",
        }
