# Project/Tutorial       - Numera Quest: Kingdom of Math Runes
# Author                 - https://www.hackster.io/maheshyadav216
# Hardware               - Arduino UNO Q    
# Software               - Arduino App Lab
# GitHub Repo of Project - https://github.com/maheshyadav216/Project-Numera-Quest-Kingdom-of-Math-Runes
# Code last Modified on  - 14/09/2026
# Code/Content license   - (CC BY-NC-SA 4.0) https://creativecommons.org/licenses/by-nc-sa/4.0/
#============================================================================//
# This is PyGame.py 
import pygame
import socket
import json
import time
import threading
import os


# ============================================================
# NUMERA QUEST - STAGE 3
# Audio Integration - Quest Start
#
# Controller:
#   Axis 0  -> Left Stick X
#   Axis 1  -> Left Stick Y
#   Button 0  -> Y
#   Button 1  -> B
#   Button 2  -> A
#   Button 3  -> X
#   Button 4  -> L1
#   Button 5  -> R1
#   Button 6  -> L2
#   Button 7  -> R2
#   Button 8  -> SELECT
#   Button 9  -> START
#   Button 10 -> Left Stick Press
#   Button 11 -> Right Stick Press
#   Button 12 -> HOME
#
#   Hat 0 -> D-Pad
# ============================================================


# ============================================================
# CONFIGURATION
# ============================================================

SCREEN_WIDTH = 960
SCREEN_HEIGHT = 540

FPS = 60

PLAYER_SIZE = 52
PLAYER_SPEED = 5

DEADZONE = 0.25

UDP_IP = "0.0.0.0"
UDP_PORT = 5005

# How long we wait for App Lab handshake.
# The game itself does NOT depend on this.
HANDSHAKE_TIMEOUT = 1.5

# Challenge interaction range
INTERACTION_DISTANCE = 60


# ============================================================
# COLORS
# ============================================================

WHITE = (255, 255, 255)
BLACK = (10, 12, 18)

GREEN = (50, 220, 100)
DARK_GREEN = (20, 110, 55)

BLUE = (60, 130, 240)
DARK_BLUE = (25, 50, 100)

PURPLE = (100, 70, 160)
DARK_PURPLE = (35, 20, 60)

YELLOW = (245, 210, 70)
RED = (230, 70, 70)

GRAY = (150, 155, 165)
DARK_GRAY = (45, 48, 58)

CYAN = (60, 220, 230)


# ============================================================
# UDP SETUP
# ============================================================

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Allow quick restart
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

try:
    sock.bind((UDP_IP, UDP_PORT))
except OSError as e:
    print(f"WARNING: UDP port {UDP_PORT} unavailable: {e}")
    print("Game will continue without App Lab communication.")
    sock = None


target_ip = None
target_port = None


# ============================================================
# PYGAME INITIALIZATION
# ============================================================

pygame.init()
pygame.joystick.init()

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()

pygame.display.set_caption("Numera Quest - Stage 2")

clock = pygame.time.Clock()


# ============================================================
# FONTS
# ============================================================

font_title = pygame.font.Font(None, 48)
font_large = pygame.font.Font(None, 46)
font_medium = pygame.font.Font(None, 30)
font_small = pygame.font.Font(None, 23)


# ============================================================
# CONTROLLER DETECTION
# ============================================================

joystick = None

if pygame.joystick.get_count() > 0:

    joystick = pygame.joystick.Joystick(0)
    joystick.init()

    print("============================================================")
    print("NUMERA QUEST - STAGE 3")
    print("============================================================")
    print(f"Controller detected: {joystick.get_name()}")
    print(f"Axes:    {joystick.get_numaxes()}")
    print(f"Buttons: {joystick.get_numbuttons()}")
    print(f"Hats:    {joystick.get_numhats()}")
    print("============================================================")

else:

    print("============================================================")
    print("NUMERA QUEST - STAGE 3")
    print("============================================================")
    print("WARNING: No controller detected.")
    print("Game will still start.")
    print("============================================================")


# ============================================================
# GAME STATE
# ============================================================

player_x = 85
player_y = 125

paused = False

interaction_message = ""
interaction_timer = 0

running = True

seq = 0

last_dpad = (0, 0)

# Challenge state
challenge_active = False
challenge_type = "FINGER_COUNT"

# Level management
current_level = 1

LEVEL_CHALLENGES = {
    1: {
        "question": "9 - 5",
        "answer": 4
    },
    2: {
        "question": "2 + 3",
        "answer": 5
    },
    3: {
        "question": "8 - 7",
        "answer": 1
    },
    3: {
        "question": "8 - 7",
        "answer": 1
    }
}

challenge_question = LEVEL_CHALLENGES[current_level]["question"]
challenge_correct_answer = LEVEL_CHALLENGES[current_level]["answer"]
challenge_selected_answer = 0
challenge_message = ""
challenge_message_timer = 0
challenge_success = False
answer_submitted = False
challenge_attempts = 0

# ============================================================
# CAMERA DETECTION RECEIVER
# ============================================================

latest_detection = {
    "label": "unknown",
    "confidence": 0.0
}

FINGER_VALUES = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5
}

camera_candidate = "unknown"
camera_candidate_count = 0
camera_stable_answer = 0
last_announced_answer = 0
camera_waiting_for_fresh_hand = False

CAMERA_STABLE_COUNT = 6

# Prevent continuous obstacle contact from spamming the collision SFX.
COLLISION_SOUND_COOLDOWN = 0.35
last_collision_sound_time = 0.0

def play_collision_sound():
    global last_collision_sound_time

    now = time.monotonic()
    if now - last_collision_sound_time >= COLLISION_SOUND_COOLDOWN:
        send_audio_command("collision_error")
        last_collision_sound_time = now

def camera_receiver():
    global latest_detection
    global camera_candidate
    global camera_candidate_count
    global camera_stable_answer
    global last_announced_answer
    global camera_waiting_for_fresh_hand

    while True:
        try:
            data, _ = sock.recvfrom(1024)
            message = json.loads(data.decode())

            if message.get("type") == "finger":

                label = message.get("label", "unknown")
                confidence = message.get("confidence", 0.0)

                latest_detection = {
                    "label": label,
                    "confidence": confidence
                }

                if camera_waiting_for_fresh_hand:

                    if label == "unknown":
                        camera_waiting_for_fresh_hand = False
                        camera_candidate = "unknown"
                        camera_candidate_count = 0
                        camera_stable_answer = 0
                        last_announced_answer = 0

                    continue

                if label == camera_candidate:
                    camera_candidate_count += 1
                else:
                    camera_candidate = label
                    camera_candidate_count = 1

                if camera_candidate_count >= CAMERA_STABLE_COUNT:

                    if label in FINGER_VALUES:

                        camera_stable_answer = FINGER_VALUES[label]

                        if challenge_active and camera_stable_answer != last_announced_answer:

                            send_audio_command(
                                f"answer_{camera_stable_answer}"
                            )

                            last_announced_answer = camera_stable_answer

                            print(
                                f"AUDIO: Announcing answer_{camera_stable_answer}"
                            )

                    else:

                        camera_stable_answer = 0

                print(
                    f"CAMERA RECEIVED: {label} = {confidence:.3f} "
                    f"| stable={camera_stable_answer}"
                )

        except Exception:
            pass



# Persistent state for the world QUEST.
# Once the math challenge is solved, this QUEST stays cleared.
quest_completed = False
final_victory = False

# Used to prevent repeated button actions while held
previous_buttons = [0] * 13


# ============================================================
# APP LAB HANDSHAKE
# ============================================================

