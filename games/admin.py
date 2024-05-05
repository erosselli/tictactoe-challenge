from django.contrib import admin
from games.models import Game, Move

admin.site.register(Game, admin.ModelAdmin)
admin.site.register(Move, admin.ModelAdmin)
