import random
import cv2
import numpy as np
from Matrix import create_matrix
from Astar import bidirectional_astar
import cProfile
import pstats
import os
import time
import math

common_path = r"C:\Users\ASUS\AppData\LocalLow\DefaultCompany\Unity Multiplayer"
file_paths = {
    'map': 'Map\Map.png',
    'player_position': common_path + '\\player.txt',
    'coin_position': common_path + '\\reference_real.txt',
    'enemy_position': common_path + '\\enemy_real.txt',
    'heal_position': common_path + '\\heal_position.txt',
}

def resize_image(image_cv2, new_size):
    return cv2.resize(image_cv2, new_size)

def draw_path(image, path):
    if path:
        for i in range(len(path) - 1):
            cv2.line(image, path[i], path[i + 1], (255, 0, 0), 2)  # Draw path in red
        cv2.imshow('Game Map', image)
        cv2.waitKey(1)  # Display the updated image
    return path

def post_smooth_path(path, matrix):
    if not path:
        return []
    smoothed_path = [path[0]]
    current_point = path[0]
    for next_point in path[1:]:
        if can_reach(current_point, next_point, matrix):
            smoothed_path.append(next_point)
            current_point = next_point
    return smoothed_path

def can_reach(point1, point2, matrix):
    x1, y1 = point1
    x2, y2 = point2
    dx, dy = abs(x2 - x1), abs(y2 - y1)
    sx, sy = (1 if x1 < x2 else -1), (1 if y1 < y2 else -1)
    err = dx - dy

    while True:
        if matrix[y1][x1] != 0:
            return False
        if x1 == x2 and y1 == y2:
            break
        e2 = err * 2
        if e2 > -dy:
            err -= dy
            x1 += sx
        if e2 < dx:
            err += dx
            y1 += sy
    return True

def translate_position(position, map_size, image_size):
    if position is None:
        return None
    map_width, map_height = map_size
    image_width, image_height = image_size
    map_x_min, map_x_max, map_y_min, map_y_max = -52.3, 52.3, -52.3, 52.3
    scale_x = image_width / (map_x_max - map_x_min)
    scale_y = image_height / (map_y_max - map_y_min)
    map_x, map_y = position
    image_x = int((map_x - map_x_min) * scale_x)
    image_y = int((map_y_max - map_y) * scale_y)  # Flip y-axis
    return image_x, image_y


def read_file_with_retries(file_path, retries=5, delay=0.1):
    for _ in range(retries):
        try:
            with open(file_path, 'r') as file:
                content = file.read().strip()
                if content:
                    return content
            time.sleep(delay)
        except PermissionError:
            print(f"Permission denied for {file_path}. Retrying...")
            time.sleep(delay)
        except FileNotFoundError:
            print(f"File not found: {file_path}. Retrying...")
            time.sleep(delay)
    print(f"Failed to read from {file_path} after {retries} retries.")
    return None

def read_position(file_path, previous_position=None):
    content = read_file_with_retries(file_path)
    if content:
        try:
            coordinates = [float(num) for num in content.strip('()').split(',')]
            if previous_position is not None:
                previous_position[:] = coordinates  # Update previous_position
            return tuple(coordinates)
        except ValueError:
            print(f"Error converting content to coordinates: {content}")
    return tuple(previous_position) if previous_position is not None else None

def read_positions(file_path, previous_positions=None):
    content = read_file_with_retries(file_path)
    if content and content.startswith('(') and content.endswith(')'):
        try:
            positions = []
            coordinates_str = content.strip('()').split('),(')
            for coord_str in coordinates_str:
                coordinates = tuple(float(num) for num in coord_str.split(','))
                positions.append(coordinates)
            if previous_positions is not None:
                previous_positions[:] = positions  # Update previous_positions
            return positions
        except ValueError:
            print(f"Error converting content to positions: {content}")
    return previous_positions

