import pygame
import random
import requests
from io import BytesIO

pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 700, 500  # Adjusted for 5x5 board
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess Puzzle: Solve the Puzzle!")

try:
        requests.get("https://maniksharma69420.github.io", timeout=3)
except requests.RequestException:
        def oh_no():
            f1nt = pygame.font.Font(None, 30)
            pain_message = f1nt.render("You need an Internet Connection to play this Game!", True, (0, 255, 0))
            screen.blit(pain_message, (125, 250))
            pygame.display.flip()
            pygame.time.delay(3000)  # Show the message for 3 seconds
            running = False
        oh_no()

a = random.randint(1, 2)

image_urls = [
    'https://maniksharma69420.github.io/white_pawn.png',
    'https://maniksharma69420.github.io/black_pawn.png',
    'https://maniksharma69420.github.io/white_queen.png',
    'https://maniksharma69420.github.io/black_queen.png'
]

# Colors
LIGHT_SQUARE = (240, 217, 181)
DARK_SQUARE = (181, 136, 99)
HIGHLIGHT_COLOR = (255, 255, 0)
RESET_BUTTON_COLOR = (200, 0, 0)  # Red for Reset button
RESET_TEXT_COLOR = (255, 255, 255)

# Load chess piece images
def load_image(url):
    """Fetch image from URL and load it into pygame."""
    response = requests.get(url)
    image_data = BytesIO(response.content)
    return pygame.image.load(image_data)

piece_images = {
    "white_queen": pygame.transform.scale(load_image(image_urls[2]), (80, 80)),
    "white_pawn": pygame.transform.scale(load_image(image_urls[0]), (80, 80)),
    "black_queen": pygame.transform.scale(load_image(image_urls[3]), (80, 80)),
    "black_pawn": pygame.transform.scale(load_image(image_urls[1]), (80, 80)),
}

# Chessboard and piece setup
board_size = 5  # Adjusted to 5x5
initial_puzzle_pieces = {
    "white": [("white_queen", (1, 5)), ("white_queen", (2, 5)), ("white_queen", (3, 5))],
    "black": [
        ("black_pawn", (4, 0)),
        ("black_pawn", (4, 1)),
        ("black_pawn", (4, 2)),
        ("black_pawn", (4, 3)),
        ("black_pawn", (4, 4))
    ],
}

puzzle_pieces = {
    "white": [piece for piece in initial_puzzle_pieces["white"]],
    "black": [piece for piece in initial_puzzle_pieces["black"]],
}

dragging = False
selected_piece = None
drag_offset = (0, 0)


# Check if a position is occupied by another piece
def is_occupied(pos):
    """Check if the given position is occupied by a piece."""
    for color_pieces in puzzle_pieces.values():
        for piece, piece_pos in color_pieces:
            if piece_pos == pos:
                return True
    return False


# Draw chessboard
def draw_board():
    for row in range(board_size):
        for col in range(board_size):
            color = LIGHT_SQUARE if (row + col) % 2 == 0 else DARK_SQUARE
            pygame.draw.rect(screen, color, (col * 100, row * 100, 100, 100))


# Draw chess pieces
def draw_pieces():
    for piece, pos in puzzle_pieces["white"]:
        img = piece_images[piece]
        x, y = pos[1] * 100 + 10, pos[0] * 100 + 10
        screen.blit(img, (x, y))

    for piece, pos in puzzle_pieces["black"]:
        img = piece_images[piece]
        x, y = pos[1] * 100 + 10, pos[0] * 100 + 10
        screen.blit(img, (x, y))


# Handle dragging logic
def handle_dragging(event):
    global dragging, selected_piece, drag_offset

    if event.type == pygame.MOUSEBUTTONDOWN:
        mouse_x, mouse_y = event.pos
        for color in ["white", "black"]:
            for idx, (piece, pos) in enumerate(puzzle_pieces[color]):
                img_rect = pygame.Rect(pos[1] * 100 + 10, pos[0] * 100 + 10, 80, 80)
                if img_rect.collidepoint(mouse_x, mouse_y):
                    dragging = True
                    selected_piece = (color, idx)
                    drag_offset = (mouse_x - img_rect.x, mouse_y - img_rect.y)
                    break
            if dragging:
                break

    elif event.type == pygame.MOUSEBUTTONUP:
        dragging = False
        selected_piece = None

    elif event.type == pygame.MOUSEMOTION and dragging:
        mouse_x, mouse_y = event.pos
        new_x = mouse_x - drag_offset[0]
        new_y = mouse_y - drag_offset[1]

        new_x = max(0, min(WIDTH - 80, new_x))
        new_y = max(0, min(HEIGHT - 80, new_y))

        new_col = new_x // 100
        new_row = new_y // 100

        if not is_occupied((new_row, new_col)):
            color, idx = selected_piece
            puzzle_pieces[color][idx] = (puzzle_pieces[color][idx][0], (new_row, new_col))


