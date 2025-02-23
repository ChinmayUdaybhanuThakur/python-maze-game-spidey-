import pygame
from random import choice, randrange
import heapq

## Constants for screen dimensions and tile size
RES = WIDTH, HEIGHT = 1202, 902
TILE = 100
cols, rows = WIDTH // TILE, HEIGHT // TILE

# Define a class to represent cells in the maze
class Cell:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.walls = {"top": True, "right": True, "bottom": True, "left": True}
        self.visited = False
        self.thickness = 4

    # Draw the cell's walls
    def draw(self, sc):
        x, y = self.x * TILE, self.y * TILE
        if self.walls["top"]:
            pygame.draw.line(sc, pygame.Color("darkorange"), (x, y), (x + TILE, y), self.thickness)
        if self.walls["right"]:
            pygame.draw.line(sc, pygame.Color("darkorange"), (x + TILE, y), (x + TILE, y + TILE), self.thickness)
        if self.walls["bottom"]:
            pygame.draw.line(sc, pygame.Color("darkorange"), (x + TILE, y + TILE), (x, y + TILE), self.thickness)
        if self.walls["left"]:
            pygame.draw.line(sc, pygame.Color("darkorange"), (x, y + TILE), (x, y), self.thickness)

    # Get the rectangles representing each wall of the cell
    def get_rects(self):
        rects = []
        x, y = self.x * TILE, self.y * TILE
        if self.walls["top"]:
            rects.append(pygame.Rect((x, y), (TILE, self.thickness)))
        if self.walls["right"]:
            rects.append(pygame.Rect((x + TILE, y), (self.thickness, TILE)))
        if self.walls["bottom"]:
            rects.append(pygame.Rect((x, y + TILE), (TILE, self.thickness)))
        if self.walls["left"]:
            rects.append(pygame.Rect((x, y), (self.thickness, TILE)))
        return rects

    # Check if a neighboring cell exists
    def check_cell(self, x, y, grid_cells):
        find_index = lambda x, y: x + y * cols
        if x < 0 or x > cols - 1 or y < 0 or y > rows - 1:
            return False
        return grid_cells[find_index(x, y)]

    # Get neighboring cells that have not been visited
    def check_neighbors(self, grid_cells):
        neighbors = []
        top = self.check_cell(self.x, self.y - 1, grid_cells)
        right = self.check_cell(self.x + 1, self.y, grid_cells)
        bottom = self.check_cell(self.x, self.y + 1, grid_cells)
        left = self.check_cell(self.x - 1, self.y, grid_cells)
        if top and not top.visited:
            neighbors.append(top)
        if right and not right.visited:
            neighbors.append(right)
        if bottom and not bottom.visited:
            neighbors.append(bottom)
        if left and not left.visited:
            neighbors.append(left)
        return choice(neighbors) if neighbors else False

    def get_neighbors(self, grid_cells):
        neighbors = []
        if not self.walls["top"]:
            top = self.check_cell(self.x, self.y - 1, grid_cells)
            if top: neighbors.append(top)
        if not self.walls["right"]:
            right = self.check_cell(self.x + 1, self.y, grid_cells)
            if right: neighbors.append(right)
        if not self.walls["bottom"]:
            bottom = self.check_cell(self.x, self.y + 1, grid_cells)
            if bottom: neighbors.append(bottom)
        if not self.walls["left"]:
            left = self.check_cell(self.x - 1, self.y, grid_cells)
            if left: neighbors.append(left)
        return neighbors

## Function to remove walls between two adjacent cells
def remove_walls(current, next):
    dx = current.x - next.x
    if dx == 1:
        current.walls["left"] = False
        next.walls["right"] = False
    elif dx == -1:
        current.walls["right"] = False
        next.walls["left"] = False
    dy = current.y - next.y
    if dy == 1:
        current.walls["top"] = False
        next.walls["bottom"] = False
    elif dy == -1:
        current.walls["bottom"] = False
        next.walls["top"] = False


