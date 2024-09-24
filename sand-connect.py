import pygame
import random
import sys
import collections
import os

# Initialize Pygame
pygame.init()

# Constants
CELL_SIZE = 30  # Cell size in pixels
GRID_WIDTH = 10  # Number of cells horizontally
GRID_HEIGHT = 20  # Number of cells vertically
SIDEBAR_WIDTH = 200  # Sidebar width
WIDTH = GRID_WIDTH * CELL_SIZE + SIDEBAR_WIDTH  # Total screen width
HEIGHT = GRID_HEIGHT * CELL_SIZE  # Screen height

# Colors
BLACK = (0, 0, 0)
SIDEBAR_COLOR = (40, 40, 40)
WHITE = (255, 255, 255)
# List of vibrant colors for particles
COLORS = [
    (255, 99, 71),    # Tomato
    (135, 206, 250),  # LightSkyBlue
    (60, 179, 113),   # MediumSeaGreen
    (238, 130, 238),  # Violet
    (255, 215, 0),    # Gold
    (106, 90, 205),   # SlateBlue
    (255, 105, 180),  # HotPink
]

# Additional colors for the title text
TITLE_COLORS = [
    (255, 0, 0),      # Red
    (255, 127, 0),    # Orange
    (255, 255, 0),    # Yellow
    (0, 255, 0),      # Green
    (0, 0, 255),      # Blue
    (75, 0, 130),     # Indigo
    (148, 0, 211),    # Violet
]

# Screen setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Sand Connect')

# Clock
clock = pygame.time.Clock()

# Grid: 2D list of cells
grid = [[None for _ in range(GRID_HEIGHT)] for _ in range(GRID_WIDTH)]

# Initialize font
pygame.font.init()
# Load pixel font
pixel_font = pygame.font.SysFont('pressstart2p', 16)
title_font_size = 20  # Adjusted font size
title_font = pygame.font.SysFont('pressstart2p', title_font_size)

# Initialize mixer for sound
pygame.mixer.init()

# Load sounds
try:
    # Place your sound files in the same directory as this script
    pygame.mixer.music.load('assets/soundsbackground_music.mp3')  # Background music
    remove_sound = pygame.mixer.Sound('assets/soundsremove_sound.wav')  # Sound for removing particles
    move_sound = pygame.mixer.Sound('assets/soundsmove_sound.mp3')  # Sound for moving clusters
    pause_sound = pygame.mixer.Sound('assets/soundspause_sound.wav')  # Sound when game is paused/unpaused
except pygame.error as e:
    print(f"Error loading sound files: {e}")
    remove_sound = None
    move_sound = None
    pause_sound = None

# Start playing background music
pygame.mixer.music.set_volume(0.5)  # Set volume (0.0 to 1.0)
pygame.mixer.music.play(-1)  # Loop indefinitely

# Score
score = 0

# Game state
is_paused = False

class Particle:
    def __init__(self, x, y, color):
        self.x = x  # x position in grid
        self.y = y  # y position in grid
        self.color = color

    def update(self, grid):
        # Try to move down if possible
        if self.y + 1 < GRID_HEIGHT and grid[self.x][self.y + 1] is None:
            grid[self.x][self.y] = None  # Remove from current position
            self.y += 1  # Move down
            grid[self.x][self.y] = self  # Place in new position
        else:
            # Try to move down-left or down-right
            moves = []
            if self.x > 0 and self.y + 1 < GRID_HEIGHT and grid[self.x - 1][self.y + 1] is None:
                moves.append((-1, 1))
            if self.x + 1 < GRID_WIDTH and self.y + 1 < GRID_HEIGHT and grid[self.x + 1][self.y + 1] is None:
                moves.append((1, 1))
            if moves:
                dx, dy = random.choice(moves)
                grid[self.x][self.y] = None
                self.x += dx
                self.y += dy
                grid[self.x][self.y] = self

