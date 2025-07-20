import numpy as np
from PIL import Image

num = 128

# Create 8x8 chessboard pattern (0 for black, 255 for white)
chessboard = np.zeros((num, num), dtype=np.uint8)
chessboard[1::2, ::2] = 255
chessboard[::2, 1::2] = 255

# Convert to image and save (mode 'L' for grayscale)
img = Image.fromarray(chessboard, mode='L')
img.save(f'data/chessboard_{num}.png')
