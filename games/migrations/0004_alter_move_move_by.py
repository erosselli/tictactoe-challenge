# Generated by Django 5.0.4 on 2024-05-04 17:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("games", "0003_rename_player1_game_player"),
    ]

    operations = [
        migrations.AlterField(
            model_name="move",
            name="move_by",
            field=models.CharField(
                choices=[("player", "Player"), ("computer", "Computer")], max_length=30
            ),
        ),
    ]
