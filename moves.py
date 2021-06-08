import operator
import numpy as np
from itertools import count, product


class State():
    def __init__(self):
        self.board = np.array([
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],
        ])

        self.init_board = self.board.tolist()

        self.whiteToMove = True

        self.is_check = None

        self.moveLog = []

        self.boardStateLog = []

        self.king_moved = set()

    def move(self, start, end):
        if not self.get_Valid_moves(start, end):
            print('Invalid Move')
            flag = 1
        else:
            flag = 0

        moved_piece = self.board[start[0]][start[1]]
        captured_piece = self.board[end[0]][end[1]]

        if moved_piece == '--':
            return self.board

        board = np.asarray(self.board)
        self.board[end[0]][end[1]] = moved_piece
        self.board[start[0]][start[1]] = '--'
        self.whiteToMove = not self.whiteToMove

        # Update Logs
        # Arrays as they are immutable
        self.moveLog.append(self.notation(end, captured_piece))
        self.boardStateLog.append(board.tolist())

        # Check for any Checks to any king
        if self.is_check_to_king(self.board):
            self.is_check, check_statement = self.is_check_to_king(self.board)
        if (self.is_check == -1 and self.whiteToMove is True) or (self.is_check == 1 and self.whiteToMove is False):
            print('Invalid Move: King in Check')
            flag = 1
        else:
            self.is_check = 0

        # Check if the Pawn is promoted
        self.pawn_promotion(self.board)

        # Castling
        self.king_moved = self.is_king_moved(self.moveLog,flag)

        if flag == 1:
            if len(self.boardStateLog) == 1:
                self.boardStateLog = [self.init_board, self.init_board]
            self.undo_move()

        return self.board

    def undo_move(self):
        if self.moveLog:
            self.moveLog.pop()
            self.boardStateLog.pop()
            self.whiteToMove = not self.whiteToMove

            if self.boardStateLog:
                self.board = np.asarray(self.boardStateLog)[-1]
            return self.board

    def notation(self, position, captured_piece):
        column_conversion = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        row_conversion = ['8', '7', '6', '5', '4', '3', '2', '1']

        piece = self.board[position[0]][position[1]][1]
        piece = '' if piece is 'P' else piece

        captured_piece = '' if captured_piece == '--' else 'x'

        notation = piece + captured_piece + column_conversion[position[1]] + row_conversion[position[0]]
        return notation

    def get_Valid_moves(self, start, end):
        pm = PieceMovement()

        # Incase of double click on one piece
        self.whiteToMove = not self.whiteToMove if start == end else self.whiteToMove

        # Piece Information
        piece_colour = self.board[start[0]][start[1]][0]
        capture_colour = self.board[end[0]][end[1]][0]

        # Move Validation
        correct_capture = piece_colour != capture_colour
        correct_move = (piece_colour is 'w' and self.whiteToMove) or (piece_colour is 'b' and not self.whiteToMove)
        is_valid_move = correct_move and correct_capture and pm.valid_piece_movement(start, end, self.board, self.moveLog)[1]

        return is_valid_move

    def all_possible_moves(self, board):
        pm = PieceMovement()
        white_moves, black_moves = [], []
        for i in range(len(board)):
            for j in range(len(board)):
                start = (i, j)
                if board[start][0] is 'w':
                    white_moves.extend(pm.valid_piece_movement(start, None, board, self.moveLog)[0])
                if board[start][0] is 'b':
                    black_moves.extend(pm.valid_piece_movement(start, None, board, self.moveLog)[0])
        return white_moves, black_moves

    def is_check_to_king(self, board):
        white_moves, black_moves = self.all_possible_moves(board)

        # Position of Respective Kings on the Board
        bK_pos, wK_pos = [], []
        x_black, y_black = np.where(board == 'bK')
        if x_black.tolist() and y_black.tolist():
            bK_pos = tuple((x_black[0], y_black[0]))

        x_white, y_white = np.where(board == 'wK')
        if x_white.tolist() and y_white.tolist:
            wK_pos = tuple((x_white[0], y_white[0]))

        if bK_pos in white_moves:
            return -1, 'Check to the Black King'
        elif wK_pos in black_moves:
            return 1, 'Check to the White King'
        else:
            return 0, None

    def is_king_moved(self,moveLog,valid):
        if valid == 0:
            for num,i in enumerate(moveLog):
                if i[0] == 'K' and num%2 == 0:
                    self.king_moved.add(1)
                if i[0] == 'x' and i[1] == 'K' and num%2 == 0:
                    self.king_moved.add(1)
                if i[0] == 'K' and num%2 == 1:
                    self.king_moved.add(-1)
                if i[0] == 'x' and i[1] == 'K' and num%2 == 1:
                    self.king_moved.add(-1)
        return self.king_moved

    def pawn_promotion(self, board):
        white_promotion = np.where(board[0, :] == 'wP')[0]
        black_promotion = np.where(board[7, :] == 'bP')[0]

        if white_promotion:
            self.board[0][white_promotion[0]] = 'wQ'
        if black_promotion:
            self.board[7][black_promotion[0]] = 'bQ'

