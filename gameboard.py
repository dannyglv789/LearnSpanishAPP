board = [[1, 1], [1, 2], [1, 3], [1, 4], [2, 1], [2, 2], [2, 3], [2, 4], [3, 1], [3, 2], [3, 3], [3, 4], [4, 1], [4, 2], [4, 3], [4, 4]]
# bottom row is legal at first
legal = [[1,1], [1, 2], [1, 3], [1, 4]]
moves = []

def player_move(move):
    """ player_move algorithm. If move is illegal, move is rejected.
        If move is legal, move is played and the above move becomes legal
    """
    if move not in legal:
        print "sorry try again"
    else:
        # slot above move becomes legal
        # get the move index so we have a reference point for the next
        # move that becomes legal, then append new legal move to legal list
        move_index = -1
        for i in board:
            move_index +=1
            if i == move:
                break
            
        legal_spot = move_index + 4
        if board[legal_spot] not in legal:
            legal.append(board[legal_spot])
        print legal
        return board[legal_spot]

player_move([1,1])
