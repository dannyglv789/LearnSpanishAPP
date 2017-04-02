# -*- coding: utf-8 -*-`
"""api.py - Create and configure the Game API exposing the resources.
This can also contain game logic. """

import logging
import endpoints
import random
from protorpc import remote, messages
from protorpc import message_types
from google.appengine.api import memcache
from google.appengine.api import taskqueue
from google.appengine.ext import ndb
from models import User, Game, Score, GameWords, StringMessages, RankingForms
from models import StringMessage, NewGameForm, GameForm, MakeMoveForm,\
    ScoreForms, RankingForm, HistoryForm, HistoryForms
from resourcecontainers import NEW_GAME_REQUEST, GET_GAME_REQUEST, \
     MAKE_MOVE_REQUEST, USER_REQUEST, NEW_WORD
from utils import get_by_urlsafe, getUserId

MEMCACHE_MOVES_REMAINING = 'MOVES_REMAINING'

# our api name and verison
@endpoints.api(name='learnspanish', version='v1')
class GuessANumberApi(remote.Service):
    """Game API"""
    @endpoints.method(message_types.VoidMessage,StringMessage,
                      name='AddNewWord',
                      http_method='POST')
    def add_word(self,request):
        """Add list of words to datastore"""
        GameWords.add_words_from_list()
        return StringMessage(message="words added")

    @endpoints.method(request_message=NEW_GAME_REQUEST,
                      response_message=GameForm,
                      name='new_game',
                      http_method='POST')
    
    def new_game(self, request):
        """Creates new game."""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException('User does not exist!')
        try:
            # user exists and new game entity is added to datastore
            game = Game.new_game(user.key)
        except ValueError:
            raise endpoints.BadRequestException('bad request')
            
        # Use a task queue to update the average attempts remaining.
        # This operation is not needed to complete the creation of a new game
        # so it is performed out of sequence.
        # taskqueue.add(url='/tasks/cache_average_attempts')
        return game.to_form()
    
    # endpoint for creating a new user
    @endpoints.method(request_message=USER_REQUEST,
                      response_message=StringMessage,
                      path='user',
                      name='create_user',
                      http_method='POST')
    def create_user(self, request):
        """ create a new user """

        # check if a user already exists
        if User.query(User.name == request.user_name).get():
            raise endpoints.ConflictException(
                    'A User with that name already exists!')

        # endpoints.get_current_user() returns a User, otherwise it returns None.
        g_user = endpoints.get_current_user()
        if not g_user:
            raise endpoints.UnauthorizedException('Authorization required')

        # get email from user
        user_id = getUserId(g_user)

        # create ndb key of kind User from user email
        u_key = ndb.Key(User, user_id)

        # store user in db
        user = User(name=request.user_name, email=request.email, key=u_key)
        user.put()

        # returns a response message confirming user was created
        return StringMessage(message='User {} created!'.format(
                request.user_name))

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='get_game',
                      http_method='GET')
    def get_game(self, request):
        """Returns game state"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game:
            return GameForm(game_over=game.game_over,
                            urlsafe_key= game.key.urlsafe(),
                            target=game.target,
                            choice_1 = game.option_1,
                            choice_2 = game.option_2,
                            choice_3 = game.option_3
                            )
        else:
            raise endpoints.NotFoundException('Game not found!')

    @endpoints.method(request_message=MAKE_MOVE_REQUEST,
                      response_message=StringMessage,
                      path='game/{urlsafe_game_key}',
                      name='make_move',
                      http_method='PUT')
    def make_move(self, request):
        """Makes a move. User sends a request containing a guess."""
        # retrieve the game with the urlsafe key, then the target
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        target = game.target
        
        if game.game_over:
            return game.to_form('Game already over!')

        if request.guess == game.target:
            # user makes a connect 4 move
            game.new_round(game)
            return StringMessage(message="correct")
        else:
            # computer makes a  connect 4 move
            game.new_round(game)
            return StringMessage(message="next")

        """
            # add win to profile
            user = endpoints.get_current_user()
            user_id = getUserId(user)
            u_key = ndb.Key(User, user_id)
            prof = u_key.get()
            prof.wins +=1

            #add msg to history
            msg = 'You win'
            game.moves.append(msg)
            prof.put()

            # return win response
            game.end_game(True)
            return game.to_form('You win!')

        # guess is incorrect
        if request.guess != game.target:
            msg = 'sorry try again!'
            game.moves.append(msg)

        if game.attempts_remaining < 1:
            game.end_game(False)
            return game.to_form(msg + ' Game over!')
        else:
            game.put()
            return game.to_form(msg)
    """

    

    @endpoints.method(response_message=ScoreForms,
                      path='scores',
                      name='get_scores',
                      http_method='GET')
    def get_scores(self, request):
        """Return all scores"""
        return ScoreForms(items=[score.to_form() for score in Score.query()])

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=ScoreForms,
                      path='scores/user/{user_name}',
                      name='get_user_scores',
                      http_method='GET')
    def get_user_scores(self, request):
        """Returns all of an individual User's scores"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                    'A User with that name does not exist!')
        scores = Score.query(Score.user == user.key)
        return ScoreForms(items=[score.to_form() for score in scores])

    @endpoints.method(response_message=StringMessage,
                      path='games/average_attempts',
                      name='get_average_attempts_remaining',
                      http_method='GET')
    def get_average_attempts(self, request):
        """Get the cached average moves remaining"""
        return StringMessage(message=memcache.get(MEMCACHE_MOVES_REMAINING) or '')

    @staticmethod
    def _cache_average_attempts():
        """Populates memcache with the average moves remaining of Games"""
        games = Game.query(Game.game_over == False).fetch()
        if games:
            count = len(games)
            total_attempts_remaining = sum([game.attempts_remaining
                                        for game in games])
            average = float(total_attempts_remaining)/count
            memcache.set(MEMCACHE_MOVES_REMAINING,
                         'The average moves remaining is {:.2f}'.format(average))
