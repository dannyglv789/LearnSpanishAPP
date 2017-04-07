import random
from datetime import date
from protorpc import messages
from google.appengine.ext import ndb
import endpoints
from listofwords import new_words, english_spanish_words

"""models.py - This file contains the class definitions for the Datastore
entities used by the Game. Because these classes are also regular Python
classes they can include methods (such as 'to_form' and 'new_game').
every entity is given a datastore key
"""
#helper function for getting user
def getUserId(user, id_type="email"):
    if id_type == "email":
        return user.email()
    
class GameWords(ndb.Model):
    """  Words for hangman"""
    word = ndb.StringProperty(required=True)
    spanish_translation = ndb.StringProperty(required=True)

    @classmethod
    def add_words_from_list(cls):
        english_words = english_spanish_words[::2]
        spanish_words = english_spanish_words[1::2]
        pairs = zip(english_words, spanish_words)
        for i in pairs:
            new_word = GameWords(word=i[0],spanish_translation=i[1])
            new_word.put()
        return "words added to datastore"
    

class User(ndb.Model):
    """User profile"""
    name = ndb.StringProperty(required=True)
    email =ndb.StringProperty()
    receives_updates = ndb.BooleanProperty(default=False)
    wins = ndb.IntegerProperty(default=0)

class Game(ndb.Model):
    """Game object"""
    game_over = ndb.BooleanProperty(required=True, default=False)
    user = ndb.KeyProperty(required=True, kind='User')
    moves = ndb.StringProperty(repeated=True)
    target = ndb.StringProperty(required=True)
    option_1 = ndb.StringProperty(required=True)
    option_2 = ndb.StringProperty(required=True)
    option_3 = ndb.StringProperty(required=True)
    answer = ndb.StringProperty(required=True)
    connect_4_turn = ndb.BooleanProperty(required=True, default=False)
