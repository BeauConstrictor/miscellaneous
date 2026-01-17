# Note on units:
# - Most of the length units here are given in 'world-pixels'. When you first
#   start the game, world-pixels are the same as screen pixels, but as you zoom
# out, world-pixels start to get smaller and smaller onscreen.
# - Probabilities are usually 1 in x.
# - Speed is world-pixels multiplied by seconds since last frame, so needs to be
#   much larger than you would expect.

# Style
# Colours used for snakes and orbs
PALETTE = [
    (255, 0, 0),  
    (255, 102, 0),
    (255, 255, 0),
    (0, 255, 0),  
    (0, 255, 255),
    (0, 102, 255),
    (153, 0, 255),
    (255, 0, 204),
    (255, 0, 255),
    (0, 204, 204) 
]
ORB_SHAKE = 10                  # How vigorously the normal orbs shake
ORB_SHAKE_RATE = 20             # How vigorously the normal orbs shake
ORB_ATTRACTION = 0.3            # How quickly orbs come to you
BIG_ORB_SHAKE_RATE = 100        # How vigorously the big orbs shake
CORPSE_SPREAD = 20              # How spread out the orbs from a corpse are

# UI
UI_PADDING = 20                 # How far from the edge of the screen to place 
                                # ui
PAUSE_BUTTON_PADDING = 100      # How far from edge to place pause message
NAMETAG_HEIGHT = 30             # How high above head to place nametags
MINIMAP_SIZE = 200              # How big to make the (square) minimap
MINIMAP_PADDING = 20            # Distance of minimap from edge of screen
MINIMAP_RADIUS = 10000          # Radius from player head visible in minimap
PLACEMENT_UPDATE_INTERVAL = 100 # Update leaderboard once every x frames
DEBUG_UPDATE_INTERVAL = 15      # Update debug screen once every x frames
LEADERBOARD_SIZE = 3            # How many bots to show above and below player

# Dimensions of the bg.png tile
BG_WIDTH = 599
BG_HEIGHT = 519

# Performance
TARGET_FPS = 30                 # FPS cap
AI_COUNT = 19                   # How many bots to include
ORB_COUNT = 80                  # How many non-corpse orbs to place at once
COLLISION_DETECT_GAP = 3        # Higher = better FPS, but less reliable
                                # collisions

# Gameplay
ORB_ATTRACTION_DIST = 50        # How close you need to be to an orb to eat it 
SPAWN_RADIUS = 3000             # How far away from origin to spawn bots and
                                # player
ORB_LENGTH_ADD = 0.2            # How much length each orb adds
SPEED = 250                     # Standard movement speed
SPRINT_SPEED = 450              # Movement speed when sprinting
SPRINT_LENGTH_LOSS = 2          # How quickly you lose length when sprinting
BIG_ORB_CHANCE = 150            # 1 in x chance to spawn a big orb
STARTING_LENGTH = (20, 300)     # Starting length of player (left), and min-max
                                # for bots
CORPSE_USELESSNESS = 6         # The higher, the less you get from corpses
MAX_EATEN_AT_ONCE = 30          # Max digesting orbs at a time
ORBS_PER_CORPSE_SEGMENT = 3     # How many orbs to spawn per segment in a corpse

# Bot AI
AI_PERLIN_SWAY = 0.05           # How random the AI's movement looks
AI_TURN_SPEED = 0.1             # Max amount a bot can turn
AI_REPEL_WEIGHT = 1.0           # How hard the AI will try to avoid player
AI_REPEL_DISTANCE = 200         # How far away a bot will avoid the player
AI_NOISE_SCALE = 0.01           # How random the AI's movement looks
ALLOW_DEBUG_CHEATS = True       # Enable special keys and open debug menu on
                                # startup

# How wide the snake should be
def snake_radius(length: int) -> float:
    return 10 + length / 10

# How much to zoom out by normally
def zoomed_in_sf(length: int) -> float:
    return length / 400 + 1

# When holding RM, how much to zoom out by
def zoomed_out_sf(length: int) -> float:
    return 15

# How big spots on the minimap are
def minimap_spot_radius(length: int) -> float:
    return 1 + 9 * (length - 20) / 980
