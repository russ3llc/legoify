import numpy as np

SCALE = 12

transparent = np.array([0, 0, 0, 0])
white1 = np.array([255, 255, 255, 60])
white2 = np.array([255, 255, 255, 106])
white3 = np.array([255, 255, 255, 141])
white4 = np.array([255, 255, 255, 168])
black = np.array([0, 0, 0, 80])

indicator = np.tile(transparent, SCALE * SCALE).reshape([SCALE, SCALE, 4]).astype(np.uint8)

# Border Corners
indicator[0, 0] = white2  # Top Left
indicator[SCALE - 1, 0] = white2  # Top Right
indicator[0, SCALE - 1] = white2  # Bottom Left
indicator[SCALE - 1, SCALE - 1] = white2  # Bottom Right
# Border Sides
indicator[0, 1:-1] = white1  # Top
indicator[1:-1, 0] = white1  # Left
indicator[-1, 1:-1] = white1  # Bottom
indicator[1:-1, -1] = white1  # Right

# Center Outline
indicator[4:8, 2] = black  # Top Side
indicator[4:8, 9] = black  # Bottom Side
indicator[2, 4:8] = black  # Left Side
indicator[9, 4:8] = black  # Right Side
indicator[3, 3] = black  # Top Left Corner
indicator[3, 8] = black  # Top Right Corner
indicator[8, 3] = black  # Bottom Left Corner
indicator[8, 8] = black  # Bottom Right Corner

# Center Gradient
indicator[5:7, 5:7] = white4  # Center
# Ring 1
indicator[5:7, 4] = white3  # Left
indicator[5:7, 7] = white3  # Right
indicator[4, 5:7] = white3  # Top
indicator[7, 5:7] = white3  # Bottom
# Ring 2
indicator[5:7, 3] = white2  # Left
indicator[5:7, 8] = white2  # Right
indicator[3, 5:7] = white2  # Top
indicator[8, 5:7] = white2  # Bottom
indicator[4, 4] = white2  # Top Left
indicator[7, 7] = white2  # Bottom Right
indicator[4, 7] = white2  # Top Right
indicator[7, 4] = white2  # Bottom Left
# Ring 3
indicator[4, 3] = white1 # Top Left 1
indicator[3, 4] = white1 # Top Left 2
indicator[7, 3] = white1 # Bottom Left 1
indicator[8, 4] = white1 # Bottom Left 2
indicator[4, 8] = white1 # Top Right 1
indicator[3, 7] = white1 # Top Right 2
indicator[7, 8] = white1 # Bottom Right 1
indicator[8, 7] = white1 # Bottom Right 2