# Function to generate the maze
def generate_maze():
    grid_cells = [Cell(col, row) for row in range(rows) for col in range(cols)]
    current_cell = grid_cells[0]
    array = []
    break_count = 1

    # Standard DFS generation
    while break_count != len(grid_cells):
        current_cell.visited = True
        next_cell = current_cell.check_neighbors(grid_cells)
        if next_cell:
            next_cell.visited = True
            break_count += 1
            array.append(current_cell)
            remove_walls(current_cell, next_cell)
            current_cell = next_cell
        elif array:
            current_cell = array.pop()

    # Add random connections for more complexity
    for cell in grid_cells:
        if randrange(100) < 25:  # 25% chance to add extra path
            neighbors = [
                (cell.x, cell.y-1, "top"),
                (cell.x+1, cell.y, "right"),
                (cell.x, cell.y+1, "bottom"),
                (cell.x-1, cell.y, "left")
            ]
            for nx, ny, wall in neighbors:
                neighbor = cell.check_cell(nx, ny, grid_cells)
                if neighbor and cell.walls[wall]:
                    remove_walls(cell, neighbor)
                    break

    return grid_cells

def heuristic(a, b):
    return abs(a.x - b.x) + abs(a.y - b.y)

def a_star(start, end, grid_cells):
    # Map cells to their (x, y) coordinates for easy lookup
    cell_dict = {(cell.x, cell.y): cell for cell in grid_cells}
    start_cell = cell_dict[(start.x, start.y)]
    end_cell = cell_dict[(end.x, end.y)]

    # Initialize g_score and f_score dictionaries
    g_score = {cell: float('inf') for cell in grid_cells}
    g_score[start_cell] = 0
    f_score = {cell: float('inf') for cell in grid_cells}
    f_score[start_cell] = heuristic(start_cell, end_cell)

    # Initialize the priority queue
    open_heap = []
    start_index = start_cell.y * cols + start_cell.x
    heapq.heappush(open_heap, (f_score[start_cell], start_index, start_cell))

    # Track the path
    came_from = {}

    while open_heap:
        # Extract the cell with the lowest f_score
        current = heapq.heappop(open_heap)[2]  # Cell is the third element
        if current == end_cell:
            # Reconstruct and return the path
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start_cell)
            path.reverse()
            return path

        # Explore neighbors
        for neighbor in current.get_neighbors(grid_cells):
            tentative_g = g_score[current] + 1  # Assuming unit distance between cells
            if tentative_g < g_score[neighbor]:
                # Update path and scores
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score[neighbor] = tentative_g + heuristic(neighbor, end_cell)
                neighbor_index = neighbor.y * cols + neighbor.x
                heapq.heappush(open_heap, (f_score[neighbor], neighbor_index, neighbor))

    # No path found
    return []

## Class to represent food in the game
class Food:
    def __init__(self):
        ## Load the food image
        self.img = pygame.image.load("img/food.png").convert_alpha()
        self.img = pygame.transform.scale(self.img, (TILE - 10, TILE - 10))
        self.rect = self.img.get_rect()
        self.set_pos()

    ## Set the position of the food randomly
    def set_pos(self):
        self.rect.topleft = randrange(cols) * TILE + 5, randrange(rows) * TILE + 5

    ## Draw the food on the screen
    def draw(self):
        game_surface.blit(self.img, self.rect)

## The rest of your code will go here...

## Check if the player collides with walls
def is_collide(x, y):
    tmp_rect = player_rect.move(x, y)
    if tmp_rect.collidelist(walls_collide_list) == -1:
        return False
    return True

## Check if the player has eaten any food
def eat_food():
    for food in food_list:
        if player_rect.collidepoint(food.rect.center):
            food.set_pos()
            return True
    return False


def is_game_over():
    global time, score, record, FPS, maze, a_star_path, walls_collide_list
    if time < 0:
        # Regenerate maze and path
        maze = generate_maze()
        start = maze[0]
        end = maze[-1]
        a_star_path = a_star(start, end, maze)
        walls_collide_list = sum([cell.get_rects() for cell in maze], [])
        
        # Reset game state
        pygame.time.wait(700)
        player_rect.center = TILE // 2, TILE // 2
        [food.set_pos() for food in food_list]
        set_record(record, score)
        record = get_record()
        time, score, FPS = 60, 0, 60

## Function to get the current record from a file
def get_record():
    try:
        with open("record") as f:
            return f.readline()
    except FileNotFoundError:
        with open("record", "w") as f:
            f.write("0")
            return "0"

