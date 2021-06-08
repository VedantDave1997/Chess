import pygame as py
import moves

# Board Configurations
height = width = 512
dimensions = 8
sq_size = height/dimensions
max_fps = 15
images = {}

def load_images():
    pieces = ["wP","wR","wN","wB","wK","wQ","bP","bR","bN","bB","bK","bQ"]

    for piece in pieces:
        images[piece] = py.transform.scale(py.image.load("images/"+piece+".png"),(int(sq_size),int(sq_size)))

def draw_game_state(screen,gs):
    draw_Board(screen)
    draw_Pieces(screen,gs.board)

def draw_Board(screen):
    colors = [py.Color("white"),py.Color("gray")]

    for r in range(dimensions):
        for c in range(dimensions):
            color = colors[((r+c)%2)]
            py.draw.rect(screen,color,py.Rect(c*sq_size,r*sq_size,sq_size,sq_size))

def draw_Pieces(screen,board):
    for r in range(dimensions):
        for c in range(dimensions):
            piece = board[r][c]
            if piece != '--':
                screen.blit(images[piece],py.Rect(c*sq_size,r*sq_size,sq_size,sq_size))

def chess_game():

    # Screen Setup
    screen = py.display.set_mode((height,width))
    clock = py.time.Clock()
    screen.fill(py.Color("white"))

    # Game State Access and Drawing Board
    board_state = moves.State()
    load_images()
    running = True

    selected = []

    while running:
        for e in py.event.get():

            if e.type == py.QUIT:
                running = False

            elif e.type == py.MOUSEBUTTONDOWN:
                location = py.mouse.get_pos()
                column = int(location[0]//sq_size)
                row = int(location[1] / sq_size)
                selected.append((row,column))

                #is_illegal = board_state.is_illegal()

                if len(selected)>1 and selected[0] == selected[1] or \
                        board_state.board[selected[0][0]][selected[0][1]] == '--': #or is_illegal:
                    selected = []

                if len(selected) == 2:
                    board_state.move(selected[0], selected[1])
                    selected = []

            elif e.type == py.KEYDOWN:
                if e.key == py.K_z:
                    print('Undo')
                    board_state.undo_move()

        draw_game_state(screen,board_state)
        clock.tick(max_fps)
        py.display.flip()


chess_game()