# Task 3 endpoints
    @endpoints.method(message_types.VoidMessage,StringMessages,
                      name='get_user_games',
                      http_method='GET')
    def get_user_games(self,request):
        """ Get Active user games"""
        # make sure user is authed
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')    
        user_id = getUserId(user)
        q = Game.query(ancestor=ndb.Key(User, user_id))
        activeGames = []
        for game in q:
            if game.game_over == False:
                activeGames.append(StringMessage(message=game.key.urlsafe()))
        return StringMessages(items=activeGames)

    @endpoints.method(GET_GAME_REQUEST,StringMessage,
                      name = 'cancel_game',
                      http_method='POST')
    def cancel_game(self,request):
        """ Cancel an active game """
        game_key = ndb.Key(urlsafe=request.urlsafe_game_key)
        game = game_key.get()

        # check user
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')
        user_id = getUserId(user)
        u_key = ndb.Key(User, user_id)
        if u_key != game.user:
            raise endpoints.UnauthorizedException('Auth required')
        
        
        if game.game_over == False:
            game_key.delete()
        else:
            raise endpoints.BadRequestException('game not active!')
        return StringMessage(message="game deleted")

    @endpoints.method(message_types.VoidMessage, ScoreForms,
                      name = 'get_high_scores',
                      http_method = 'GET')
    def get_high_scores(self, request):
        """ get high scores """
        q = Score.query()
        q = q.order(Score.guesses)
        q = q.fetch(5)
        return ScoreForms(items=[score.to_form() for score in q])

    @endpoints.method(message_types.VoidMessage,RankingForms,
                      name = 'get_user_rankings',
                      http_method = 'GET')
    def get_user_rankings(self,request):
        """ get user rankings """
        q = User.query()
        q = q.order(-User.wins)
        
        rankings = []
        for u in q:
            rankings.append(RankingForm(user_name=u.name, wins=u.wins))
        return RankingForms(user_rankings=rankings)

    @endpoints.method(GET_GAME_REQUEST,HistoryForms,
                      name = 'get_game_history',
                      http_method = 'GET')
    def get_game_history(self,request):
        """ get game history"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)

        if game.moves:
            history = []
            for m in game.moves:
                history.append(HistoryForm(move=m))
            return HistoryForms(moves = history)
        
        
    
        

api = endpoints.api_server([GuessANumberApi])