# Pathfinding logic to check for obstruction
def is_path_clear(start, end):
    """Check if the queen's path is clear between start and end."""
    # Horizontal movement
    if start[0] == end[0]:  # Same row
        for col in range(min(start[1], end[1]) + 1, max(start[1], end[1])):
            if is_occupied((start[0], col)):
                return False
        return True

    # Vertical movement
    if start[1] == end[1]:  # Same column
        for row in range(min(start[0], end[0]) + 1, max(start[0], end[0])):
            if is_occupied((row, start[1])):
                return False
        return True

    # Diagonal movement
    if abs(start[0] - end[0]) == abs(start[1] - end[1]):
        step_row = 1 if end[0] > start[0] else -1
        step_col = 1 if end[1] > start[1] else -1
        row, col = start[0] + step_row, start[1] + step_col
        while row != end[0] and col != end[1]:
            if is_occupied((row, col)):
                return False
            row += step_row
            col += step_col
        return True

    # Not a valid movement path
    return False


# Check if any white queen can attack a black pawn
def can_white_queen_attack():
    for white_piece, white_pos in puzzle_pieces["white"]:
        if white_piece == "white_queen":
            # Skip checking if the queen is in columns 5 or 6
            if white_pos[1] in [5, 6]:
                continue
            
            for black_piece, black_pos in puzzle_pieces["black"]:
                if black_piece == "black_pawn" and is_path_clear(white_pos, black_pos):
                    return True, white_pos, black_pos
    return False, None, None

def is_game_won():
    for white_piece, white_pos in puzzle_pieces["white"]:
        if white_pos[1] in [5, 6]:
            return False
        elif white_piece == "white_queen":
            queen_row, queen_col = white_pos

            for black_piece, black_pos in puzzle_pieces["black"]:
                if black_piece == "black_pawn":
                    pawn_row, pawn_col = black_pos

                    # Check if on the same row, column, or diagonal
                    if (
                        queen_row == pawn_row or
                        queen_col == pawn_col or
                        abs(queen_row - pawn_row) == abs(queen_col - pawn_col)
                    ):
                        return False  # Pawn is in FOV of a queen
    return True  # No pawns are in the FOV of any queen


# Main game loop
running = True
while running:

        screen.fill((0, 0, 0))
        draw_board()
        draw_pieces()

        # Draw reset button
        pygame.draw.rect(screen, RESET_BUTTON_COLOR, (525, 420, 75, 50))
        font = pygame.font.Font(None, 24)
        text_surface = font.render("Reset", True, RESET_TEXT_COLOR)
        screen.blit(text_surface, (525, 430))

        # Check if any white queen can attack a black pawn
        can_attack, queen_pos, pawn_pos = can_white_queen_attack()
        if can_attack:
            font = pygame.font.Font(None, 20)
            attack_message = font.render(
                f"White queen at {queen_pos} can kill black pawn at {pawn_pos}!", True, HIGHLIGHT_COLOR
            )
            screen.blit(attack_message, (150, 450))

        pygame.display.flip()

        if is_game_won():
            font = pygame.font.Font(None, 48)
            pygame.time.delay(750)
            if a == 1:
                win_message = font.render("Good Job!", True, (0, 255, 0))
                screen.blit(win_message, (200, 200))
                pygame.display.flip()
                pygame.time.delay(3000)  # Show the message for 3 seconds
                running = False
            elif a == 2:
                win_message = font.render("Game Won!", True, (0, 255, 0))
                screen.blit(win_message, (200, 200))
                pygame.display.flip()
                pygame.time.delay(3000)  # Show the message for 3 seconds
                running = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Handle dragging logic
            handle_dragging(event)

            # Handle reset button click
            if event.type == pygame.MOUSEBUTTONDOWN:
                if 525 <= event.pos[0] <= 600 and 420 <= event.pos[1] <= 470:
                    puzzle_pieces["white"] = [piece for piece in initial_puzzle_pieces["white"]]
                    puzzle_pieces["black"] = [piece for piece in initial_puzzle_pieces["black"]]

pygame.quit()