board = [[1, 1], [1, 2], [1, 3], [1, 4],
         [2, 1], [2, 2], [2, 3], [2, 4],
         [3, 1], [3, 2], [3, 3], [3, 4],
         [4, 1], [4, 2], [4, 3], [4, 4]]

# bottom row is legal at first
legal = [[1,1], [1, 2], [1, 3], [1, 4]]
print legal
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

def player_move(move, player):
    """ player_move algorithm. If move is illegal, move is rejected.
        If move is legal, move is played and the slot above move becomes legal
        move_index: the list position of the player move
        legal_spot: the newly legal position based on move_index
    """
    if move not in legal:
        print "sorry try again, move not allowed"
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

for i in wins:
    if i == []:
        print "You won!"

for i in computer_wins:
    if i == []:
        print "Sorry you lost."
