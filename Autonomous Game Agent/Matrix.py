from collections import deque
import numpy as np

def create_distance_map(matrix):
    height, width = matrix.shape
    distance_map = np.full((height, width), np.inf)
    queue = deque()

    # Initialize the queue with all obstacle cells
    obstacles = np.argwhere(matrix != 0)
    for y, x in obstacles:
        distance_map[y, x] = 0
        queue.append((x, y))

    # BFS to compute distance from each obstacle
    while queue:
        x, y = queue.popleft()
        current_distance = distance_map[y, x]

        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height:
                if distance_map[ny, nx] > current_distance + 1:
                    distance_map[ny, nx] = current_distance + 1
                    queue.append((nx, ny))

    return distance_map

def create_matrix(image_rgb):
    color_to_value = {
        (255, 255, 255): 0,  # White (walkable areas)
        (0, 0, 0): 1,        # Black (obstacles)
        (0, 231, 0): 2       # Green (healing zones)
    }

    # Vectorized conversion using numpy
    matrix = np.zeros((image_rgb.shape[0], image_rgb.shape[1]), dtype=int)
    for color, value in color_to_value.items():
        mask = np.all(image_rgb == np.array(color), axis=-1)
        matrix[mask] = value

    distance_map = create_distance_map(matrix)
    
    return matrix, distance_map