def try_app_lab_handshake():
    """
    Try to find App Lab without blocking the game.

    App Lab is optional for Phase 1.
    """

    global target_ip
    global target_port

    if sock is None:
        return

    print("Trying to find App Lab...")

    try:

        # Temporary timeout
        sock.settimeout(HANDSHAKE_TIMEOUT)

        start_time = time.time()

        while time.time() - start_time < HANDSHAKE_TIMEOUT:

            try:

                data, addr = sock.recvfrom(1024)

                if data.decode(errors="ignore") == "PING":

                    target_ip = addr[0]
                    target_port = addr[1]

                    sock.sendto(b"ACK", addr)

                    print(
                        f"App Lab connected: "
                        f"{target_ip}:{target_port}"
                    )

                    break

            except socket.timeout:
                break

    except Exception as e:

        print(f"App Lab handshake skipped: {e}")

    finally:

        # Return to non-blocking mode
        try:
            sock.setblocking(False)
        except Exception:
            pass

    if target_ip is None:

        print("App Lab not found.")
        print("Game will run independently.")

    print("============================================================")


# ============================================================
# SEND CONTROLLER SNAPSHOT TO APP LAB
# ============================================================

def send_snapshot(x_value, y_value, a_value, b_value):

    global seq

    if sock is None:
        return

    if target_ip is None or target_port is None:
        return

    state = {
        "seq": seq,
        "x": round(x_value, 2),
        "y": round(y_value, 2),
        "a": int(a_value),
        "b": int(b_value)
    }

    try:

        sock.sendto(
            json.dumps(state).encode(),
            (target_ip, target_port)
        )

    except Exception:
        pass

    seq += 1


# ============================================================
# AUDIO COMMANDS
# ============================================================

def send_audio_command(sound_name):
    if sock is None:
        return

    if target_ip is None or target_port is None:
        return

    message = {
        "type": "sound",
        "sound": sound_name
    }

    try:
        sock.sendto(
            json.dumps(message).encode(),
            (target_ip, target_port)
        )
        print(f"AUDIO COMMAND: {sound_name}")
    except Exception:
        pass


# ============================================================
# DRAW HELPERS
# ============================================================

def draw_text(text, font, color, x, y):

    surface = font.render(text, True, color)
    screen.blit(surface, (x, y))


def draw_centered_text(text, font, color, y, center_x=None):

    surface = font.render(text, True, color)

    if center_x is None:
        x = (SCREEN_WIDTH - surface.get_width()) // 2
    else:
        x = int(center_x - surface.get_width() / 2)

    screen.blit(surface, (x, y))


# ============================================================
# QUEST ZONE
# ============================================================

def get_challenge_rect():
    # Keep QUEST inside the gameplay region, just before the
    # instruction panel. Size is deliberately large for fullscreen.
    playfield_right = SCREEN_WIDTH - 315

    if current_level == 2:
        return pygame.Rect(
            STAGE2_QUEST_X - 65,
            STAGE2_QUEST_Y - 65,
            130,
            130
        )

    if current_level == 3:
        return pygame.Rect(
            STAGE3_QUEST_X - 65,
            STAGE3_QUEST_Y - 65,
            130,
            130
        )

    return pygame.Rect(
        playfield_right - 145,
        SCREEN_HEIGHT // 2 - 70,
        130,
        130
    )


# ============================================================
# LEVEL 1 OBSTACLES
# ============================================================

LEVEL1_OBSTACLES = [
    # Upper-left barrier
    pygame.Rect(
        int(SCREEN_WIDTH * 0.20),
        int(SCREEN_HEIGHT * 0.30),
        int(SCREEN_WIDTH * 0.20),
        42
    ),

    # Left vertical barrier
    pygame.Rect(
        int(SCREEN_WIDTH * 0.20),
        int(SCREEN_HEIGHT * 0.52),
        42,
        int(SCREEN_HEIGHT * 0.25)
    ),

    # Central barrier
    pygame.Rect(
        int(SCREEN_WIDTH * 0.45),
        int(SCREEN_HEIGHT * 0.39),
        int(SCREEN_WIDTH * 0.19),
        42
    ),

    # Lower central barrier
    pygame.Rect(
        int(SCREEN_WIDTH * 0.51),
        int(SCREEN_HEIGHT * 0.65),
        42,
        int(SCREEN_HEIGHT * 0.19)
    ),

    # Final gate before QUEST
    pygame.Rect(
        int(SCREEN_WIDTH * 0.70),
        int(SCREEN_HEIGHT * 0.28),
        42,
        int(SCREEN_HEIGHT * 0.24)
    ),
]

# ============================================================
# LEVEL 1 FOREST DECORATIONS
# ============================================================

# Trees are positioned relative to the actual gameplay area,
# so none of them can spill into the HOW TO PLAY panel.
PLAYFIELD_LEFT = 25
PLAYFIELD_RIGHT = SCREEN_WIDTH - 315
PLAYFIELD_TOP = 90
PLAYFIELD_BOTTOM = SCREEN_HEIGHT - 45
PLAYFIELD_WIDTH = PLAYFIELD_RIGHT - 25
PLAYFIELD_HEIGHT = PLAYFIELD_BOTTOM - PLAYFIELD_TOP

LEVEL1_TREES = [
    (25 + int(PLAYFIELD_WIDTH * 0.16), PLAYFIELD_TOP + int(PLAYFIELD_HEIGHT * 0.18)),
    (25 + int(PLAYFIELD_WIDTH * 0.17), PLAYFIELD_TOP + int(PLAYFIELD_HEIGHT * 0.43)),
    (25 + int(PLAYFIELD_WIDTH * 0.12), PLAYFIELD_TOP + int(PLAYFIELD_HEIGHT * 0.76)),
    (25 + int(PLAYFIELD_WIDTH * 0.32), PLAYFIELD_TOP + int(PLAYFIELD_HEIGHT * 0.12)),
    (25 + int(PLAYFIELD_WIDTH * 0.42), PLAYFIELD_TOP + int(PLAYFIELD_HEIGHT * 0.78)),
    (25 + int(PLAYFIELD_WIDTH * 0.61), PLAYFIELD_TOP + int(PLAYFIELD_HEIGHT * 0.14)),
    (25 + int(PLAYFIELD_WIDTH * 0.70), PLAYFIELD_TOP + int(PLAYFIELD_HEIGHT * 0.80)),
    (25 + int(PLAYFIELD_WIDTH * 0.76), PLAYFIELD_TOP + int(PLAYFIELD_HEIGHT * 0.66)),
]

# ============================================================
# STAGE 2 - CRYSTAL CAVERNS
# ============================================================

STAGE3_START_X = PLAYFIELD_RIGHT - 105
STAGE3_START_Y = PLAYFIELD_TOP + 105

# Stage 3 QUEST is deliberately placed at the bottom-left,
# opposite the player START position.
STAGE3_QUEST_X = PLAYFIELD_LEFT + 125
STAGE3_QUEST_Y = PLAYFIELD_BOTTOM - 115

# Number Temple: pillars and stone walls create a route
# that is visually and spatially different from Levels 1 and 2.
STAGE3_OBSTACLES = [
    # Upper-left horizontal temple wall
    pygame.Rect(
        int(SCREEN_WIDTH * 0.20),
        int(SCREEN_HEIGHT * 0.25),
        int(SCREEN_WIDTH * 0.18),
        42
    ),

    # Upper-middle pillar
    pygame.Rect(
        int(SCREEN_WIDTH * 0.43),
        int(SCREEN_HEIGHT * 0.19),
        46,
        int(SCREEN_HEIGHT * 0.19)
    ),

    # Centre horizontal wall
    pygame.Rect(
        int(SCREEN_WIDTH * 0.53),
        int(SCREEN_HEIGHT * 0.43),
        int(SCREEN_WIDTH * 0.18),
        42
    ),

    # Centre-left vertical pillar
    pygame.Rect(
        int(SCREEN_WIDTH * 0.30),
        int(SCREEN_HEIGHT * 0.48),
        46,
        int(SCREEN_HEIGHT * 0.18)
    ),

    # Lower-middle horizontal wall
    pygame.Rect(
        int(SCREEN_WIDTH * 0.42),
        int(SCREEN_HEIGHT * 0.70),
        int(SCREEN_WIDTH * 0.18),
        42
    ),

    # Right-middle vertical pillar
    pygame.Rect(
        int(SCREEN_WIDTH * 0.72),
        int(SCREEN_HEIGHT * 0.53),
        46,
        int(SCREEN_HEIGHT * 0.20)
    ),

    # Lower-right short wall
    pygame.Rect(
        int(SCREEN_WIDTH * 0.70),
        int(SCREEN_HEIGHT * 0.78),
        int(SCREEN_WIDTH * 0.12),
        42
    ),
]

