"""models.py - This file contains the class definitions for the Datastore
entities used by the Game. Because these classes are also regular Python
classes they can include methods (such as 'to_form' and 'new_game')."""

import random
from datetime import date
from protorpc import messages
from google.appengine.ext import ndb
import endpoints

#helper function for getting user
def getUserId(user, id_type="email"):
    if id_type == "email":
        return user.email()
class HangManWords(ndb.Model):
    """  Words for hangman """
    word = ndb.StringProperty(required=True)
    scrambled_word = ndb.StringProperty(required=True)

class User(ndb.Model):
    """User profile"""
    name = ndb.StringProperty(required=True)
    email =ndb.StringProperty()
    receives_updates = ndb.BooleanProperty(default=False)
    wins = ndb.IntegerProperty(default=0)

class Game(ndb.Model):
    """Game object"""
    target = ndb.StringProperty(required=True)
    attempts_allowed = ndb.IntegerProperty(required=True)
    attempts_remaining = ndb.IntegerProperty(required=True, default=5)
    game_over = ndb.BooleanProperty(required=True, default=False)
    user = ndb.KeyProperty(required=True, kind='User')
    moves = ndb.StringProperty(repeated=True)

    @classmethod
    def new_game(cls, user, attempts):
        """Creates and returns a new game"""
        q = HangManWords.query()
        words = []
        for x in q:
            words.append(x.word)
#        if max < min:
#            raise ValueError('Maximum must be greater than minimum')
# key
        g_user = endpoints.get_current_user()
        user_id = getUserId(g_user)
        u_key = ndb.Key(User, user_id)
        game_id = Game.allocate_ids(size=1, parent=u_key)[0]
        game_key = ndb.Key(Game, game_id, parent=u_key)
        
        game = Game(user=user,
                    target=random.choice(words),
                    attempts_allowed=attempts,
                    attempts_remaining=attempts,
                    game_over=False,
                    key = game_key)
        game.put()
        return game

    def to_form(self, message):
        """Returns a GameForm representation of the Game"""
        form = GameForm()
        form.urlsafe_key = self.key.urlsafe()
        form.user_name = self.user.get().name
        form.attempts_remaining = self.attempts_remaining
        form.game_over = self.game_over
        form.message = message
        return form

    def end_game(self, won=False):
        """Ends the game - if won is True, the player won. - if won is False,
        the player lost."""
        self.game_over = True
        self.put()
        # Add the game to the score 'board'
        score = Score(user=self.user, date=date.today(), won=won,
                      guesses=self.attempts_allowed - self.attempts_remaining)
        score.put()

class Score(ndb.Model):
    """Score object"""
    user = ndb.KeyProperty(required=True, kind='User')
    date = ndb.DateProperty(required=True)
    won = ndb.BooleanProperty(required=True)
    guesses = ndb.IntegerProperty(required=True)

    def to_form(self):
#        user = endpoints.get_current_user()
#        user_id = getUserId(user)
        return ScoreForm(user_name=self.user.urlsafe(), won=self.won,
                         date=str(self.date), guesses=self.guesses)


class GameForm(messages.Message):
    """GameForm for outbound game state information"""
    urlsafe_key = messages.StringField(1, required=True)
    attempts_remaining = messages.IntegerField(2, required=True)
    game_over = messages.BooleanField(3, required=True)
    message = messages.StringField(4, required=True)
    user_name = messages.StringField(5, required=True)
    
class GameForm(messages.Message):
    """GameForm for outbound game state information"""
    urlsafe_key = messages.StringField(1, required=True)
    attempts_remaining = messages.IntegerField(2, required=True)
    game_over = messages.BooleanField(3, required=True)
    message = messages.StringField(4, required=True)
    user_name = messages.StringField(5, required=True)


class NewGameForm(messages.Message):
    """Used to create a new game"""
    user_name = messages.StringField(1, required=True)
#    min = messages.IntegerField(2, default=1)
#    max = messages.IntegerField(3, default=10)
    attempts = messages.IntegerField(4, default=5)


class MakeMoveForm(messages.Message):
    """Used to make a move in an existing game"""
    guess = messages.StringField(1, required=True)

class ScoreForm(messages.Message):
    """ScoreForm for outbound Score information"""
    user_name = messages.StringField(1, required=True)
    date = messages.StringField(2, required=True)
    won = messages.BooleanField(3, required=True)
    guesses = messages.IntegerField(4, required=True)


class ScoreForms(messages.Message):
    """Return multiple ScoreForms"""
    items = messages.MessageField(ScoreForm, 1, repeated=True)


class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    message = messages.StringField(1, required=True)

class StringMessages(messages.Message):
    """StringMessage-- outbound (single) string message"""
    items = messages.MessageField(StringMessage, 1, repeated=True)

class RankingForm(messages.Message):
    """ScoreForm for outbound Score information"""
    user_name = messages.StringField(1, required=True)
    wins = messages.IntegerField(2, required=True)

class RankingForms(messages.Message):
    user_rankings = messages.MessageField(RankingForm, 1, repeated=True)

class HistoryForm(messages.Message):
    move = messages.StringField(1,required=True)

class HistoryForms(messages.Message):
    moves = messages.MessageField(HistoryForm, 1, repeated=True)
