from protorpc import messages
from google.appengine.ext import ndb
import endpoints

from models import User, Game, Score, GameWords, StringMessages, RankingForms
from models import StringMessage, NewGameForm, GameForm, MakeMoveForm,\
    ScoreForms, RankingForm, HistoryForm, HistoryForms, ConnectFourMoveForm

# If the request contains path or querystring arguments,
# you cannot use a simple Message class as described under Create the API.
# Instead, you must use a ResourceContainer class"

NEW_GAME_REQUEST = endpoints.ResourceContainer(
    user_name = messages.StringField(1, required=True)
)

GET_GAME_REQUEST = endpoints.ResourceContainer(
    urlsafe_game_key=messages.StringField(1)
)

MAKE_MOVE_REQUEST = endpoints.ResourceContainer(
    MakeMoveForm,
    urlsafe_game_key=messages.StringField(1)
)

USER_REQUEST = endpoints.ResourceContainer(
    user_name=messages.StringField(1),
    email=messages.StringField(2)
)

CONNECT_FOUR_MOVE_REQUEST = endpoints.ResourceContainer(
    ConnectFourMoveForm
)

NEW_WORD = endpoints.ResourceContainer(
    word = messages.StringField(1, required=True),
    spanish_translation = messages.StringField(2, required=True)
)