#    player_moves = ndb.StringProperty(repeated=True)
    # connect four game
    board = [[1, 1], [1, 2], [1, 3], [1, 4], [2, 1], [2, 2], [2, 3], [2, 4], [3, 1], [3, 2], [3, 3], [3, 4], [4, 1], [4, 2], [4, 3], [4, 4]]
    legal = [[1,1], [1, 2], [1, 3], [1, 4]]
    wins = {"x_row_1": [[1, 1], [1, 2], [1, 3], [1, 4]],
         "x_row_2": [[2, 1], [2, 2], [2, 3], [2, 4]],
         "x_row_3": [[3, 1], [3, 2], [3, 3], [3, 4]],
         "x_row_4": [[4, 1], [4, 2], [4, 3], [4, 4]],
         "y_row_1": [[1,1], [2,1], [3,1], [4,1]],
         "y_row_2": [[1,2], [2,2], [3,2], [4,2]],
         "y_row_3": [[1,3], [2,3], [3,3], [4,3]],
         "y_row_4": [[1,4], [2,4], [3,4], [4,4]],
         "diag_1": [[1,1], [2,2], [3,3],[4,4]],
         "diag_2": [[4,1], [3,2], [2,3], [1,4]]
    }

    computer_wins = {"x_row_1": [[1, 1], [1, 2], [1, 3], [1, 4]],
         "x_row_2": [[2, 1], [2, 2], [2, 3], [2, 4]],
         "x_row_3": [[3, 1], [3, 2], [3, 3], [3, 4]],
         "x_row_4": [[4, 1], [4, 2], [4, 3], [4, 4]],
         "y_row_1": [[1,1], [2,1], [3,1], [4,1]],
         "y_row_2": [[1,2], [2,2], [3,2], [4,2]],
         "y_row_3": [[1,3], [2,3], [3,3], [4,3]],
         "y_row_4": [[1,4], [2,4], [3,4], [4,4]],
         "diag_1": [[1,1], [2,2], [3,3],[4,4]],
         "diag_2": [[4,1], [3,2], [2,3], [1,4]]
    }

    

    @classmethod
    def new_game(cls, user):
        """Creates a new game from user request"""

        # retrieve word entity from random key
        q = GameWords.query().fetch(keys_only=True)
        entity_key = random.choice(q)
        word_entity = entity_key.get()
        spanish_words = english_spanish_words[1::2]

        # fetch correct answer and two spanish choices
        incorrect_1 = random.choice(spanish_words)
        incorrect_2 = random.choice(spanish_words)
        correct = word_entity.spanish_translation

        # create a random list containing the rigiht answer
        choices_list = [incorrect_1, incorrect_2, correct]
        randomized = [random.choice(choices_list),random.choice(choices_list),random.choice(choices_list)]
        if correct not in randomized:
            randomized[0] = correct
            randomized[1] = random.choice(spanish_words)
            randomized[2] = random.choice(spanish_words)
        
        g_user = endpoints.get_current_user()
        user_id = getUserId(g_user)
        u_key = ndb.Key(User, user_id)
        game_id = Game.allocate_ids(size=1, parent=u_key)[0]
        game_key = ndb.Key(Game, game_id, parent=u_key)
        game = Game(
                    user=user,
                    game_over=False,
                    key = game_key,
                    target=word_entity.word,
                    option_1 = randomized[0],
                    option_2 = randomized[1],
                    option_3 = randomized[2],
                    answer = word_entity.spanish_translation
                    )
        game.put()
        
        return game

    def player_move(self, move, player):
        # player_move algorithm. If move is illegal, move is rejected.
        # If move is legal, move is played and the slot above move becomes legal
        # move_index: the list position of the player move
        # legal_spot: the newly legal position based on move_index

        if move not in self.legal:
            print "sorry try again"
        else:
            # slot above move becomes legal
            move_index = -1
            for i in board:
                move_index +=1
                if i == move:
                    break
                
            legal_spot = move_index + 4
            if board[legal_spot] not in legal:
                legal.append(board[legal_spot])

            # remove played move from legal list
            list_pos = -1
            for i in legal:
                list_pos +=1
                if i == move:
                    legal.pop(list_pos)

            # removes move from wins dictionary. Once one of the win
            # lists is empty, player has won.
            if player == "player_1":
                for key, value in wins.iteritems():
                    for x in value:
                        if x == move:
                            value.remove(x)
            else:
                for key, value in computer_wins.iteritems():
                    for x in value:
                        if x == move:
                            value.remove(x)
            print move_index
            return board[legal_spot]
    
    def new_round(self,current_game):
        """ switches the target word """
        # retrieve word entity randomly for new round
        q = GameWords.query().fetch(keys_only=True)
        entity_key = random.choice(q)
        word_entity = entity_key.get()
        spanish_words = english_spanish_words[1::2]

        # fetch correct answer and two spanish choices
        incorrect_1 = random.choice(spanish_words)
        incorrect_2 = random.choice(spanish_words)
        correct = word_entity.spanish_translation

        # create a random list containing the rigiht answer
        choices_list = [incorrect_1, incorrect_2, correct]
        randomized = [random.choice(choices_list),random.choice(choices_list),random.choice(choices_list)]
        if correct not in randomized:
            randomized[0] = correct
            randomized[1] = random.choice(spanish_words)
            randomized[2] = random.choice(spanish_words)
            
        current_game.target=word_entity.word
        current_game.option_1 = randomized[0]
        current_game.option_2 = randomized[1]
        current_game.option_3 = randomized[2]
        current_game.answer = word_entity.spanish_translation
        current_game.put()
    
    def to_form(self):
        """Returns a GameForm representation of the Game"""
        form = GameForm()
        form.urlsafe_key = self.key.urlsafe()
        form.game_over = self.game_over
        form.target = self.target
        form.choice_1 = self.option_1
        form.choice_2 = self.option_2
        form.choice_3 = self.option_3
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
    game_over = messages.BooleanField(2, required=True)
    target = messages.StringField(3, required=True)
    choice_1 = messages.StringField(4, required=True)
    choice_2 = messages.StringField(5, required=True)
    choice_3 = messages.StringField(6, required=True)
    
class NewGameForm(messages.Message):
    """Used to create a new game"""
    user_name = messages.StringField(1, required=True)


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
    """response of a single string message"""
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

