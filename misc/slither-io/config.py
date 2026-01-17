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
BG_WIDTH = 599
BG_HEIGHT = 519
TARGET_FPS = 50
SPAWN_RADIUS = 3000
AI_COUNT = 19
ORB_COUNT = 80
SPEED = 250
SPRINT_SPEED = 350
ORB_LENGTH_ADD = 0.2
ORB_SHAKE = 10
ORB_SHAKE_RATE = 20
ORB_ATTRACTION = 0.3
ORB_ATTRACTION_DIST = 50
NAMETAG_HEIGHT = 30
BIG_ORB_CHANCE = 150
BIG_ORB_SHAKE_RATE = 70
STARTING_LENGTH = (20, 300)
UI_PADDING = 20
PAUSE_BUTTON_PADDING = 100
CORPSE_USELESSNESS = 12
CORPSE_SPREAD = 20
MINIMAP_SIZE = 200
MINIMAP_PADDING = 20
MINIMAP_RADIUS = 10000
PLACEMENT_UPDATE_INTERVAL = 100
DEBUG_UPDATE_INTERVAL = 15
MAX_EATEN_AT_ONCE = 30
ORBS_PER_CORPSE_SEGMENT = 3
LEADERBOARD_SIZE = 3
DEBUG_IS_DEFAULT = False
AI_PERLIN_SWAY = 0.05
AI_TURN_SPEED = 0.1
AI_REPEL_WEIGHT = 1.0
AI_REPEL_DISTANCE = 200
AI_NOISE_SCALE = 0.01
COLLISION_DETECT_GAP = 3

def snake_radius(segment_count: int) -> float:
    return 10 + segment_count / 10

def zoomed_in_sf(segment_count: int) -> float:
    return segment_count / 400 + 1
def zoomed_out_sf(segment_count: int) -> float:
    return 15

def minimap_spot_radius(segment_count: int) -> float:
    return 1 + 9 * (segment_count - 20) / 980
