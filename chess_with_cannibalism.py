class Board():
    def __init__(self, board = None, alt_board = None, castling_rights = None):
        self.board = [["BR", "BN", "BB", "BQ", "BK", "BB", "BN", "BR"],
                      ["BP", "BP", "BP", "BP", "BP", "BP", "BP", "BP"],
                      ["" for _ in range(8)],
                      ["" for _ in range(8)],
                      ["" for _ in range(8)],
                      ["" for _ in range(8)],
                      ["WP", "WP", "WP", "WP", "WP", "WP", "WP", "WP"],
                      ["WR", "WN", "WB", "WQ", "WK", "WB", "WN", "WR"]] if board is None else board
        self.alt_board = [["" for _ in range(8)] for _ in range(8)] if alt_board is None else alt_board
        self.castling_rights = {"W": {"Q": True, "K": True}, "B": {"Q": True, "K": True}} if castling_rights is None else castling_rights
    def GetValidMoves(self, start, board = None, check_if_check = True):
        if board is None:
            board = self.board
        moves = []
        if board[start[0]][start[1]] == "":
            if self.alt_board[start[0]][start[1]] != "":
                return [start]
        else:
            if board[start[0]][start[1]][1] == "R" or board[start[0]][start[1]][1] == "Q": # ROOK / QUEEN
                for direction in [-1, 1]: # Move in both positive and negative directions
                    for i_shift in [True, False]: # Move in both i and j directions
                        for shift in range(1, 8): # Move between 1 and 7 positions
                            if not (0 <= start[0 if i_shift else 1] + shift * direction <= 7):
                                break # Invalid position
                            target = (board[start[0] + shift * direction][start[1]] if i_shift else board[start[0]][start[1] + shift * direction])
                            if target == "":
                                moves.append((start[0] + shift * direction, start[1]) if i_shift else (start[0], start[1] + shift * direction))
                            else:
                                moves.append((start[0] + shift * direction, start[1]) if i_shift else (start[0], start[1] + shift * direction)) # Valid capture/cannibalism
                                break # Cannot proceed further in direction
            if board[start[0]][start[1]][1] == "N": # KNIGHT
                for shift in ((-2, -1), (-2, 1), (2, -1), (2, 1), (-1, -2), (1, -2), (-1, 2), (1, 2)):
                    if not ((0 <= start[0] + shift[0] <= 7) and (0 <= start[1] + shift[1] <= 7)):
                        continue # Invalid position
                    moves.append((start[0] + shift[0], start[1] + shift[1])) # Valid move/capture/cannibalism
            if board[start[0]][start[1]][1] == "B" or board[start[0]][start[1]][1] == "Q": # BISHOP / QUEEN
                for i_direction in [-1, 1]: # Move in positive and negative i and j directions
                    for j_direction in [-1, 1]:
                        for shift in range(1, 8): # Move between 1 and 7 positions
                            if not ((0 <= start[0] + shift * i_direction <= 7) and (0 <= start[1] + shift * j_direction <= 7)):
                                break # Invalid position
                            moves.append((start[0] + shift * i_direction, start[1] + shift * j_direction))
                            if board[start[0] + shift * i_direction][start[1] + shift * j_direction] != "":
                                break # Cannot proceed further in direction
            if board[start[0]][start[1]][1] == "K": # KING
                for i_shift in range(-1, 2):
                    for j_shift in range(-1, 2):
                        if i_shift != 0 or j_shift != 0:
                            if not ((0 <= start[0] + i_shift <= 7) and (0 <= start[1] + j_shift <= 7)):
                                continue # Invalid position
                            moves.append((start[0] + i_shift, start[1] + j_shift))
            if board[start[0]][start[1]][1] == "P": # PAWN
                for j_shift in range(-1, 2): # Capture diagonally or move with no j_shift without capture
                    if not ((0 <= start[0] + (-1 if board[start[0]][start[1]][0] == "W" else 1) <= 7) and (0 <= start[1] + j_shift <= 7)):
                        continue # Invalid position
                    if board[start[0] + (-1 if board[start[0]][start[1]][0] == "W" else 1)][start[1] + j_shift] != "":
                        moves.append((start[0] + (-1 if board[start[0]][start[1]][0] == "W" else 1), start[1] + j_shift))
                    elif j_shift == 0: # Move without capture to empty position
                        moves.append((start[0] + (-1 if board[start[0]][start[1]][0] == "W" else 1), start[1]))
                if (board[start[0]][start[1]][0] == "W" and start[0] == 6) or (board[start[0]][start[1]][0] == "B" and start[0] == 1):
                    if board[start[0] + (-1 if board[start[0]][start[1]][0] == "W" else 1)][start[1]] == "" and board[start[0] + (-2 if board[start[0]][start[1]][0] == "W" else 2)][start[1]] == "": # Must both be empty positions
                        moves.append((start[0] + (-2 if board[start[0]][start[1]][0] == "W" else 2), start[1]))
        if board[start[0]][start[1]] != "": # Remove cannibalism of higher-value pieces
            piece_values = {"P": 1, "N": 3, "B": 3, "R": 5, "Q": 9, "K": float("inf")}
            remove_is = []
            for i, move in enumerate(moves):
                if board[move[0]][move[1]] != "":
                    if board[start[0]][start[1]][0] == board[move[0]][move[1]][0]:
                        if piece_values[board[start[0]][start[1]][1]] < piece_values[board[move[0]][move[1]][1]]:
                            remove_is.append(i)
            for i in remove_is[::-1]:
                moves.pop(i) # Remove invalid moves
        if check_if_check:
            remove_is = []
            for i, move in enumerate(moves):
                if self.CheckInCheck(self.board[start[0]][start[1]][0], self.GetBoardWithMove(start, move)[0]): # Moves cannot place the current player in check
                    remove_is.append(i)
            for i in remove_is[::-1]:
                moves.pop(i) # Remove invalid moves
        return moves # Return possible moves
    def FilterAltMoves(self, start, moves):
        if self.board[start[0]][start[1]] == "":
            return moves.copy() # Only possible move is from alternate board
        alt_moves = []
        for move in moves:
            if self.board[move[0]][move[1]] != "":
                if self.board[move[0]][move[1]][0] == self.board[start[0]][start[1]][0]: # Cannibalistic move
                    alt_moves.append(move)
        return alt_moves
    def CheckCastleValid(self, castle_colour, castle_side):
        return self.castling_rights[castle_colour][castle_side] and self.board[7 if castle_colour == "W" else 0][0 if castle_side == "Q" else 7] == castle_colour + "R" and self.board[7 if castle_colour == "W" else 0][4] == castle_colour + "K"
    def GetBoardWithMove(self, start, end):
        moved_board = [row.copy() for row in self.board]
        moved_alt_board = [row.copy() for row in self.alt_board]
        if moved_board[start[0]][start[1]] != "" and moved_board[end[0]][end[1]] != "": # Pieces present to make check
            if moved_board[start[0]][start[1]][0] == moved_board[end[0]][end[1]][0]: # Cannibalism
                moved_alt_board[end[0]][end[1]] = moved_board[end[0]][end[1]] # Move target piece to alternate board
        moved_board[end[0]][end[1]] = moved_board[start[0]][start[1]]
        moved_board[start[0]][start[1]] = ""
        return moved_board, moved_alt_board
    def GetBoardWithCastle(self, castle_colour, castle_side):
        moved_board = [row.copy() for row in self.board]
        moved_board[7 if castle_colour == "W" else 0][0 if castle_side == "Q" else 7] = ""
        moved_board[7 if castle_colour == "W" else 0][2 if castle_side == "Q" else 5] = castle_colour + "R"
        moved_board[7 if castle_colour == "W" else 0][4] = ""
        moved_board[7 if castle_colour == "W" else 0][1 if castle_side == "Q" else 6] = castle_colour + "K"
    def MakeMove(self, start, end):
        if start == end and self.alt_board[start[0]][start[1]] != "": # Summoning piece from alternate board
            self.board[start[0]][start[1]] = self.alt_board[start[0]][start[1]] # Move piece from alternate board to main board
            self.alt_board[start[0]][start[1]] = ""
            return
        if self.board[start[0]][start[1]] != "":
            if start[0] == (7 if self.board[start[0]][start[1]][0] == "W" else 0) and (start[1] == 0 or start[1] == 7) and self.board[start[0]][start[1]][1] == "R": # Moving a rook from starting position
                self.castling_rights[self.board[start[0]][start[1]][0]]["Q" if start[1] == 0 else "K"] = False # Remove relevant castling rights
            elif start[0] == (7 if self.board[start[0]][start[1]][0] == "W" else 0) and start[1] == 4 and self.board[start[0]][start[1]][1] == "K": # Moving the king from starting position
                self.castling_rights[self.board[start[0]][start[1]][0]]["Q"] = False # Remove all castling rights
                self.castling_rights[self.board[start[0]][start[1]][0]]["K"] = False
            if self.board[end[0]][end[1]] != "": # Pieces present to make check
                if self.board[start[0]][start[1]][0] == self.board[end[0]][end[1]][0]: # Cannibalism
                    self.alt_board[end[0]][end[1]] = self.board[end[0]][end[1]] # Move target piece to alternate board
        self.board[end[0]][end[1]] = self.board[start[0]][start[1]]
        self.board[start[0]][start[1]] = ""
    def MakeCastle(self, castle_colour, castle_side):
        self.board[7 if castle_colour == "W" else 0][0 if castle_side == "Q" else 7] = ""
        if self.board[7 if castle_colour == "W" else 0][2 if castle_side == "Q" else 5] != "":
            self.alt_board[7 if castle_colour == "W" else 0][2 if castle_side == "Q" else 5] = self.board[7 if castle_colour == "W" else 0][1 if castle_side == "Q" else 5]
        self.board[7 if castle_colour == "W" else 0][2 if castle_side == "Q" else 5] = castle_colour + "R"
        self.board[7 if castle_colour == "W" else 0][4] = ""
        if self.board[7 if castle_colour == "W" else 0][1 if castle_side == "Q" else 6] != "":
            self.alt_board[7 if castle_colour == "W" else 0][1 if castle_side == "Q" else 6] = self.board[7 if castle_colour == "W" else 0][2 if castle_side == "Q" else 6]
        self.board[7 if castle_colour == "W" else 0][1 if castle_side == "Q" else 6] = castle_colour + "K"
        self.castling_rights[castle_colour] = {"Q": False, "K": False} # Remove all castling rights for colour
    def MergeAltBoard(self, merge_colour):
        merged_board = [row.copy() for row in self.board]
        for i, row in enumerate(self.alt_board):
            for j, piece in enumerate(row):
                if piece != "":
                    if piece[0] == merge_colour:
                        merged_board[i][j] = piece
        return merged_board
    def CheckInCheck(self, target_colour, board = None):
        if board is None:
            board = self.board
        target_king = None
        for i, row in enumerate(board): # Find target king
            for j, piece in enumerate(row):
                if piece == target_colour + "K":
                    target_king = (i, j) # Save king position
                    break
            if not target_king is None:
                break # King found
        if target_colour is None:
            return False # No king present to attack
        for i, row in enumerate(board): # Find attacking pieces
            for j, piece in enumerate(row):
                if piece != "":
                    if piece[0] != target_colour: # Opponent piece
                        if target_king in self.GetValidMoves((i, j), board, False):
                            return True
        return False
    def CheckInMate(self, target_colour, board = None):
        if board is None:
            board = self.board
        if self.CheckInCheck(target_colour, board):
            for i, row in enumerate(board): # Find attacking pieces
                for j, piece in enumerate(row):
                    if len(self.GetValidMoves((i, j), board)) != 0:
                        if piece == "":
                            return False # Piece can be summoned to empty position from alternate board
                        if piece[0] == target_colour: # Checked player piece
                            print((i, j), piece, self.GetValidMoves((i, j), board))
                            return False # Possible moves to escape check, not mate
            return True # No possible moves, mate
        return False # Not in check