STAGE3_PILLARS = [
    (0.17, 0.38, 30),
    (0.39, 0.78, 28),
    (0.57, 0.27, 30),
    (0.83, 0.40, 27),
    (0.79, 0.72, 30),
    (0.26, 0.79, 25),
]

STAGE2_START_X = 105
STAGE2_START_Y = SCREEN_HEIGHT - 155

# Stage 2 QUEST is deliberately moved to the upper-right area,
# instead of using the Stage 1 mid-right position.
STAGE2_QUEST_X = PLAYFIELD_RIGHT - 125
STAGE2_QUEST_Y = int(SCREEN_HEIGHT * 0.35)

# A completely different maze-like arrangement from Level 1.
STAGE2_OBSTACLES = [
    # Upper horizontal wall
    pygame.Rect(
        int(SCREEN_WIDTH * 0.31),
        int(SCREEN_HEIGHT * 0.22),
        int(SCREEN_WIDTH * 0.18),
        42
    ),

    # Left-middle vertical wall
    pygame.Rect(
        int(SCREEN_WIDTH * 0.22),
        int(SCREEN_HEIGHT * 0.43),
        42,
        int(SCREEN_HEIGHT * 0.22)
    ),

    # Centre L-shaped barrier
    pygame.Rect(
        int(SCREEN_WIDTH * 0.48),
        int(SCREEN_HEIGHT * 0.38),
        42,
        int(SCREEN_HEIGHT * 0.17)
    ),
    pygame.Rect(
        int(SCREEN_WIDTH * 0.48),
        int(SCREEN_HEIGHT * 0.51),
        int(SCREEN_WIDTH * 0.15),
        42
    ),

    # Lower-left horizontal wall
    pygame.Rect(
        int(SCREEN_WIDTH * 0.29),
        int(SCREEN_HEIGHT * 0.70),
        int(SCREEN_WIDTH * 0.17),
        42
    ),

    # Lower-middle vertical wall
    pygame.Rect(
        int(SCREEN_WIDTH * 0.61),
        int(SCREEN_HEIGHT * 0.67),
        42,
        int(SCREEN_HEIGHT * 0.17)
    ),

    # IMPORTANT: no obstacle is placed inside the QUEST
    # approach/label area on the right side.
]

# Decorative/interactive-looking crystal locations are very
# different from Stage 1 and intentionally form landmarks.
# Values are percentages of the fullscreen dimensions.
STAGE2_CRYSTALS = [
    (0.14, 0.30, 28),
    (0.34, 0.16, 34),
    (0.53, 0.24, 24),
    (0.70, 0.18, 32),
    (0.88, 0.30, 25),
    (0.38, 0.48, 31),
    (0.17, 0.60, 24),
    (0.53, 0.66, 27),
    (0.72, 0.78, 34),
    (0.27, 0.82, 22),
    (0.84, 0.82, 23),
]

STAGE2_ROCKS = [
    (0.16, 0.43, 28),
    (0.35, 0.58, 24),
    (0.56, 0.32, 27),
    (0.69, 0.48, 22),
    (0.47, 0.82, 25),
    (0.88, 0.70, 25),
]

def stage2_point(x_percent, y_percent):
    return (
        int(SCREEN_WIDTH * x_percent),
        int(SCREEN_HEIGHT * y_percent)
    )