class PieceMovement(State):
    global king_moved
    def __init__(self):
        super().__init__()
        self.pawn_moves = []

    def valid_piece_movement(self, start, end, board, moveLog):

        piece = board[start[0]][start[1]][1]

        if piece is 'P':
            moves, valid = self.valid_pawn_movement(start, end, board)
        elif piece is 'R':
            moves, valid = self.valid_rook_movement(start, end, board)
        elif piece is 'B':
            moves, valid = self.valid_bishop_movement(start, end, board)
        elif piece is 'Q':
            moves, valid = self.valid_queen_movement(start, end, board)
        elif piece is 'N':
            moves, valid = self.valid_knight_movement(start, end, board)
        elif piece is 'K':
            moves, valid = self.valid_king_movement(start, end, board)
        else:
            moves,valid  = [],True
        return moves, valid

    def valid_pawn_movement(self, start, end, board):
        r, c = start
        pawn_colour = board[(r, c)][0]

        # Movement for White Pawn
        square = []
        if end!= None:
            self.pawn_moves.extend([start[0],end[0]])
        if pawn_colour == 'w':
            if 0 <= c <= 7 and r - 1 >= 0:
                if r == 6:
                    if board[(r - 1, c)] == '--':
                        square.append((r - 1, c))
                    if board[(r - 1, c)] == '--' and board[(r - 2, c)] == '--':
                        square.extend([(r - 1, c), (r - 2, c)])
                else:
                    if board[(r - 1, c)] == '--':
                        square.append((r - 1, c))
                if 0 <= c - 1 <= 7:
                    if board[(r - 1, c - 1)][0] == 'b':
                        square.append((r - 1, c - 1))
                if 0 <= c + 1 <= 7:
                    if board[(r - 1, c + 1)][0] == 'b':
                        square.append((r - 1, c + 1))
        else:
            if 0 <= c <= 7 and r + 1 <= 7:
                if r == 1:
                    if board[(r + 1, c)] == '--':
                        square.append((r + 1, c))
                    if board[(r + 1, c)] == '--' and board[(r + 2, c)] == '--':
                        square.extend([(r + 1, c), (r + 2, c)])
                else:
                    if board[(r + 1, c)] == '--':
                        square.append((r + 1, c))
                if 0 <= c + 1 <= 7:
                    if board[(r + 1, c + 1)][0] == 'w':
                        square.append((r + 1, c + 1))
                if 0 <= c + 1 <= 7:
                    if r == 4 and board[(r, c + 1)] == 'wP':
                        square.append((r + 1, c + 1))
                if 0 <= c - 1 <= 7:
                    if board[(r + 1, c - 1)][0] == 'w':
                        square.append((r + 1, c - 1))
        en_passand_squares, removal = self.en_passant(start, board)
        square.extend(en_passand_squares) if en_passand_squares else []

        if end in en_passand_squares:
            index = en_passand_squares.index(end)
            e1, e2 = removal[index][0]
            board[(e1, e2)] = '--'

        valid = (end[0], end[1]) in square if end != None else None
        return square, valid

    def en_passant(self, start, board):
        arr = np.zeros((16))
        r, c = start

        #if board[(r, c)][0] == 'w':
        #    arr[] print(arr)

        en_passant_squares, removal = [], []
        if board[(r, c)][0] == 'w':
            if 0 <= c - 1 <= 7 and r == 3 and board[(r, c - 1)] == 'bP':
                en_passant_squares.extend([(r - 1, c - 1)])
                removal.append([(r, c - 1)])
            if 0 <= c + 1 <= 7 and r == 3 and board[(r, c + 1)] == 'bP':
                en_passant_squares.extend([(r - 1, c + 1)])
                removal.append([(r, c + 1)])
        if board[(r, c)][0] == 'b':
            if 0 <= c - 1 <= 7 and r == 4 and board[(r, c - 1)] == 'wP':
                en_passant_squares.extend([(r + 1, c - 1)])
                removal.append([(r, c - 1)])
            if 0 <= c + 1 <= 7 and r == 4 and board[(r, c + 1)] == 'wP':
                en_passant_squares.extend([(r + 1, c + 1)])
                removal.append([(r, c + 1)])
        return en_passant_squares, removal

    def valid_rook_movement(self, start, end, board):
        # All the possible directions of the Rook
        up = list(product(list(range(start[0], -1, -1)), [start[1]]))[1:]
        down = list(product(list(range(start[0], 8)), [start[1]]))[1:]
        left = list(product([start[0]], list(range(start[1], -1, -1))))[1:]
        right = list(product([start[0]], list(range(start[1], 8))))[1:]
        all_directions = [up, down, left, right]

        # Piece information at (x,y) position of the board
        board_piece = lambda y: map(lambda x: board[x[0]][x[1]], y)

        # Function providing valid movements for the rook
        def directional_moves(lst):
            count = 0
            if not lst: count += 1
            for k in lst:
                count += 1
                if k == '--':  # Empty Space
                    pass
                elif k[0] != board[start[0]][start[1]][0]:  # Capture of the piece
                    break
                else:  # Everything else
                    count -= 1
                    break
            return count

        # List of all possible movements of board indices in tuple format
        moves = []
        for direction in all_directions:
            c = directional_moves(list(board_piece(direction)))
            moves.extend(direction[:c])

        # Validation check if the end movement lies in the valid scope of movement
        valid = (end[0], end[1]) in moves if end != None else None
        return moves, valid

    def valid_bishop_movement(self, start, end, board):
        y, x = start

        def append(dx, dy):
            for i in count(start=1):
                newx = x + dx * i
                newy = y + dy * i
                if i == 1: moves = []
                if 0 <= newx < 8 and 0 <= newy < 8:
                    sq = (newy, newx)
                    moves.append(sq)
                else:
                    break
            yield moves

        all_moves = []
        for dx in (-1, 1):
            for dy in (-1, 1):
                all_moves.extend(list(append(dx, dy)))

        moves = []
        for direction in all_moves:
            if direction:
                for i in direction:
                    if board[i] == '--':
                        moves.append(i)
                    elif board[i][0] != board[start[0]][start[1]][0]:
                        moves.append(i)
                        break
                    else:
                        break

        valid = (end[0], end[1]) in moves if end != None else None
        return moves, valid

    def valid_queen_movement(self, start, end, board):
        return self.valid_bishop_movement(start, end, board)[0] + self.valid_rook_movement(start, end, board)[0] \
            , self.valid_bishop_movement(start, end, board)[1] or self.valid_rook_movement(start, end, board)[1]

    def valid_knight_movement(self, start, end, board):
        x, y = start
        moves = list(product([x - 1, x + 1], [y - 2, y + 2])) + list(product([x - 2, x + 2], [y - 1, y + 1]))
        moves = [(x, y) for x, y in moves if x >= 0 and y >= 0 and x < 8 and y < 8]
        valid = (end[0], end[1]) in moves if end != None else None
        return moves, valid

    def valid_king_movement(self, start, end, board):
        moves_temp = list(
            map(lambda x: tuple(map(operator.add, x, (start[0], start[1]))), list(product([-1, 0, 1], repeat=2))))
        moves,moves_all = [],[]

        # Castling
        #moves_castling,king,rook,replace = self.castling(start, end, board, king_moved)
        #moves.extend(moves_castling)

        # King Moves
        for i in moves_temp:
            if (7 >= int(i[0]) >= 0) and i != start and board[i][0]!=board[start][0]:
                moves.append(i)

        #if king in moves and end == king:
        #    board[king] = 'wK'
        #    board[rook] = 'wR'
        #    board[replace] = '--'

        valid = (end[0], end[1]) in moves if end != None else None
        return moves, valid

    def castling(self, start, end, board, king_moved):
        if 1 not in king_moved and board[7][7] == 'wR' and end == tuple((7, 6)) \
                and board[start[0]][start[1]] == 'wK' and board[(7,5)] == '--' and board[(7,6)] == '--':
            moves,king,rook,replace = [(7,6)], tuple((7,6)), tuple((7,5)), tuple((7,7))
        elif 1 not in king_moved and board[7][0] == 'wR' and end == tuple((7, 2)) \
                and board[start[0]][start[1]] == 'wK' and board[(7,1)] == '--' and board[(7,2)] == '--' and board[(7,3)] == '--':
            moves,king,rook,replace = [(7,2)], tuple((7,2)), tuple((7,3)), tuple((7,0))
        elif -1 not in king_moved and board[0][0] == 'bR' and end == tuple((0, 2)) \
                and board[start[0]][start[1]] == 'bK' and board[(0,1)] == '--' and board[(0,2)] == '--' and board[(0,3)] == '--':
            moves,king,rook,replace = [(0,2)], tuple((0,2)), tuple((0,3)), tuple((0,0))
        else:
            moves,king,rook,replace = [],0,0,0
        return moves,king,rook,replace