class TextInterface():
    def DisplayBoard(self, board, alt_board, turn):
        board_str = "   a   b   c   d   e   f   g   h        a   b   c   d   e   f   g   h\n" # Add column indices
        for i in range(8):
            board_str += str(8 - i) + " " # Add row index
            for piece in board[i]:
                board_str += "[" + (piece if piece != "" else "  ") + "]" # Add piece code or blank square
            board_str += "  |  "
            for piece in alt_board[i]:
                board_str += "[" + (piece if piece != "" else "  ") + "]" # Add piece code or blank square
            board_str += " " + str(8 - i) + " \n" # Add row index and new line
        print(board_str + "   a   b   c   d   e   f   g   h        a   b   c   d   e   f   g   h") # Add column indices
        print("Turn: " + ("White" if turn else "Black"))
    def DisplayBoardWithMoves(self, board, alt_board, start, moves, alt_moves):
        board_str = "   a   b   c   d   e   f   g   h        a   b   c   d   e   f   g   h\n" # Add column indices
        for i in range(8):
            board_str += str(8 - i) + " " # Add row index
            for j, piece in enumerate(board[i]):
                if (i, j) == start:
                    board_str += "{" + (piece if piece != "" else "  ") + "}"
                else:
                    board_str += ("[" if (i, j) in moves else " ") + (piece if piece != "" else "  ") + ("]" if (i, j) in moves else " ") # Add piece code or blank square
            board_str += "  |  "
            for j, piece in enumerate(alt_board[i]):
                board_str += ("[" if (i, j) in alt_moves else " ") + (piece if piece != "" else "  ") + ("]" if (i, j) in alt_moves else " ") # Add piece code or blank square
            board_str += " " + str(8 - i) + " \n" # Add row index and new line
        print(board_str + "   a   b   c   d   e   f   g   h        a   b   c   d   e   f   g   h") # Add column indices
    def GetStartMove(self):
        start_not = input("Enter start position (as notation, e.g. 'e4'), castle type ('Q'/'K') or 'exit': ").lower()
        if start_not == "exit":
            return None, None, False # End game loop
        return self.ConvertNotationToPosition(start_not) if not start_not.upper() in ["Q", "K"] else start_not.upper(), start_not.upper() in ["Q", "K"], True # Return position or castle type
    def GetEndMove(self):
        end_not = input("Enter target position (as notation, e.g. 'e4') or 'cancel' to reselect start position: ").lower()
        if end_not == "cancel":
            return None, False # Reselect start position
        return self.ConvertNotationToPosition(end_not), True
    def ConvertNotationToPosition(self, notation: str):
        return (8 - int(notation[1]), ord(notation[0].lower()) - 97)
