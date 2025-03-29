import random
import pygame

class CephalopodAI:
    def __init__(self):
        self.board = [[None for _ in range(5)] for _ in range(5)]  # 5x5 board
        self.player_turn = True  # True if it's the player's turn, False for AI
    
    def is_valid_move(self, x, y):
        return self.board[x][y] is None  # A move is valid if the cell is empty
    
    def get_valid_moves(self):
        return [(x, y) for x in range(5) for y in range(5) if self.is_valid_move(x, y)]
    
    def get_adjacent_dice(self, x, y):
        adjacent = []
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 5 and 0 <= ny < 5 and self.board[nx][ny]:
                adjacent.append((nx, ny, self.board[nx][ny]))
        return adjacent
    
    def evaluate_move(self, x, y):
        adjacent = self.get_adjacent_dice(x, y)
        capture_value = sum(d[2] for d in adjacent if len(adjacent) >= 2 and sum(d[2] for d in adjacent) <= 6)
        board_control = len(adjacent)
        return capture_value + board_control
    
    def minimax(self, depth, maximizing):
        if depth == 0:
            return None, None, None, -1
        
        best_score = float('-inf') if maximizing else float('inf')
        best_move = None
        
        for x, y in self.get_valid_moves():
            score = self.evaluate_move(x, y)
            if (maximizing and score > best_score) or (not maximizing and score < best_score):
                best_score = score
                best_move = (x, y, sum(d[2] for d in self.get_adjacent_dice(x, y)) if self.can_capture(x, y) else 1)
        
        return best_move if best_move else random.choice(self.get_valid_moves()) + (1,), best_score
    
    def can_capture(self, x, y):
        adjacent = self.get_adjacent_dice(x, y)
        if len(adjacent) >= 2:
            sum_pips = sum(d[2] for d in adjacent)
            return sum_pips <= 6
        return False
    
    def play_turn(self):
        move, _ = self.minimax(2, True)
        x, y, value = move
        self.board[x][y] = value
        print(f"AI plays at ({x}, {y}) with value {value}")
        
        adjacent = self.get_adjacent_dice(x, y)
        sum_pips = sum(d[2] for d in adjacent)
        if sum_pips <= 6:
            for nx, ny, _ in adjacent:
                self.board[nx][ny] = None
        self.player_turn = True  # Give turn back to player

# Game rendering with pygame
def draw_board(screen, board):
    screen.fill((255, 255, 255))
    for x in range(5):
        for y in range(5):
            rect = pygame.Rect(y * 100, x * 100, 100, 100)
            pygame.draw.rect(screen, (0, 0, 0), rect, 2)
            if board[x][y]:
                font = pygame.font.Font(None, 36)
                text = font.render(str(board[x][y]), True, (0, 0, 0))
                screen.blit(text, (y * 100 + 40, x * 100 + 40))

def handle_player_move(game, x, y, value):
    if game.is_valid_move(x, y):
        game.board[x][y] = value
        game.player_turn = False  # Switch to AI turn

game = CephalopodAI()
pygame.init()
screen = pygame.display.set_mode((500, 500))
clock = pygame.time.Clock()
running = True
player_value = 1  # Default value for player's dice

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and game.player_turn:
            mx, my = pygame.mouse.get_pos()
            grid_x, grid_y = my // 100, mx // 100
            handle_player_move(game, grid_x, grid_y, player_value)
        elif event.type == pygame.KEYDOWN:
            if pygame.K_1 <= event.key <= pygame.K_6:
                player_value = event.key - pygame.K_0
    
    if not game.player_turn:
        game.play_turn()
    
    draw_board(screen, game.board)
    pygame.display.flip()
    clock.tick(30)

pygame.quit()
#TODO CAZZO
#git config --global user.name "IlTuoNome"
#git config --global user.email "tuaemail@example.com"
