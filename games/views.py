# Django / DRF imports
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotAuthenticated
from rest_framework.response import Response

# Project imports
from games.models import Game
from games.serializers import (
    CreateGameSerializer,
    MakeMoveSerializer,
    RetrieveGameSerializer,
)


class GamesViewSet(viewsets.ModelViewSet):
    def perform_authentication(self, request):
        current_user = self.request.user
        if not current_user or not current_user.id:
            raise NotAuthenticated()
        return super().perform_authentication(request)

    def get_queryset(self):
        current_user = self.request.user
        return Game.objects.filter(player=current_user).order_by("created_at")

    def get_serializer_class(self):
        if self.action == "move":
            return MakeMoveSerializer

        if self.action == "create":
            return CreateGameSerializer

        return RetrieveGameSerializer

    @action(detail=True, methods=["post"])
    def move(self, request, **kwargs):
        game = self.get_object()
        serializer = self.get_serializer(data=request.data, context={"game": game})
        serializer.is_valid(raise_exception=True)
        move_instance, winner = serializer.save()

        return Response(
            {
                "board": move_instance.board_state,
                "game_winner": winner,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["get"])
    def moves(self, *args, **kwargs):
        game = self.get_object()
        moves = game.moves.order_by("created_at")
        return Response([move.board_state for move in moves], status=status.HTTP_200_OK)