## Function to set and update the record in a file
def set_record(record, score):
    rec = max(int(record), score)
    with open("record", "w") as f:
        f.write(str(rec))

## Initialize Pygame and set up the game window
FPS = 60
pygame.init()
game_surface = pygame.Surface(RES)
surface = pygame.display.set_mode((WIDTH + 300, HEIGHT))
clock = pygame.time.Clock()

## Load background images
bg_game = pygame.image.load("img/bg_1.webp").convert()
bg_game = pygame.transform.scale(bg_game, RES)  # Resize to match game resolution
bg = pygame.image.load("img/stats.jpg").convert()

## Generate the maze and calculate path
maze = generate_maze()
start = maze[0]            # Entrance (top-left)
end = maze[-1]             # Exit (bottom-right)
a_star_path = a_star(start, end, maze)  # Calculate initial path

## Player settings
player_speed = 5
player_img = pygame.image.load("img/sprite.jpg").convert_alpha()
player_img = pygame.transform.scale(
    player_img, (TILE - 2 * maze[0].thickness, TILE - 2 * maze[0].thickness)
)
player_rect = player_img.get_rect()
player_rect.center = TILE // 2, TILE // 2
directions = {
    "a": (-player_speed, 0),
    "d": (player_speed, 0),
    "w": (0, -player_speed),
    "s": (0, player_speed),
}
keys = {"a": pygame.K_LEFT, "d": pygame.K_RIGHT, "w": pygame.K_UP, "s": pygame.K_DOWN}
direction = (0, 0)

## Food settings
food_list = [Food() for i in range(3)]

## Create a list of rectangles representing walls for collision detection
walls_collide_list = sum([cell.get_rects() for cell in maze], [])

## Timer, score, and record
pygame.time.set_timer(pygame.USEREVENT, 1000)
time = 60
score = 0
record = get_record()

## Fonts
font = pygame.font.SysFont("Impact", 150)
text_font = pygame.font.SysFont("Impact", 80)

## The rest of your code will go here...

## Main game loop
while True:
    ## Blit background images
    surface.blit(bg, (WIDTH, 0))
    surface.blit(game_surface, (0, 0))
    game_surface.blit(bg_game, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        if event.type == pygame.USEREVENT:
            time -= 1

    ## Handle player controls and movement
    pressed_key = pygame.key.get_pressed()
    for key, key_value in keys.items():
        if pressed_key[key_value] and not is_collide(*directions[key]):
            direction = directions[key]
            break
    if not is_collide(*direction):
        player_rect.move_ip(direction)

    ## Draw the maze
    [cell.draw(game_surface) for cell in maze]

    ## Gameplay: Check if the player has eaten food and if the game is over
    if eat_food():
        FPS += 10
        score += 1
    is_game_over()

    ## Draw the player
    game_surface.blit(player_img, player_rect)

    ## Draw food items
    [food.draw() for food in food_list]

    ## Draw A* path
    for cell in a_star_path:
        x = cell.x * TILE + TILE//2
        y = cell.y * TILE + TILE//2
        pygame.draw.circle(game_surface, (0, 255, 0), (x, y), 5)

    ## Draw exit marker
    exit_rect = pygame.Rect(end.x * TILE + 10, end.y * TILE + 10, TILE - 20, TILE - 20)
    pygame.draw.rect(game_surface, (255, 0, 0), exit_rect)

    ## Draw game statistics
    surface.blit(
        text_font.render("TIME", True, pygame.Color("red")), (WIDTH + 70, 30)
    )
    surface.blit(font.render(f"{time}", True, pygame.Color("red")), (WIDTH + 70, 130))
    surface.blit(
        text_font.render("score:", True, pygame.Color("white")),
        (WIDTH + 50, 350),
    )
    surface.blit(
        font.render(f"{score}", True, pygame.Color("white")), (WIDTH + 70, 430)
    )
    surface.blit(
        text_font.render("record:", True, pygame.Color("magenta")),
        (WIDTH + 30, 620),
    )
    surface.blit(
        font.render(f"{record}", True, pygame.Color("magenta")), (WIDTH + 70, 700)
    )

    pygame.display.flip()
    clock.tick(FPS)