def start_screen():
    screen.fill(BLACK)
    title_text = title_font.render("Sand Connect", True, WHITE)
    instruction_font = pixel_font
    instruction_text = instruction_font.render("Press any key to start", True, WHITE)
    screen.blit(title_text, ((WIDTH - title_text.get_width()) // 2, HEIGHT // 3))
    screen.blit(instruction_text, ((WIDTH - instruction_text.get_width()) // 2, HEIGHT // 2))
    pygame.display.flip()
    waiting = True
    while waiting:
        clock.tick(15)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                waiting = False
                sys.exit()
            if event.type == pygame.KEYDOWN:
                waiting = False

def game_over_screen():
    screen.fill(BLACK)
    over_text = title_font.render("Game Over", True, WHITE)
    score_text = pixel_font.render(f"Final Score: {score}", True, WHITE)
    instruction_font = pixel_font
    instruction_text = instruction_font.render("Press any key to restart or ESC to quit", True, WHITE)
    screen.blit(over_text, ((WIDTH - over_text.get_width()) // 2, HEIGHT // 3))
    screen.blit(score_text, ((WIDTH - score_text.get_width()) // 2, HEIGHT // 2))
    screen.blit(instruction_text, ((WIDTH - instruction_text.get_width()) // 2, HEIGHT // 1.5))
    pygame.display.flip()
    waiting = True
    while waiting:
        clock.tick(15)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                waiting = False
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    waiting = False
                    sys.exit()
                else:
                    waiting = False

def pause_screen():
    pause_text = title_font.render("Paused", True, WHITE)
    instruction_text = pixel_font.render("Press P to resume", True, WHITE)
    screen.blit(pause_text, ((WIDTH - pause_text.get_width()) // 2, HEIGHT // 3))
    screen.blit(instruction_text, ((WIDTH - instruction_text.get_width()) // 2, HEIGHT // 2))
    pygame.display.flip()

def create_new_sand_cluster():
    global running
    cluster_size = random.randint(3, 5)  # Random cluster size
    particles = []
    # Start position in the middle of the grid
    start_x = GRID_WIDTH // 2
    start_y = 0
    for i in range(cluster_size):
        x = start_x
        y = start_y + i  # Stack particles downwards
        if x >= 0 and x < GRID_WIDTH and y >= 0 and y < GRID_HEIGHT:
            if grid[x][y] is None:
                color = random.choice(COLORS)  # Assign random color to each particle
                particle = Particle(x, y, color)
                particles.append(particle)
                grid[x][y] = particle
            else:
                # Game over
                running = False
                break
        else:
            # Out of bounds
            running = False
            break
    return particles

def can_move_cluster(cluster_particles, dx):
    for particle in cluster_particles:
        new_x = particle.x + dx
        if new_x < 0 or new_x >= GRID_WIDTH:
            return False
        if grid[new_x][particle.y] is not None and grid[new_x][particle.y] not in cluster_particles:
            return False
    return True

def move_cluster(cluster_particles, dx):
    # Remove particles from grid
    for particle in cluster_particles:
        grid[particle.x][particle.y] = None
    # Move particles
    for particle in cluster_particles:
        particle.x += dx
    # Place particles back in grid
    for particle in cluster_particles:
        grid[particle.x][particle.y] = particle
    # Play move sound
    # if move_sound:
    #     move_sound.play()

def animate_particles_removal(particles_to_remove):
    for _ in range(5):
        for cx, cy in particles_to_remove:
            pygame.draw.rect(screen, WHITE, (cx * CELL_SIZE, cy * CELL_SIZE, CELL_SIZE, CELL_SIZE))
        pygame.display.flip()
        pygame.time.delay(50)
        for cx, cy in particles_to_remove:
            particle = grid[cx][cy]
            if particle is not None:
                pygame.draw.rect(screen, particle.color, (cx * CELL_SIZE, cy * CELL_SIZE, CELL_SIZE, CELL_SIZE))
        pygame.display.flip()
        pygame.time.delay(50)

def remove_connected_particles():
    global score
    visited = [[False for _ in range(GRID_HEIGHT)] for _ in range(GRID_WIDTH)]
    particles_to_remove = []
    for x in range(GRID_WIDTH):
        for y in range(GRID_HEIGHT):
            if grid[x][y] is not None and not visited[x][y]:
                connected = []
                queue = collections.deque()
                queue.append((x, y))
                visited[x][y] = True
                color = grid[x][y].color
                while queue:
                    cx, cy = queue.popleft()
                    connected.append((cx, cy))
                    # Check adjacent cells
                    for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                        nx, ny = cx + dx, cy + dy
                        if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT:
                            if not visited[nx][ny] and grid[nx][ny] is not None:
                                if grid[nx][ny].color == color:
                                    visited[nx][ny] = True
                                    queue.append((nx, ny))
                # Remove if connected particles are 4 or more
                if len(connected) >= 4:
                    particles_to_remove.extend(connected)
    if particles_to_remove:
        score += len(particles_to_remove) * 10  # Award points
        # Play remove sound
        if remove_sound:
            remove_sound.play()
        # Animate removal
        animate_particles_removal(particles_to_remove)
        for cx, cy in particles_to_remove:
            grid[cx][cy] = None

def update_particles():
    # Update particles from bottom to top
    for y in range(GRID_HEIGHT - 1, -1, -1):
        for x in range(GRID_WIDTH):
            particle = grid[x][y]
            if particle is not None:
                particle.update(grid)

def draw_sidebar():
    # Draw sidebar background
    pygame.draw.rect(screen, SIDEBAR_COLOR, (GRID_WIDTH * CELL_SIZE, 0, SIDEBAR_WIDTH, HEIGHT))
    
    # Draw pixel art frame for the score
    frame_color = (255, 223, 0)
    frame_rect = pygame.Rect(GRID_WIDTH * CELL_SIZE + 10, 150, SIDEBAR_WIDTH - 20, 100)
    pygame.draw.rect(screen, frame_color, frame_rect, 4)
    
    # Display score with pixel font
    score_text = pixel_font.render("SCORE", True, WHITE)
    score_value = pixel_font.render(f"{score}", True, WHITE)
    
    # Center the score text within the rectangle
    score_text_rect = score_text.get_rect(center=(frame_rect.centerx, frame_rect.centery - 20))
    score_value_rect = score_value.get_rect(center=(frame_rect.centerx, frame_rect.centery + 20))
    screen.blit(score_text, score_text_rect)
    screen.blit(score_value, score_value_rect)
    
    # Display game title with colorful colors
    title_str = "Sand Connect"
    title_x = GRID_WIDTH * CELL_SIZE + SIDEBAR_WIDTH // 2
    title_y = 50
    # Reduce font size if necessary to fit the sidebar
    global title_font_size, title_font
    title_font_size = 20
    title_font = pygame.font.SysFont('pressstart2p', title_font_size)
    # Check if the text fits, reduce font size if needed
    title_render = title_font.render(title_str, True, WHITE)
    while title_render.get_width() > SIDEBAR_WIDTH - 20 and title_font_size > 10:
        title_font_size -= 2
        title_font = pygame.font.SysFont('pressstart2p', title_font_size)
        title_render = title_font.render(title_str, True, WHITE)
    # Render each character with a different color
    title_x_pos = GRID_WIDTH * CELL_SIZE + (SIDEBAR_WIDTH - title_render.get_width()) // 2
    for idx, char in enumerate(title_str):
        color = TITLE_COLORS[idx % len(TITLE_COLORS)]
        char_render = title_font.render(char, True, color)
        screen.blit(char_render, (title_x_pos, title_y))
        title_x_pos += char_render.get_width()

def render():
    # Draw background gradient
    for i in range(HEIGHT):
        color = (i * 255 // HEIGHT, 0, 128)
        pygame.draw.line(screen, color, (0, i), (GRID_WIDTH * CELL_SIZE, i))
    # Draw particles
    for x in range(GRID_WIDTH):
        for y in range(GRID_HEIGHT):
            particle = grid[x][y]
            if particle is not None:
                pygame.draw.rect(screen, particle.color, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
                # Add a border around the particle
                pygame.draw.rect(screen, WHITE, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)
    # Draw sidebar
    draw_sidebar()
    pygame.display.flip()

def main():
    global running, current_cluster, score, grid, is_paused
    start_screen()
    while True:
        running = True
        is_paused = False
        score = 0
        grid = [[None for _ in range(GRID_HEIGHT)] for _ in range(GRID_WIDTH)]
        current_cluster = create_new_sand_cluster()
        fall_time = 0
        fall_speed = 1.0  # Adjusted fall speed for clusters
        particle_fall_time = 0
        particle_fall_speed = 0.2  # Adjusted fall speed for particles
        while running:
            dt = clock.tick(60) / 1000  # Delta time in seconds
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        is_paused = not is_paused
                        # Play pause sound
                        if pause_sound:
                            pause_sound.play()
                        if is_paused:
                            # Pause music
                            pygame.mixer.music.pause()
                        else:
                            # Unpause music
                            pygame.mixer.music.unpause()
                    if not is_paused:
                        if event.key == pygame.K_LEFT:
                            if can_move_cluster(current_cluster, dx=-1):
                                move_cluster(current_cluster, dx=-1)
                        elif event.key == pygame.K_RIGHT:
                            if can_move_cluster(current_cluster, dx=1):
                                move_cluster(current_cluster, dx=1)
                        elif event.key == pygame.K_DOWN:
                            fall_time = fall_speed  # Accelerate falling
            if not is_paused:
                fall_time += dt
                particle_fall_time += dt
                # Move current cluster down based on fall speed
                if fall_time > fall_speed:
                    fall_time = 0
                    # Try to move down
                    can_move_down = True
                    for particle in current_cluster:
                        new_y = particle.y + 1
                        if new_y >= GRID_HEIGHT or (grid[particle.x][new_y] is not None and grid[particle.x][new_y] not in current_cluster):
                            can_move_down = False
                            break
                    if can_move_down:
                        # Remove particles from grid
                        for particle in current_cluster:
                            grid[particle.x][particle.y] = None
                        # Move particles
                        for particle in current_cluster:
                            particle.y += 1
                        # Place particles back in grid
                        for particle in current_cluster:
                            grid[particle.x][particle.y] = particle
                    else:
                        # Cluster has settled
                        current_cluster = None
                        # Remove connected particles
                        remove_connected_particles()
                        # Create new cluster
                        current_cluster = create_new_sand_cluster()
                        if not running:
                            break
                # Update particles (simulate sand physics) based on particle fall speed
                if particle_fall_time > particle_fall_speed:
                    particle_fall_time = 0
                    update_particles()
                # Render
                render()
            else:
                # If paused, display pause screen
                pause_screen()
        # Game Over
        game_over_screen()

if __name__ == '__main__':
    main()