class ChessGame():
    def __init__(self):
        self.interface = TextInterface()
    def PlayGame(self):
        turn = True
        board = Board()
        playing = True
        game_won = False
        while playing:
            selecting_move = True
            while selecting_move and playing:
                self.interface.DisplayBoard(board.board, board.alt_board, turn)
                if board.CheckInCheck("W" if turn else "B"):
                    print("In check")
                start, is_castle, playing = self.interface.GetStartMove()
                if is_castle:
                    if board.CheckCastleValid("W" if turn else "B", start):
                       break
                    else:
                        print("Castle invalid")
                        continue
                if not playing:
                    break
                if board.board[start[0]][start[1]] == "" and board.alt_board[start[0]][start[1]] == "":
                    print("No piece selected")
                    continue
                if (board.board if board.board[start[0]][start[1]] != "" else board.alt_board)[start[0]][start[1]][0] != ("W" if turn else "B"):
                    print("Opponent piece selected")
                    continue
                moves = board.GetValidMoves(start)
                if len(moves) > 0:
                    selecting_end = True
                    while selecting_end:
                        self.interface.DisplayBoardWithMoves(board.board, board.alt_board, start, moves, board.FilterAltMoves(start, moves))
                        end, selecting_end = self.interface.GetEndMove()
                        if not selecting_end:
                            break
                        if end in moves:
                            selecting_end = False
                            selecting_move = False
                        else:
                            print("Move invalid")
                else:
                    print("No possible moves")
                    selecting_end = False # Reselect start move
            if not playing:
                break
            if is_castle:
                board.MakeCastle("W" if turn else "B", start)
            else:
                if end in board.GetValidMoves(start):
                    board.MakeMove(start, end)
                if board.CheckInMate("B" if turn else "W"):
                    game_won = True
                    playing = False
            turn = not turn
        if game_won:
            print(("Black" if turn else "White") + "won")
ChessGame().PlayGame()