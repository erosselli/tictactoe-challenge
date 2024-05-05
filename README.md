# Ethyca Technical Challenge - Python

## Project Description
This is a Django project that uses Django REST Framework to implement a REST API. It has a single Django application called `games` and the database it uses is SQLite. The time used to setup, implement, and test the project was 4 hours. 

### A note on the DB
SQLite is the default DB that comes with a Django project created with the `django-admin startproject` command. Given more time for the project, I'd definitely add a more robust DB, PostgreSQL is usually my DB of choice.  

### Requirements

The requirements for the project are listed in the `requirements.txt` file. To install them, simply [create a virtual environment](https://docs.python.org/3/library/venv.html) and activate it, then run `pip install -r requirements.txt` in the project folder. 

## Running the Project
To run the project, you'll need to run migrations first. Run the following command in the project folder:
`python manage.py migrate`

You'll also need to create a user, which you can do by running:
`python manage.py createsuperuser` 

Then start the server:
`python manage.py runserver` 

If you go to `http://localhost:8000`, you should see the Django Admin, and should be able to log in with the user you previously created. You can create new users from the Django Admin as needed. 

## Tests

This project has (some) unit tests! You can find them in `games/test_views.py`. You can run them with `python manage.py test`, which uses the `unittest` module built-in to the Python standard library. 

## Game Logic 

The business logic for the tic-tac-toe game is mostly implemented on the `GameLogicService` class found in `games/services.py`. The tic-tac-toe board is represented as a 3 x 3 matrix (i.e a list of lists), and there's two Django models that store game information: `Game` and `Move`. A `Move` belongs to a `Game`, and in the `board_state` field stores the state of the game board after said move was done. It also has a `move_by` field to indicate whether the move was made by the player or by the computer. There's an assumption that the player is always the one who starts the game (by calling the `POST /games/:id/move` endpoint) and so they always use the `'X'` in the board. 

## REST API 

The REST API can be found at `http://localhost:8000/api/v1/`. If you open it in a browser, DRF provides a nice interface to interact with the API. The REST API has the following endpoints:

- `GET /api/v1/games` lists all the user's games, chronologically ordered
- `POST /api/v1/games` creates a game for the user
- `GET /api/v1/games/:id` retrieves the details of the given game, including its current board state
- `GET /api/v1/games/:id/moves` retrieves all the moves of the given game, chronologically ordered
- `POST /api/v1/games/:id/move` receives a JSON of the form `{"x": x_value, "y": y_value}` and makes the next move for the player to position (x_value, y_value), if the move is valid. Returns the state of the board after the computer has made its next move.

### Authentication 

The REST API uses Basic Auth with username and password. This is the default authentication scheme and I only used it because of the time constraint in the project. Without HTTPS this authentication is not secure, since username and password are transmitted unencrypted over the network. Given more time, I'd definitely change this to use a different authentication scheme, maybe something like JWTs using a package like `django-rest-framework-simplejwt`. 


## Improvements

I think some major improvements could be made to the project, given a bit more time. Two that I consider important are changing the way the authentication is handled and changing the DB, as explained above. In the current implementation I opted for using the defaults so as to save time setting up the project. 

Another improvement I would have liked to implement is an endpoint that allows someone to register as a user, perhaps `POST api/v1/users/` o `POST api/v1/users/sign-up`, since right now users can only be created from the Django Admin (or via the `createsuperuser` management command). 

Finally, one thing I would have loved to implement is the ability to play against another human player, rather than against the computer. I had originally named the `player` field in the `Game` model as `player1`, hopeful that I'd have time to add a `player2` optional field. In the end I didn't so I renamed all `player1` references to just `player` (you can see this in migration 003). The idea was that a player would be able to optionally add a player2 to their game, and in that case the computer wouldn't make any moves when calling the `POST /api/v1/games/:id/move` endpoint. The `move_by` field on the latest `Move` in the game could be used to determine whose turn it was, only allowing a player to call the endpoint when it is their turn. 

I also think the `__check_game_over` method in the `GameLogicService` class can definitely be improved upon; there are probably better, more efficient solutions to checking whether or not a game is over, since I'm iterating over the board more than once. I was hoping I'd have time to refactor this code but didn't want to go over the established time limit. 