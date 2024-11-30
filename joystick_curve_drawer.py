import pygame
import serial
import random
import sys

pygame.init()

# Window setup
win_width, win_height = 800, 600
win = pygame.display.set_mode((win_width, win_height))
pygame.display.set_caption("Dodge the Stones")

# Colors
bg_color = (255, 255, 255)
player_color = (0, 255, 0)
stone_color = (255, 0, 0)
failure_color = (255, 0, 0)
win_color = (0, 0, 255)

# Player setup
player_radius = 20
player_x, player_y = win_width // 2, win_height - player_radius - 10

# Stone setup
stone_width, stone_height = 40, 40
stone_speed = 5
stone_count = 5
stones = [{"x": random.randint(0, win_width - stone_width), "y": -random.randint(50, 300)} for _ in range(stone_count)]

# Game variables
clock = pygame.time.Clock()
running = True
game_over = False
dodged_stones = 50  # Countdown to winning

# Serial communication setup
arduino_port = '/dev/tty.usbmodem1301'  # Replace with your Arduino port
ser = serial.Serial(arduino_port, 9600)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Handle serial data for joystick input
    try:
        data = ser.readline().decode().strip().split(',')
        if len(data) == 3:
            joy_x, joy_y, button_state = map(int, data)

            # Move player based on joystick input
            player_x += (joy_x - 512) // 100 * 5
            player_y += (joy_y - 512) // 100 * 5

            # Keep player within screen bounds
            player_x = max(player_radius, min(win_width - player_radius, player_x))
            player_y = max(player_radius, min(win_height - player_radius, player_y))
    except Exception as e:
        print(f"Error reading joystick data: {e}")
        continue

    # Move stones
    for stone in stones:
        stone["y"] += stone_speed

        # Reset stone if it goes off-screen
        if stone["y"] > win_height:
            stone["y"] = -random.randint(50, 300)
            stone["x"] = random.randint(0, win_width - stone_width)
            dodged_stones -= 1  # Successfully dodged a stone

            # Check win condition
            if dodged_stones == 0:
                running = False
                game_over = False

        # Check for collision
        if (
            player_x - player_radius < stone["x"] + stone_width
            and player_x + player_radius > stone["x"]
            and player_y - player_radius < stone["y"] + stone_height
            and player_y + player_radius > stone["y"]
        ):
            game_over = True
            running = False

    # Drawing
    win.fill(bg_color)

    if game_over:
        # Game Over screen
        font = pygame.font.Font(None, 74)
        text = font.render("Game Over!", True, failure_color)
        win.blit(text, (win_width // 2 - text.get_width() // 2, win_height // 2 - text.get_height() // 2))
    elif dodged_stones == 0:
        # Win screen
        font = pygame.font.Font(None, 74)
        text = font.render("You Win!", True, win_color)
        win.blit(text, (win_width // 2 - text.get_width() // 2, win_height // 2 - text.get_height() // 2))
    else:
        # Draw player
        pygame.draw.circle(win, player_color, (player_x, player_y), player_radius)
        # Draw stones
        for stone in stones:
            pygame.draw.rect(win, stone_color, (stone["x"], stone["y"], stone_width, stone_height))

        # Draw remaining stones to dodge
        font = pygame.font.Font(None, 36)
        text = font.render(f"Stones to dodge: {dodged_stones}", True, (0, 0, 0))
        win.blit(text, (10, 10))

    pygame.display.flip()
    clock.tick(60)

# Clean up
ser.close()
pygame.quit()
sys.exit()