def is_position_blocked(x, y):

    player_rect = pygame.Rect(
        int(x - PLAYER_SIZE // 2),
        int(y - PLAYER_SIZE // 2),
        PLAYER_SIZE,
        PLAYER_SIZE
    )

    if current_level == 1:

        for obstacle in LEVEL1_OBSTACLES:
            if player_rect.colliderect(obstacle):
                return True

        for tree_x, tree_y in LEVEL1_TREES:
            tree_collision = pygame.Rect(
                tree_x - 24,
                tree_y + 8,
                48,
                55
            )

            if player_rect.colliderect(tree_collision):
                return True

    elif current_level == 2:

        for obstacle in STAGE2_OBSTACLES:
            if player_rect.colliderect(obstacle):
                return True

        for rock_x_pct, rock_y_pct, rock_r in STAGE2_ROCKS:
            rock_x, rock_y = stage2_point(rock_x_pct, rock_y_pct)

            rock_collision = pygame.Rect(
                rock_x - rock_r,
                rock_y - rock_r,
                rock_r * 2,
                rock_r * 2
            )

            if player_rect.colliderect(rock_collision):
                return True

        # Crystals are solid obstacles in the cavern.
        for crystal_x_pct, crystal_y_pct, crystal_size in STAGE2_CRYSTALS:
            crystal_x, crystal_y = stage2_point(
                crystal_x_pct,
                crystal_y_pct
            )

            crystal_collision = pygame.Rect(
                crystal_x - int(crystal_size * 0.55),
                crystal_y - int(crystal_size * 0.80),
                int(crystal_size * 1.10),
                int(crystal_size * 1.60)
            )

            if player_rect.colliderect(crystal_collision):
                return True

    elif current_level == 3:

        for obstacle in STAGE3_OBSTACLES:
            if player_rect.colliderect(obstacle):
                return True

        # Temple pillars are solid objects.
        for pillar_x_pct, pillar_y_pct, pillar_radius in STAGE3_PILLARS:
            pillar_x, pillar_y = stage2_point(
                pillar_x_pct,
                pillar_y_pct
            )

            pillar_collision = pygame.Rect(
                pillar_x - pillar_radius,
                pillar_y - pillar_radius,
                pillar_radius * 2,
                pillar_radius * 2
            )

            if player_rect.colliderect(pillar_collision):
                return True

    return False

def draw_tree(x, y):

    # Larger tree for the fullscreen master UI.
    trunk_w = 24
    trunk_h = 42

    # Trunk
    pygame.draw.rect(
        screen,
        (90, 55, 32),
        (x - trunk_w // 2, y + 18, trunk_w, trunk_h)
    )

    pygame.draw.rect(
        screen,
        (155, 95, 45),
        (x - trunk_w // 2 + 5, y + 20, 5, trunk_h - 5)
    )

    # Layered canopy
    pygame.draw.circle(
        screen,
        (25, 115, 55),
        (x, y),
        38
    )

    pygame.draw.circle(
        screen,
        (40, 155, 70),
        (x - 22, y + 8),
        30
    )

    pygame.draw.circle(
        screen,
        (50, 175, 80),
        (x + 22, y + 8),
        30
    )

    pygame.draw.circle(
        screen,
        (70, 195, 95),
        (x, y - 18),
        25
    )

    # Small highlight
    pygame.draw.circle(
        screen,
        (105, 225, 125),
        (x - 9, y - 23),
        8
    )


def draw_start_marker():

    # Permanent origin marker. It is deliberately placed
    # BELOW the starting character so it does not overlap
    # the game title or the character itself.
    if current_level == 2:
        marker_x = STAGE2_START_X
        marker_y = STAGE2_START_Y
    elif current_level == 3:
        marker_x = STAGE3_START_X
        marker_y = STAGE3_START_Y
    else:
        marker_x = 85
        marker_y = 125

    arrow_top = marker_y + PLAYER_SIZE // 2 + 16
    arrow_tip = arrow_top + 34

    pygame.draw.line(
        screen,
        YELLOW,
        (marker_x, arrow_top),
        (marker_x, arrow_tip),
        5
    )

    pygame.draw.polygon(
        screen,
        YELLOW,
        [
            (marker_x - 12, arrow_tip - 2),
            (marker_x + 12, arrow_tip - 2),
            (marker_x, arrow_tip + 14)
        ]
    )

    start_surface = font_small.render(
        "START",
        True,
        YELLOW
    )

    screen.blit(
        start_surface,
        (
            marker_x - start_surface.get_width() // 2,
            arrow_tip + 18
        )
    )


# ============================================================
# STAGE 2 DRAW HELPERS
# ============================================================

def draw_crystal(x, y, size):

    points = [
        (x, y - size),
        (x + size // 2, y - size // 3),
        (x + size // 3, y + size),
        (x - size // 3, y + size),
        (x - size // 2, y - size // 3),
    ]

    pygame.draw.polygon(
        screen,
        (80, 210, 230),
        points
    )

    pygame.draw.polygon(
        screen,
        (170, 245, 255),
        points,
        3
    )

    pygame.draw.line(
        screen,
        WHITE,
        (x, y - size + 7),
        (x - size // 5, y + size // 2),
        2
    )


def draw_rock(x, y, radius):

    pygame.draw.circle(
        screen,
        (80, 80, 105),
        (x, y),
        radius
    )

    pygame.draw.circle(
        screen,
        (130, 130, 155),
        (x - radius // 3, y - radius // 3),
        radius // 3
    )

    pygame.draw.circle(
        screen,
        (45, 45, 65),
        (x, y),
        radius,
        3
    )


def draw_temple_pillar(x, y, radius):

    pillar_rect = pygame.Rect(
        x - radius,
        y - radius,
        radius * 2,
        radius * 2
    )

    pygame.draw.rect(
        screen,
        (68, 52, 92),
        pillar_rect,
        border_radius=6
    )

    pygame.draw.rect(
        screen,
        (225, 195, 105),
        pillar_rect,
        4,
        border_radius=6
    )

    pygame.draw.line(
        screen,
        (235, 215, 165),
        (pillar_rect.left + 8, pillar_rect.top + 10),
        (pillar_rect.right - 8, pillar_rect.top + 10),
        3
    )


def draw_temple_arena(play_rect):

    screen.fill((72, 57, 45), play_rect)

    # Large stone floor bands
    for row in range(4):
        y = play_rect.top + row * (play_rect.height // 4)
        pygame.draw.line(
            screen,
            (112, 91, 68),
            (play_rect.left, y),
            (play_rect.right, y),
            2
        )

    # Pillars
    for x_pct, y_pct, radius in STAGE3_PILLARS:
        x, y = stage2_point(x_pct, y_pct)
        draw_temple_pillar(x, y, radius)

    # Stone walls
    for obstacle in STAGE3_OBSTACLES:

        pygame.draw.rect(
            screen,
            (93, 76, 61),
            obstacle,
            border_radius=4
        )

        pygame.draw.rect(
            screen,
            (208, 181, 128),
            obstacle,
            4,
            border_radius=4
        )

        # Stone block seams
        if obstacle.width > obstacle.height:
            for seam_x in range(obstacle.left + 38, obstacle.right, 48):
                pygame.draw.line(
                    screen,
                    (135, 108, 82),
                    (seam_x, obstacle.top + 5),
                    (seam_x, obstacle.bottom - 5),
                    2
                )
        else:
            for seam_y in range(obstacle.top + 38, obstacle.bottom, 48):
                pygame.draw.line(
                    screen,
                    (135, 108, 82),
                    (obstacle.left + 5, seam_y),
                    (obstacle.right - 5, seam_y),
                    2
                )


def draw_cavern_arena(play_rect):

    # Deep cavern floor
    screen.fill((22, 28, 58), play_rect)

    # Cave-floor bands
    pygame.draw.rect(
        screen,
        (28, 38, 78),
        (
            play_rect.left,
            play_rect.top,
            play_rect.width,
            play_rect.height // 3
        )
    )

    pygame.draw.rect(
        screen,
        (24, 33, 68),
        (
            play_rect.left,
            play_rect.top + play_rect.height * 2 // 3,
            play_rect.width,
            play_rect.height // 3
        )
    )

    # Crystal decorations
    for crystal_x_pct, crystal_y_pct, crystal_size in STAGE2_CRYSTALS:
        crystal_x, crystal_y = stage2_point(
            crystal_x_pct,
            crystal_y_pct
        )
        draw_crystal(crystal_x, crystal_y, crystal_size)

    # Rocks
    for rock_x_pct, rock_y_pct, rock_radius in STAGE2_ROCKS:
        rock_x, rock_y = stage2_point(
            rock_x_pct,
            rock_y_pct
        )
        draw_rock(rock_x, rock_y, rock_radius)

    # Stone barriers
    for obstacle in STAGE2_OBSTACLES:

        pygame.draw.rect(
            screen,
            (58, 60, 82),
            obstacle
        )

        pygame.draw.rect(
            screen,
            (125, 130, 165),
            obstacle,
            4
        )

        pygame.draw.line(
            screen,
            (175, 180, 210),
            (obstacle.left + 10, obstacle.top + 9),
            (obstacle.right - 10, obstacle.top + 9),
            3
        )

        pygame.draw.line(
            screen,
            (45, 47, 65),
            (obstacle.left + 10, obstacle.bottom - 9),
            (obstacle.right - 10, obstacle.bottom - 9),
            3
        )


# ============================================================
# DRAW GAME WORLD
# ============================================================

def draw_final_victory():
    # RPG-style final victory screen
    screen.fill((16, 10, 34))

    # Layered kingdom backdrop
    pygame.draw.circle(screen, (35, 25, 72), (SCREEN_WIDTH // 2, 210), 230)
    pygame.draw.circle(screen, (28, 20, 58), (SCREEN_WIDTH // 2, 210), 185)

    outer = pygame.Rect(55, 35, SCREEN_WIDTH - 110, SCREEN_HEIGHT - 70)
    pygame.draw.rect(screen, (31, 22, 64), outer, border_radius=28)
    pygame.draw.rect(screen, (225, 195, 105), outer, 4, border_radius=28)
    pygame.draw.rect(screen, (55, 39, 95), outer.inflate(-16, -16), 2, border_radius=22)

    title_font = pygame.font.Font(None, max(62, min(86, int(SCREEN_HEIGHT * 0.10))))
    hero_font = pygame.font.Font(None, max(38, min(58, int(SCREEN_HEIGHT * 0.065))))
    stage_font = pygame.font.Font(None, max(25, min(32, int(SCREEN_HEIGHT * 0.036))))
    control_font = pygame.font.Font(None, max(27, min(36, int(SCREEN_HEIGHT * 0.040))))

    draw_centered_text("NUMERA QUEST", title_font, WHITE, SCREEN_HEIGHT * 0.13)
    draw_centered_text("THE KINGDOM OF NUMBERS IS SAFE!", hero_font, CYAN, SCREEN_HEIGHT * 0.23)

    # Victory emblem / restored Number Kingdom seal
    emblem_x = SCREEN_WIDTH // 2
    emblem_y = int(SCREEN_HEIGHT * 0.43)
    pygame.draw.circle(screen, (52, 37, 92), (emblem_x, emblem_y), 82)
    pygame.draw.circle(screen, (225, 195, 105), (emblem_x, emblem_y), 82, 5)
    pygame.draw.circle(screen, (88, 67, 135), (emblem_x, emblem_y), 64, 2)
    draw_centered_text("★", title_font, YELLOW, emblem_y - 43)

    draw_centered_text("ALL 3 QUESTS COMPLETED", font_large, WHITE, SCREEN_HEIGHT * 0.59)

    # Three completed adventures
    stages = [
        ("1", "NUMBER FOREST"),
        ("2", "CRYSTAL CAVERNS"),
        ("3", "NUMBER TEMPLE"),
    ]
    gap = 18
    card_w = min(255, (SCREEN_WIDTH - 170 - 2 * gap) // 3)
    card_h = 58
    total_w = card_w * 3 + gap * 2
    start_x = (SCREEN_WIDTH - total_w) // 2
    card_y = int(SCREEN_HEIGHT * 0.65)

    for i, (num, name) in enumerate(stages):
        rect = pygame.Rect(start_x + i * (card_w + gap), card_y, card_w, card_h)
        pygame.draw.rect(screen, (45, 33, 82), rect, border_radius=12)
        pygame.draw.rect(screen, (102, 83, 150), rect, 2, border_radius=12)
        pygame.draw.circle(screen, (225, 195, 105), (rect.x + 25, rect.centery), 15)
        draw_centered_text("✓", stage_font, (35, 28, 55), rect.centery - 12, center_x=rect.x + 25)
        text_surface = stage_font.render(name, True, WHITE)
        screen.blit(text_surface, (rect.x + 48, rect.centery - text_surface.get_height() // 2))

    draw_centered_text("QUEST COMPLETE", font_medium, YELLOW, SCREEN_HEIGHT * 0.79)

    # Actual controller actions are shown explicitly.
    control_y = int(SCREEN_HEIGHT * 0.88)
    draw_centered_text("A  —  PLAY AGAIN", control_font, WHITE, control_y, center_x=SCREEN_WIDTH * 0.37)
    draw_centered_text("B  —  EXIT", control_font, WHITE, control_y, center_x=SCREEN_WIDTH * 0.63)

def draw_world():

    screen.fill((22, 18, 38))

    # --------------------------------------------------------
    # HEADER - unchanged master UI structure
    # --------------------------------------------------------

    header_rect = pygame.Rect(
        20, 15, SCREEN_WIDTH - 40, 60
    )

    pygame.draw.rect(screen, (30, 24, 55), header_rect)
    pygame.draw.rect(screen, PURPLE, header_rect, 2)

    draw_text("NUMERA QUEST", font_title, WHITE, 35, 22)
    draw_text(
        "THE KINGDOM OF NUMBERS",
        font_medium,
        CYAN,
        355,
        29
    )

    if current_level == 1:
        level_name = "LEVEL 1  •  NUMBER FOREST"
    elif current_level == 2:
        level_name = "LEVEL 2  •  CRYSTAL CAVERNS"
    else:
        level_name = "LEVEL 3  •  NUMBER TEMPLE"

    level_surface = font_medium.render(
        level_name,
        True,
        YELLOW
    )

    screen.blit(
        level_surface,
        (
            header_rect.right - level_surface.get_width() - 20,
            29
        )
    )

    # --------------------------------------------------------
    # MAIN PLAYFIELD
    # --------------------------------------------------------

    play_rect = pygame.Rect(
        25,
        90,
        SCREEN_WIDTH - 315,
        SCREEN_HEIGHT - 135
    )

    if current_level == 1:

        pygame.draw.rect(
            screen,
            (18, 75, 48),
            play_rect
        )

        pygame.draw.rect(
            screen,
            (80, 210, 110),
            play_rect,
            3
        )

        for tree_x, tree_y in LEVEL1_TREES:
            draw_tree(tree_x, tree_y)

        for obstacle in LEVEL1_OBSTACLES:

            pygame.draw.rect(screen, (55, 45, 30), obstacle)
            pygame.draw.rect(screen, (150, 105, 55), obstacle, 4)

            pygame.draw.line(
                screen,
                (195, 145, 80),
                (obstacle.left + 10, obstacle.top + 10),
                (obstacle.right - 10, obstacle.top + 10),
                3
            )

            pygame.draw.line(
                screen,
                (115, 75, 38),
                (obstacle.left + 10, obstacle.bottom - 10),
                (obstacle.right - 10, obstacle.bottom - 10),
                3
            )

    elif current_level == 2:

        draw_cavern_arena(play_rect)

        pygame.draw.rect(
            screen,
            (100, 150, 220),
            play_rect,
            3
        )

    else:

        draw_temple_arena(play_rect)

        pygame.draw.rect(
            screen,
            (218, 181, 91),
            play_rect,
            3
        )

    # --------------------------------------------------------
    # QUEST
    # --------------------------------------------------------

    challenge_rect = get_challenge_rect()

    if quest_completed:

        pygame.draw.circle(
            screen,
            DARK_GRAY,
            challenge_rect.center,
            57
        )

        pygame.draw.circle(
            screen,
            GREEN,
            challenge_rect.center,
            57,
            5
        )

        check_x, check_y = challenge_rect.center

        pygame.draw.line(
            screen,
            GREEN,
            (check_x - 22, check_y),
            (check_x - 6, check_y + 16),
            7
        )

        pygame.draw.line(
            screen,
            GREEN,
            (check_x - 6, check_y + 16),
            (check_x + 28, check_y - 22),
            7
        )

        label = "CLEARED"

    else:

        pygame.draw.circle(
            screen,
            DARK_PURPLE,
            challenge_rect.center,
            64
        )

        pygame.draw.circle(
            screen,
            YELLOW,
            challenge_rect.center,
            64,
            5
        )

        pygame.draw.circle(
            screen,
            PURPLE,
            challenge_rect.center,
            48
        )

        question_surface = font_title.render("?", True, YELLOW)

        screen.blit(
            question_surface,
            (
                challenge_rect.centerx - question_surface.get_width() // 2,
                challenge_rect.centery - question_surface.get_height() // 2 - 6
            )
        )

        label = "QUEST"

    label_surface = font_medium.render(label, True, WHITE)

    screen.blit(
        label_surface,
        (
            challenge_rect.centerx - label_surface.get_width() // 2,
            challenge_rect.bottom + 18
        )
    )

    # --------------------------------------------------------
    # START MARKER
    # --------------------------------------------------------

    draw_start_marker()

    # --------------------------------------------------------
    # PLAYER
    # --------------------------------------------------------

    player_rect = pygame.Rect(
        int(player_x - PLAYER_SIZE // 2),
        int(player_y - PLAYER_SIZE // 2),
        PLAYER_SIZE,
        PLAYER_SIZE
    )

    pygame.draw.rect(
        screen,
        GREEN,
        player_rect,
        border_radius=9
    )

    pygame.draw.rect(
        screen,
        WHITE,
        player_rect,
        3,
        border_radius=9
    )

    pygame.draw.circle(
        screen,
        BLACK,
        (player_rect.left + 15, player_rect.top + 16),
        4
    )

    pygame.draw.circle(
        screen,
        BLACK,
        (player_rect.left + 37, player_rect.top + 16),
        4
    )

    pygame.draw.arc(
        screen,
        BLACK,
        (
            player_rect.left + 14,
            player_rect.top + 21,
            24,
            18
        ),
        0,
        3.14,
        3
    )

    # --------------------------------------------------------
    # HOW TO PLAY
    # --------------------------------------------------------

    how_to_play_rect = pygame.Rect(
        SCREEN_WIDTH - 275,
        90,
        250,
        SCREEN_HEIGHT - 135
    )

    pygame.draw.rect(
        screen,
        (25, 35, 55),
        how_to_play_rect
    )

    pygame.draw.rect(
        screen,
        CYAN,
        how_to_play_rect,
        3
    )

    title_surface = font_medium.render(
        "HOW TO PLAY",
        True,
        YELLOW
    )

    screen.blit(
        title_surface,
        (
            how_to_play_rect.centerx - title_surface.get_width() // 2,
            how_to_play_rect.top + 15
        )
    )

    instruction_x = how_to_play_rect.left + 16

    if current_level == 1:
        instructions = [
            ("1", "Move through", "the forest."),
            ("2", "Avoid the", "barriers."),
            ("3", "Reach the", "QUEST marker."),
            ("4", "Press A to", "start the quest."),
            ("5", "Show the", "correct fingers."),
        ]
    elif current_level == 2:
        instructions = [
            ("1", "Explore the", "crystal cavern."),
            ("2", "Avoid rocks", "and stone walls."),
            ("3", "Reach the", "QUEST marker."),
            ("4", "Press A to", "start the quest."),
            ("5", "Show the", "correct fingers."),
        ]
    else:
        instructions = [
            ("1", "Explore the", "number temple."),
            ("2", "Avoid pillars", "and stone walls."),
            ("3", "Reach the", "QUEST marker."),
            ("4", "Press A to", "start the quest."),
            ("5", "Show the", "correct fingers."),
        ]

    y = how_to_play_rect.top + 68

    for number, line1, line2 in instructions:

        pygame.draw.circle(
            screen,
            PURPLE,
            (instruction_x + 13, y + 13),
            13
        )

        number_surface = font_small.render(
            number,
            True,
            WHITE
        )

        screen.blit(
            number_surface,
            (
                instruction_x + 13 - number_surface.get_width() // 2,
                y + 13 - number_surface.get_height() // 2
            )
        )

        draw_text(
            line1,
            font_small,
            WHITE,
            instruction_x + 35,
            y
        )

        draw_text(
            line2,
            font_small,
            GRAY,
            instruction_x + 35,
            y + 23
        )

        y += 62

    # --------------------------------------------------------
    # FOOTER
    # --------------------------------------------------------

    footer_y = SCREEN_HEIGHT - 32

    draw_text(
        "LEFT STICK / D-PAD  MOVE",
        font_small,
        WHITE,
        30,
        footer_y
    )

    draw_text(
        "A  INTERACT",
        font_small,
        YELLOW,
        300,
        footer_y
    )

    draw_text(
        "START  PAUSE",
        font_small,
        GRAY,
        465,
        footer_y
    )

    status_text = (
        "● APP LAB CONNECTED"
        if target_ip is not None
        else "● APP LAB NOT CONNECTED"
    )

    status_color = GREEN if target_ip is not None else GRAY

    status_surface = font_small.render(
        status_text,
        True,
        status_color
    )

    screen.blit(
        status_surface,
        (
            SCREEN_WIDTH - status_surface.get_width() - 25,
            footer_y
        )
    )

# ============================================================
# DRAW CHALLENGE SCREEN
# ============================================================

def draw_challenge():

    # Keep the game world behind the challenge so this feels
    # like a popup rather than a completely different screen.
    # A translucent overlay focuses attention on the challenge.
    overlay = pygame.Surface(
        (SCREEN_WIDTH, SCREEN_HEIGHT),
        pygame.SRCALPHA
    )

    overlay.fill((8, 5, 25, 65))
    screen.blit(overlay, (0, 0))

    # --------------------------------------------------------
    # CENTERED CHALLENGE POPUP
    # --------------------------------------------------------

    popup_width = min(900, SCREEN_WIDTH - 260)
    popup_height = min(560, SCREEN_HEIGHT - 210)

    popup_rect = pygame.Rect(
        (SCREEN_WIDTH - popup_width) // 2,
        (SCREEN_HEIGHT - popup_height) // 2,
        popup_width,
        popup_height
    )

    # Shadow
    shadow_rect = popup_rect.move(10, 12)

    pygame.draw.rect(
        screen,
        (8, 8, 18),
        shadow_rect,
        border_radius=18
    )

    # Popup background
    pygame.draw.rect(
        screen,
        DARK_BLUE,
        popup_rect,
        border_radius=18
    )

    pygame.draw.rect(
        screen,
        PURPLE,
        popup_rect,
        4,
        border_radius=18
    )

    # Inner accent line
    inner_rect = popup_rect.inflate(-16, -16)

    pygame.draw.rect(
        screen,
        (55, 95, 180),
        inner_rect,
        2,
        border_radius=13
    )

    # --------------------------------------------------------
    # TITLE
    # --------------------------------------------------------

    draw_centered_text(
        "NUMBER CHALLENGE",
        font_title,
        WHITE,
        popup_rect.top + 42
    )

    # --------------------------------------------------------
    # QUESTION - deliberately large and clear
    # --------------------------------------------------------

    challenge_font = pygame.font.Font(
        None,
        max(64, min(90, int(SCREEN_HEIGHT * 0.085)))
    )

    draw_centered_text(
        challenge_question,
        challenge_font,
        YELLOW,
        popup_rect.top + 125
    )

    # --------------------------------------------------------
    # INSTRUCTION
    # --------------------------------------------------------

    draw_centered_text(
        "Show your answer using your fingers",
        font_medium,
        CYAN,
        popup_rect.top + 220
    )

    # --------------------------------------------------------
    # CAMERA STATUS
    # --------------------------------------------------------

    if challenge_selected_answer == 0:

        draw_centered_text(
            "Show your hand to the camera",
            font_medium,
            WHITE,
            popup_rect.top + 305
        )

    else:

        detected_font = pygame.font.Font(
            None,
            max(30, min(42, int(SCREEN_HEIGHT * 0.040)))
        )

        draw_centered_text(
            f"Detected answer: {challenge_selected_answer}",
            detected_font,
            WHITE,
            popup_rect.top + 305
        )

    # --------------------------------------------------------
    # FEEDBACK MESSAGE
    # --------------------------------------------------------

    if challenge_message:

        message_rect = pygame.Rect(
            popup_rect.left + 70,
            popup_rect.top + 365,
            popup_rect.width - 140,
            58
        )

        pygame.draw.rect(
            screen,
            BLACK,
            message_rect,
            border_radius=10
        )

        pygame.draw.rect(
            screen,
            YELLOW,
            message_rect,
            2,
            border_radius=10
        )

        draw_centered_text(
            challenge_message,
            font_medium,
            WHITE,
            message_rect.top + 12
        )

    # --------------------------------------------------------
    # FOOTER INSIDE POPUP
    # --------------------------------------------------------

    draw_centered_text(
        "Show your fingers     B = Back",
        font_small,
        GRAY,
        popup_rect.bottom - 38
    )

# ============================================================
# DRAW PAUSE SCREEN
# ============================================================

def draw_pause():

    overlay = pygame.Surface(
        (SCREEN_WIDTH, SCREEN_HEIGHT),
        pygame.SRCALPHA
    )

    overlay.fill((0, 0, 0, 170))

    screen.blit(overlay, (0, 0))

    draw_centered_text(
        "GAME PAUSED",
        font_title,
        WHITE,
        SCREEN_HEIGHT // 2 - 45
    )

    draw_centered_text(
        "Press START to continue",
        font_medium,
        CYAN,
        SCREEN_HEIGHT // 2 + 5
    )


# ============================================================
# BUTTON EDGE DETECTION
# ============================================================

def button_pressed(button_number):

    if joystick is None:
        return False

    if button_number >= joystick.get_numbuttons():
        return False

    current = joystick.get_button(button_number)

    previous = previous_buttons[button_number]

    return current == 1 and previous == 0


def update_previous_buttons():

    if joystick is None:
        return

    count = min(
        joystick.get_numbuttons(),
        len(previous_buttons)
    )

    for i in range(count):

        previous_buttons[i] = joystick.get_button(i)


# ============================================================
# MAIN LOOP
# ============================================================

print("Starting Numera Quest...")
print("Use LEFT STICK or D-PAD to move.")
print("A = Interact")
print("B = Back")
print("START = Pause")
print("============================================================")


# Important:
# The game window is already open before this happens.
try_app_lab_handshake()

send_audio_command("welcome")
send_audio_command("stage1_music")

camera_thread = threading.Thread(
    target=camera_receiver,
    daemon=True
)

camera_thread.start()

last_snapshot_time = 0


while running:

    # --------------------------------------------------------
    # EVENTS
    # --------------------------------------------------------

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            running = False

        elif event.type == pygame.KEYDOWN:

            # ESC also closes the game
            if event.key == pygame.K_ESCAPE:

                pygame.display.quit()
                pygame.quit()
                os._exit(0)

            # Development-only finger-count simulation.
            # Later this will be replaced by camera recognition.
            elif challenge_active:

                if event.key == pygame.K_1:
                    challenge_selected_answer = 1
                    challenge_message = ""
                    challenge_message_timer = 0

                elif event.key == pygame.K_2:
                    challenge_selected_answer = 2
                    challenge_message = ""
                    challenge_message_timer = 0

                elif event.key == pygame.K_3:
                    challenge_selected_answer = 3
                    challenge_message = ""
                    challenge_message_timer = 0

                elif event.key == pygame.K_4:
                    challenge_selected_answer = 4
                    challenge_message = ""
                    challenge_message_timer = 0

                elif event.key == pygame.K_5:
                    challenge_selected_answer = 5
                    challenge_message = ""
                    challenge_message_timer = 0


    # --------------------------------------------------------
    # CONTROLLER STATE
    # --------------------------------------------------------

    axis_x = 0.0
    axis_y = 0.0

    dpad_x = 0
    dpad_y = 0

    a_pressed = 0
    b_pressed = 0

    if joystick is not None:

        pygame.event.pump()

        if joystick.get_button(1) or joystick.get_button(9):
            print(
                "DEBUG BUTTONS:",
                "B=", joystick.get_button(1),
                "START=", joystick.get_button(9)
            )

        # ----------------------------------------------------
        # LEFT JOYSTICK
        # ----------------------------------------------------

        if joystick.get_numaxes() >= 2:

            axis_x = joystick.get_axis(0)
            axis_y = joystick.get_axis(1)

            # Apply deadzone
            if abs(axis_x) < DEADZONE:
                axis_x = 0.0

            if abs(axis_y) < DEADZONE:
                axis_y = 0.0

        # ----------------------------------------------------
        # D-PAD / HAT
        # ----------------------------------------------------

        if joystick.get_numhats() > 0:

            dpad_x, dpad_y = joystick.get_hat(0)

        # ----------------------------------------------------
        # A BUTTON
        # Button 2 confirmed from diagnostic
        # ----------------------------------------------------

        if joystick.get_numbuttons() > 2:

            a_pressed = joystick.get_button(2)
            b_pressed = joystick.get_button(1)


    # --------------------------------------------------------
    # FINAL VICTORY SCREEN CONTROLS
    # A = PLAY AGAIN
    # B = EXIT
    # --------------------------------------------------------

    if final_victory:

        if button_pressed(2):
            final_victory = False

            current_level = 1
            player_x = 85
            player_y = 125

            quest_completed = False
            challenge_active = False
            challenge_success = False
            challenge_attempts = 0
            challenge_selected_answer = 0
            answer_submitted = False
            challenge_message = ""
            challenge_message_timer = 0

            challenge_question = LEVEL_CHALLENGES[1]["question"]
            challenge_correct_answer = LEVEL_CHALLENGES[1]["answer"]

            camera_stable_answer = 0
            camera_candidate = "unknown"
            camera_candidate_count = 0
            last_announced_answer = 0
            camera_waiting_for_fresh_hand = False

            interaction_message = ""
            interaction_timer = 0

            send_audio_command("stage1_music")

            print("FINAL SCREEN: A -> PLAY AGAIN")
            print("GAME: RESTARTED AT LEVEL 1")

        elif button_pressed(1):
            print("FINAL SCREEN: B -> EXIT")

            pygame.display.quit()
            pygame.quit()
            os._exit(0)

        # While the victory screen is active, do not allow normal
        # gameplay, movement, pause, or challenge input to continue.
        if final_victory:
            draw_final_victory()
            pygame.display.flip()
            clock.tick(30)
            continue

    # --------------------------------------------------------
    # EXIT / PAUSE
    # Button 9 = START
    # Button 1 = B
    # --------------------------------------------------------

    # START + B = Exit Game
    if button_pressed(9) and b_pressed:

        print("START + B: EXITING GAME")

        pygame.display.quit()
        pygame.quit()
        os._exit(0)

    # START alone = Pause / Resume
    elif button_pressed(9):

        paused = not paused

        print(
            "Game:",
            "PAUSED" if paused else "RESUMED"
        )


    # --------------------------------------------------------
    # MOVEMENT
    # --------------------------------------------------------

    if not paused and not challenge_active:

        # Start with joystick movement
        move_x = axis_x
        move_y = axis_y

        # D-pad can override joystick direction
        # when pressed.
        if dpad_x != 0:

            move_x = float(dpad_x)

        if dpad_y != 0:

            # Pygame HAT:
            # Up = +1
            # Down = -1
            #
            # Screen Y is opposite, so invert it.
            move_y = float(-dpad_y)

        # Apply movement with obstacle collision
        new_x = player_x + move_x * PLAYER_SPEED
        new_y = player_y + move_y * PLAYER_SPEED

        # Check X movement
        if not is_position_blocked(new_x, player_y):
            player_x = new_x
        else:
            play_collision_sound()

        # Check Y movement
        if not is_position_blocked(player_x, new_y):
            player_y = new_y
        else:
            play_collision_sound()

        # Keep player inside game area
        min_x = 25 + PLAYER_SIZE // 2
        max_x = SCREEN_WIDTH - 315 - PLAYER_SIZE // 2

        min_y = 90 + PLAYER_SIZE // 2
        max_y = SCREEN_HEIGHT - 35 - PLAYER_SIZE // 2

        player_x = max(
            min_x,
            min(max_x, player_x)
        )

        player_y = max(
            min_y,
            min(max_y, player_y)
        )


    # --------------------------------------------------------
    # A BUTTON / CHALLENGE
    # --------------------------------------------------------

    if not paused:

        if challenge_active:

            challenge_selected_answer = camera_stable_answer

            if (
                challenge_selected_answer != 0
                and challenge_selected_answer == last_announced_answer
                and not answer_submitted
            ):

                if challenge_selected_answer == challenge_correct_answer:

                    challenge_message = "Correct! Challenge complete!"

                    send_audio_command("correct_answer")
                    send_audio_command("victory")

                    challenge_message_timer = 120
                    challenge_success = True
                    quest_completed = True
                    answer_submitted = True

                    print("CHALLENGE: CORRECT")
                    print("QUEST: MARKED CLEARED")

                else:

                    challenge_attempts += 1
                    answer_submitted = False

                    challenge_message = "Not quite. Try again!"
                    challenge_message_timer = 120
                    challenge_success = False

                    print(
                        f"CHALLENGE: WRONG - ATTEMPT {challenge_attempts}"
                    )

                    # Play the immediate wrong-answer SFX first,
                    # then the spoken feedback.
                    send_audio_command("wrong_buzzer")
                    send_audio_command("wrong_answer_try_again")

                    if challenge_attempts == 1:

                        send_audio_command("two_tries_left")

                    elif challenge_attempts == 2:

                        send_audio_command("last_try")

                    if challenge_attempts >= 3:

                        send_audio_command("challenge_failed")

                        answer_submitted = True

                        challenge_message = "Challenge failed. Let's try this stage again."
                        challenge_message_timer = 180

                        print("CHALLENGE: FAILED AFTER 3 ATTEMPTS")

                    # Clear the old camera answer.
                    # The player must show the hand again.
                    camera_stable_answer = 0
                    camera_candidate = "unknown"
                    camera_candidate_count = 0
                    last_announced_answer = 0
                    camera_waiting_for_fresh_hand = True

        else:

            if button_pressed(2) and not quest_completed:

                challenge_rect = get_challenge_rect()

                player_rect = pygame.Rect(
                    int(player_x - PLAYER_SIZE // 2),
                    int(player_y - PLAYER_SIZE // 2),
                    PLAYER_SIZE,
                    PLAYER_SIZE
                )

                interaction_rect = challenge_rect.inflate(
                    INTERACTION_DISTANCE * 2,
                    INTERACTION_DISTANCE * 2
                )

                if interaction_rect.colliderect(player_rect):

                    challenge_active = True
                    challenge_selected_answer = 0
                    challenge_message = ""
                    challenge_message_timer = 0
                    challenge_success = False
                    last_announced_answer = 0
                    # IMPORTANT: Do not reset challenge_attempts here.
                    # Leaving the challenge with B must not restore tries.
                    answer_submitted = False

                    camera_stable_answer = 0
                    camera_candidate = "unknown"
                    camera_candidate_count = 0
                    camera_waiting_for_fresh_hand = False

                    send_audio_command("music_stop")
                    send_audio_command("quest_start")

                    print("A BUTTON: ENTER CHALLENGE")

                else:

                    interaction_message = (
                        "You are too far from the number rune."
                    )

                    interaction_timer = 120

                    print("A BUTTON: TOO FAR FROM QUEST")


    # --------------------------------------------------------
    # B BUTTON
    # Button 1
    # --------------------------------------------------------

    if button_pressed(1):

        if challenge_active:

            challenge_active = False
            challenge_message = ""
            challenge_message_timer = 0
            challenge_success = False
            answer_submitted = False
            last_announced_answer = 0
            camera_stable_answer = 0
            camera_candidate = "unknown"
            camera_candidate_count = 0

            # Resume the current arena music after leaving the challenge.
            send_audio_command(f"stage{current_level}_music")

            # Keep challenge_attempts unchanged. Returning with B is not
            # a new attempt and must not restore the player's tries.
            print(
                f"B BUTTON: BACK TO WORLD (TRIES REMAINING: {3 - challenge_attempts})"
            )

        else:

            print("B BUTTON: BACK")

            interaction_message = "Back"
            interaction_timer = 60

    # --------------------------------------------------------
    # INTERACTION TIMER
    # --------------------------------------------------------

    if interaction_timer > 0:

        interaction_timer -= 1

    else:

        interaction_message = ""


    # --------------------------------------------------------
    # CHALLENGE MESSAGE TIMER
    # --------------------------------------------------------

    if challenge_message_timer > 0:

        challenge_message_timer -= 1

        if challenge_message_timer == 0:
            challenge_message = ""

            if challenge_success:

                challenge_active = False
                challenge_success = False

                if current_level == 1:

                    current_level = 2

                    challenge_question = LEVEL_CHALLENGES[current_level]["question"]
                    challenge_correct_answer = LEVEL_CHALLENGES[current_level]["answer"]

                    quest_completed = False
                    challenge_attempts = 0
                    challenge_selected_answer = 0
                    answer_submitted = False

                    player_x = STAGE2_START_X
                    player_y = STAGE2_START_Y

                    camera_stable_answer = 0
                    camera_candidate = "unknown"
                    camera_candidate_count = 0
                    last_announced_answer = 0
                    camera_waiting_for_fresh_hand = False

                    send_audio_command("stage2_music")

                    print("STAGE TRANSITION: LEVEL 1 -> LEVEL 2")
                    print("PLAYER: RETURNED TO STAGE 2 START")

                elif current_level == 2:

                    current_level = 3

                    challenge_question = LEVEL_CHALLENGES[current_level]["question"]
                    challenge_correct_answer = LEVEL_CHALLENGES[current_level]["answer"]

                    quest_completed = False
                    challenge_attempts = 0
                    challenge_selected_answer = 0
                    answer_submitted = False

                    player_x = STAGE3_START_X
                    player_y = STAGE3_START_Y

                    camera_stable_answer = 0
                    camera_candidate = "unknown"
                    camera_candidate_count = 0
                    last_announced_answer = 0
                    camera_waiting_for_fresh_hand = False

                    send_audio_command("stage3_music")

                    print("STAGE TRANSITION: LEVEL 2 -> LEVEL 3")
                    print("PLAYER: RETURNED TO STAGE 3 START")

                else:

                    # Level 3 is the final quest.
                    final_victory = True
                    send_audio_command("music_stop")
                    print("NUMERA QUEST: ALL 3 QUESTS COMPLETED")
                    print("FINAL VICTORY SCREEN: ACTIVE")

            elif challenge_attempts >= 3:
                challenge_active = False
                challenge_success = False
                challenge_attempts = 0
                answer_submitted = False
                last_announced_answer = 0
                camera_stable_answer = 0
                camera_candidate = "unknown"
                camera_candidate_count = 0

                # Failed challenge: send the player back to the
                # beginning so the complete route must be replayed.
                if current_level == 2:
                    player_x = STAGE2_START_X
                    player_y = STAGE2_START_Y
                elif current_level == 3:
                    player_x = STAGE3_START_X
                    player_y = STAGE3_START_Y
                else:
                    player_x = 85
                    player_y = 125

                send_audio_command(f"stage{current_level}_music")

                print("CHALLENGE: FAILED - RETURN TO WORLD")
                print("PLAYER: RETURNED TO START")

    # --------------------------------------------------------
    # SEND CONTROLLER DATA TO APP LAB
    #
    # Send approximately 30 times per second.
    # Keep same x/y/a structure as previous version.
    # --------------------------------------------------------

    current_time = time.time()

    if current_time - last_snapshot_time >= (1.0 / 30.0):

        # If D-pad is being used, convert it into
        # directional x/y values for the matrix side.

        send_x = axis_x
        send_y = axis_y

        if dpad_x != 0:
            send_x = float(dpad_x)

        if dpad_y != 0:
            send_y = float(-dpad_y)

        send_snapshot(
            send_x,
            send_y,
            a_pressed,
            b_pressed
        )

        last_snapshot_time = current_time


    # --------------------------------------------------------
    # DRAW
    # --------------------------------------------------------

    # Always draw the current gameplay world first. The challenge
    # popup is then layered over it so the forest/cavern remains
    # visible behind the translucent overlay.
    if final_victory:
        draw_final_victory()
    else:
        draw_world()

        if challenge_active:
            draw_challenge()

    # Interaction message
    if interaction_message and not challenge_active:

        message_rect = pygame.Rect(
            160,
            110,
            SCREEN_WIDTH - 320,
            60
        )

        pygame.draw.rect(
            screen,
            BLACK,
            message_rect
        )

        pygame.draw.rect(
            screen,
            YELLOW,
            message_rect,
            2
        )

        draw_centered_text(
            interaction_message,
            font_medium,
            WHITE,
            128
        )


    # Pause overlay
    if paused:

        draw_pause()


    pygame.display.flip()

    clock.tick(FPS)

    # Update button history AFTER processing buttons
    update_previous_buttons()


# ============================================================
# CLEANUP
# ============================================================

print("============================================================")
print("Numera Quest stopped.")
print("============================================================")

if joystick is not None:

    joystick.quit()

pygame.joystick.quit()
pygame.quit()

if sock is not None:

    sock.close()