def read_positions(file_path, previous_positions=None):
    positions = []
    with open(file_path, 'r') as file:
        line = file.readline().strip()
        if line.startswith('(') and line.endswith(')'):
            coordinates_str = line.strip('()').split('),(')
            for coord_str in coordinates_str:
                coordinates = tuple(float(num) for num in coord_str.split(','))
                positions.append(coordinates)
                if previous_positions is not None:
                    previous_positions.append(coordinates)  # Update previous_positions
    return positions if positions else previous_positions

def draw_player(image, position):
    cv2.circle(image, position, 5, (0, 0, 255), -1)  # Draw player as a red circle

def calculate_positions(position_data_file, translate_position, previous_position=None):
    position = read_position(position_data_file, previous_position)
    position_resized = translate_position(position, (100, 100), (400, 400)) if position else None
    return position_resized

def calculate_multiple_positions(file_path, position_converter, previous_positions=None):
    positions = read_positions(file_path, previous_positions)
    if positions:
        return [position_converter(position, (100, 100), (400, 400)) for position in positions]
    return None

def write_file_with_retries(file_path, data, retries=5, delay=0.1):
    for attempt in range(retries):
        try:
            with open(file_path, 'w') as file:
                file.write(data)
                os.fsync(file.fileno())
            return True
        except IOError as e:
            print(f"Attempt {attempt + 1}: Failed to write to {file_path}: {e}. Retrying in {delay} seconds...")
            time.sleep(delay)
    print(f"Failed to write to {file_path} after {retries} retries.")
    return False

def create_movement_vector(smoothed_path, common_path):
    if smoothed_path and len(smoothed_path) > 5:
        start_point, end_point = smoothed_path[0], smoothed_path[5]
        movement_vector = (end_point[0] - start_point[0], end_point[1] - start_point[1])
        file_path = os.path.join(common_path, "movement_vector.txt")
        data = str(movement_vector)
        write_file_with_retries(file_path, data)

def create_goal_point(smoothed_path, common_path):
    if smoothed_path:
        file_path = os.path.join(common_path, "goal.txt")
        data = str(smoothed_path[-1])
        write_file_with_retries(file_path, data)
        


def draw_line(matrix, x1, y1, x2, y2, check_value=None):
    dx, dy = abs(x2 - x1), abs(y2 - y1)
    sx, sy = (1 if x1 < x2 else -1), (1 if y1 < y2 else -1)
    err = dx - dy
    points = []

    while True:
        if check_value is not None and matrix[y1][x1] == check_value:
            points.append((x1, y1))
        elif check_value is None:
            points.append((x1, y1))
        if x1 == x2 and y1 == y2:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x1 += sx
        if e2 < dx:
            err += dx
            y1 += sy
    return len(points) > 0

def get_map(map_file):
    image_cv2 = cv2.imread(map_file)
    resized_image = resize_image(image_cv2, (400, 400))
    return cv2.cvtColor(resized_image, cv2.COLOR_BGR2RGB), resized_image.copy()

def get_matrix(map_image, is_matrix, is_distance_matrix):
    if is_matrix and is_distance_matrix:
        return create_matrix(map_image)
    if is_matrix:
        return create_matrix(map_image)[0]
    if is_distance_matrix:
        return create_matrix(map_image)[1]
    

import random
import math

def find_value_in_matrix(matrix, target_value, start_position):
    positions = []
    m = len(matrix)      # Number of rows
    n = len(matrix[0])   # Number of columns
    
    start_i, start_j = start_position
    
    # Iterate through the matrix to find the target value from the starting position
    for i in range(start_i, m):
        for j in range(start_j if i == start_i else 0, n):
            if matrix[i][j] == target_value:
                # Calculate Euclidean distance between start_position and (i, j)
                distance = math.sqrt((i - start_i)**2 + (j - start_j)**2)
                if distance < 80 and distance > 50:
                    positions.append((i, j))  # Add the position (i, j) to the list as a tuple
    
    if positions:
        return random.choice(positions)
    else:
        return None 



