#Spanish Word Guessing Game 

## Set-Up Instructions:
1. The API can be accessed at https://gameapp-1266.appspot.com/_ah/api/explorer
 
 
 
##Game Description:
In Learn Spanish users receive a spanish word with a specified number of 
attempts to guess the english translation. 

1. Create user at create_user endpoint (requires auth) 
2. Create new game at new_game endpoint
3. Use urlsafe_game_key to view created game and scrambled word at get_game endpoint
4. Use urlsafe_game_key to make a move at make_move endpoint untill win or loss reply.
5. Each game can be retrieved or played at get_user_games endpoint

##Files Included:
 - api.py: Contains endpoints and game playing logic.
 - app.yaml: App configuration.
 - cron.yaml: Cronjob configuration.
 - main.py: Handler for taskqueue handler.
 - models.py: Entity and message definitions including helper methods.
 - utils.py: Helper function for retrieving ndb.Models by urlsafe Key string.
 
##Endpoints Added: 
 - **add_unscramble_word**
    - Method: POST
    - Parameters: word
    - Returns: key of word created
    - Description: creates word for future games to scramble
	
 - **get_user_games**
    - Method: GET
    - Parameters: none
    - Returns: Active user games
    - Description: Returns current users active games. Requires Authorization
	
 - **cancel_game**
    - Method: POST
    - Parameters: urlsafe_game_key
    - Returns: Message confirming deletion of game.
    - Description: Cancels an active game. Raises badrequest error if game
	not active
	
 - **get_high_scores**
    - Method: GET
    - Parameters: none
    - Returns: List of top 5 scores
    - Description: Returns User scores by number of guesses
	
 - **get_user_rankings**
    - Method: GET
    - Parameters: none
    - Returns: List of users ranked by number of wins
    - Description: Returns users ranked by number of wins
	
 - **get_game_history**
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: List moves in order for each game
    - Description: returns list of moves in order for each game
	
##Endpoints Included:
 - **create_user**
    - Path: 'user'
    - Method: POST
    - Parameters: user_name, email (optional)
    - Returns: Message confirming creation of the User.
    - Description: Creates a new User. user_name provided must be unique. Will 
    raise a ConflictException if a User with that user_name already exists.
    
 - **new_game**
    - Path: 'game'
    - Method: POST
    - Parameters: user_name, attempts
    - Returns: GameForm with initial game state.
    - Description: Creates a new Game. Selects a random word from the words entity
      and scrambles it.	user_name provided must correspond to an
    existing user - will raise a NotFoundException if not. Min must be less than
    max. Also adds a task to a task queue to update the average moves remaining
    for active games.
     
 - **get_game**
    - Path: 'game/{urlsafe_game_key}'
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: GameForm with current game state.
    - Description: Returns the current state of a game.
    
 - **make_move**
    - Path: 'game/{urlsafe_game_key}'
    - Method: PUT
    - Parameters: urlsafe_game_key, guess
    - Returns: GameForm with new game state.
    - Description: Accepts a 'guess' and returns the updated state of the game.
    If this causes a game to end, a corresponding Score entity will be created.
    
 - **get_scores**
    - Path: 'scores'
    - Method: GET
    - Parameters: None
    - Returns: ScoreForms.
    - Description: Returns all Scores in the database (unordered).
    
 - **get_user_scores**
    - Path: 'scores/user/{user_name}'
    - Method: GET
    - Parameters: user_name
    - Returns: ScoreForms. 
    - Description: Returns all Scores recorded by the provided player (unordered).
    Will raise a NotFoundException if the User does not exist.
    
 - **get_active_game_count**
    - Path: 'games/active'
    - Method: GET
    - Parameters: None
    - Returns: StringMessage
    - Description: Gets the average number of attempts remaining for all games
    from a previously cached memcache key.
	
##Models Added:
 - *HangmanWords*
	- Stores words created by users, and scrambles them for games
	
##Models Included:
 - **User**
    - Stores unique user_name and (optional) email address.
    
 - **Game**
    - Stores unique game states. Associated with User model via KeyProperty.
    
 - **Score**
    - Records completed games. Associated with Users model via KeyProperty.

##Forms Added:
 - **RankingForm **
    - Used to rank players by win
	
 - **HistoryForm**
    - Used to return moves by game
	
##Forms Included:
 - **GameForm**
    - Representation of a Game's state (urlsafe_key, attempts_remaining,
    game_over flag, message, user_name).
 - **NewGameForm**
    - Used to create a new game (user_name, min, max, attempts)
 - **MakeMoveForm**
    - Inbound make move form (guess).
 - **ScoreForm**
    - Representation of a completed game's Score (user_name, date, won flag,
    guesses).
 - **ScoreForms**
    - Multiple ScoreForm container.
 - **StringMessage**
    - General purpose String container.

##SendReminderEmail 
 - email is sent to users with 3 or more wins only with good job message 