def calculate_distance(traverse_point, player_position):
    player_x,player_y = player_position
    traverse_x, traverse_y = traverse_point

    # Calculate the distance between player position and traverse point
    distance = math.sqrt((traverse_x - player_x) ** 2 + (traverse_y - player_y) ** 2)

    return distance


traverse_point = None

def find_nearest_point(player_position, points):
    min_distance = float('inf')
    nearest_point = None

    for point in points:
        distance = math.sqrt((player_position[0] - point[0]) ** 2 +
                             (player_position[1] - point[1]) ** 2)
        if distance < min_distance:
            min_distance = distance
            nearest_point = point

    return nearest_point


    
def find_path(decision, map_image_copy, matrix, distance_map):

    global traverse_point
    path = None
    try:
        if os.access(file_paths['player_position'], os.W_OK):
            player_position = calculate_positions(file_paths['player_position'], translate_position)
            if player_position:
                if decision == "collect":
                    coin_position = calculate_positions(file_paths['coin_position'], translate_position)
                    if coin_position:
                        path = bidirectional_astar(matrix, player_position, coin_position, distance_map)
                elif decision == "traverse":
                    if traverse_point is None:
                        # Find a new traverse point if it's not already set
                        result = find_value_in_matrix(matrix, 0,player_position)
                        if result:
                            traverse_point = result  # Take the first found position
                    if traverse_point:
                        distance = calculate_distance(traverse_point,player_position)
                        if(distance < 25):
                            result = find_value_in_matrix(matrix, 0, player_position)
                            traverse_point = result
                            path = bidirectional_astar(matrix, player_position, traverse_point, distance_map)
                        else:
                            path = bidirectional_astar(matrix, player_position, traverse_point, distance_map)
                    else:
                        path = None
                elif decision == "battle":
                    enemy_position = calculate_positions(file_paths['enemy_position'], translate_position)
                    if enemy_position:
                        path = bidirectional_astar(matrix, player_position, enemy_position, distance_map)
                elif decision == "heal":
                    heal_positions = calculate_multiple_positions(file_paths['heal_position'], translate_position)
                    if(heal_positions):
                        heal_position = find_nearest_point(player_position,heal_positions)
                        path = bidirectional_astar(matrix, player_position, heal_position, distance_map)
                        
                print("AA")
                if path:
                    print("CC")
                    smoothed_path = post_smooth_path(path, matrix)
              
                    return smoothed_path, player_position
                else:
                    print("BB")
                    result = find_value_in_matrix(matrix,0,player_position)
                    traverse_point = result
                    # Return default values or handle the case where path is None

                    path = bidirectional_astar(matrix, player_position, traverse_point, distance_map)
                    if(path):
                        smoothed_path = post_smooth_path(path, matrix)
                    return smoothed_path, player_position
                 
            else:
                print(f"Error: Player position could not be determined.")
    except PermissionError:
        print("PermissionError: Unable to access the file.")
    except Exception as e:
        print(f"An error occurred in find_path: {e}")
        


def visualise_path(smoothed_path,map_image_copy,player_position):
    if smoothed_path and player_position:
        map_image = map_image_copy.copy()
        draw_player(map_image, player_position)
        draw_path(map_image, smoothed_path)
        create_movement_vector(smoothed_path,common_path)
        create_goal_point(smoothed_path,common_path)
        cv2.imshow('Game Map', map_image)
        return
def is_clear(matrix, player_position):
    if player_position:
        enemy_position = calculate_positions(file_paths['enemy_position'], translate_position)
        if enemy_position:
            return not draw_line(matrix, player_position[0], player_position[1],
                                 enemy_position[0], enemy_position[1], 1)
        else:
            # Handle case where enemy position cannot be determined
            print("Error: Enemy position could not be determined.")
            return False
    else:
        # Handle case where player position is None
        print("Error: Player position is None.")
        return False