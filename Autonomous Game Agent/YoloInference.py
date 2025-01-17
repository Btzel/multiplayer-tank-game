from platform import release
from tracemalloc import stop
import autoit
import cv2
import numpy as np
import pyautogui
import time
import torch
import math
import pyautogui
pyautogui.FAILSAFE = False
import pygetwindow as gw
import keyboard
from ultralytics import YOLO
import ctypes
import win32api as wapi
import re
from DecisionMaker import decision_messenger
import os
from MapPathfinder import find_path,is_clear,visualise_path,get_map,get_matrix,file_paths
import cProfile
import pstats
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Key, Controller as KeyboardController

# Initialize mouse and keyboard controllers
mouse = MouseController()
keyboard = KeyboardController()

GAME_WINDOW_X = 0
GAME_WINDOW_Y = 0
GAME_WINDOW_WIDTH = 800
GAME_WINDOW_HEIGHT = 600
STATIC_PLAYER_LOCATION = (GAME_WINDOW_WIDTH // 2, GAME_WINDOW_HEIGHT // 2)
PATH_LINE_LENGTH = 200  # Length of the path line in pixels
PATH_LINE_COLOR = (0, 255, 0)  # Color of the path line (green)
PATH_LINE_THICKNESS = 2  # Thickness of the path line
path_line_angle = 90  # 90 degrees corresponds to upwards direction
common_path = r"C:\Users\ASUS\AppData\LocalLow\DefaultCompany\Unity Multiplayer"
angle_path = common_path + "\\angle.txt"
health_path = common_path + "\\health.txt"
coin_path = common_path + "\\coin.txt"
last_successful_angle = None
last_successful_target_point = None
last_succesful_coin = 0
last_succesful_health = 100
last_succesful_enemy_count = 0
last_succesful_teammate_count = 0
last_succesful_coin_nearby = False
last_succesful_decision = None
closest_coin = None
previous_decision = None
player_position = None
reference_position = None
reference_pixel_position = None
decision = None
enemy_players = None
is_close = None
angle = None
distance = None


COLORS = {
    "coin": (0, 255, 255),   # Yellow for coins
    "player": (0, 0, 255),   # Blue for players
    "health": (0, 220, 0),   # Green for health
    "inside_circle": (220, 0, 220),  # Magenta for objects inside the circle
    "closest": (180, 180, 0),  # Dark cyan for the closest objects
}
THICKNESS = 1.5  # Thickness of bounding box lines
THICKNESS_CLOSEST = 1.5  # Thickness of lines to closest object
CIRCLE_RADIUS = 200  # Radius of the circle around the player

# Initialize YOLO model
model = YOLO("Model\\best_v8.pt")

# Check and print the device being used
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f'Model is running on: {device}')

# Initialize decision dictionary
decision = {
    "coins": [],
    "player": [],
    "healths": [],
}


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


def read_coin(data_file):
    global last_succesful_coin
    content = read_file_with_retries(data_file)
    if content is not None:
        try:
            last_succesful_coin = int(content)
        except ValueError:
            print(f"Error converting content to int: {content}")
    return last_succesful_coin  
        
def read_health(data_file):
    global last_succesful_health
    content = read_file_with_retries(data_file)
    if content is not None:
        try:
            last_succesful_health = int(content)
        except ValueError:
            print(f"Error converting content to int: {content}")
    return last_succesful_health

def angle_reader():
    global last_successful_angle
    content = read_file_with_retries(angle_path)
    if content is not None:
        try:
            content = content.replace(',', '.')
            last_successful_angle = float(content)
        except ValueError:
            print(f"Error converting content to float: {content}")
    return last_successful_angle

def non_max_suppression(boxes, scores, threshold):
    """Apply Non-Maximum Suppression to remove overlapping detections."""
    assert len(boxes) == len(scores)
    
    if len(boxes) == 0:
        return []
    x1 = boxes[:, 0]
    y1 = boxes[:, 1]
    x2 = boxes[:, 2]
    y2 = boxes[:, 3]

    area = (x2 - x1 + 1) * (y2 - y1 + 1)
    sorted_indices = np.argsort(scores)[::-1]
    selected_indices = []

    while len(sorted_indices) > 0:
        current_index = sorted_indices[0]
        selected_indices.append(current_index)

        xx1 = np.maximum(x1[current_index], x1[sorted_indices[1:]])
        yy1 = np.maximum(y1[current_index], y1[sorted_indices[1:]])
        xx2 = np.minimum(x2[current_index], x2[sorted_indices[1:]])
        yy2 = np.minimum(y2[current_index], y2[sorted_indices[1:]])

        intersection_area = np.maximum(0.0, xx2 - xx1 + 1) * np.maximum(0.0, yy2 - yy1 + 1)

        union_area = area[current_index] + area[sorted_indices[1:]] - intersection_area

        iou = intersection_area / union_area

        sorted_indices = sorted_indices[1:][iou <= threshold]

    return selected_indices

def is_inside_circle(center, point, radius):
    return (center[0] - point[0]) ** 2 + (center[1] - point[1]) ** 2 <= radius ** 2

def calculate_distance(object_position, player_position):
    return math.sqrt((object_position[0] - player_position[0])**2 + (object_position[1] - player_position[1])**2)

def extract_color(frame, box):
    x1, y1, x2, y2 = map(int, box)
    player_region = frame[y1:y2, x1:x2]
    average_color = cv2.mean(player_region)[:3]
    return average_color

def is_similar_color(color1, color2, threshold=70):
    color_value = np.linalg.norm(np.array(color1) - np.array(color2))
    print(color_value)
    return color_value > threshold

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

def write_enemy_real(real_position, common_path):
    file_path = os.path.join(common_path, "enemy_real.txt")
    data = f"({real_position[0]}, {real_position[1]})\n"
    write_file_with_retries(file_path, data)
    
def write_reference_real(real_position, common_path):
    file_path = os.path.join(common_path, "reference_real.txt")
    data = f"({real_position[0]}, {real_position[1]})\n"
    write_file_with_retries(file_path, data)

def action_handler(decision,enemy_players,is_close,angle,distance,reference_real_position,player_real_position,map_image_copy,matrix,distance_map):

    if(decision == "heal"):
        heal(map_image_copy,matrix,is_close,distance_map,angle,distance)
    elif(decision == "collect"):
        collect(map_image_copy,matrix,distance_map,angle,distance)
    elif(decision == "traverse"):
        traverse(map_image_copy,matrix,is_close,distance_map,angle,distance)
    elif(decision == "evade"):
        heal(map_image_copy,matrix,is_close,distance_map,angle,distance)
    elif(decision == "shoot and follow"):
        can_shoot = shoot(enemy_players,reference_real_position,player_real_position,map_image_copy,matrix,distance_map,is_close,angle)
        follow(enemy_players,is_close,angle,distance,reference_real_position,player_real_position,map_image_copy,matrix,distance_map)
    elif(decision == "shoot and collect"):
        can_shoot = shoot(enemy_players,reference_real_position,player_real_position,map_image_copy,matrix,distance_map,is_close,angle)
        collect(map_image_copy,matrix,distance_map,angle,distance)
    elif(decision == "shoot and heal"):
        can_shoot = shoot(enemy_players,reference_real_position,player_real_position,map_image_copy,matrix,distance_map,is_close,angle)
        heal(map_image_copy,matrix,is_close,distance_map,angle,distance)
    elif(decision == "shoot and evade"):
        can_shoot = shoot(enemy_players,reference_real_position,player_real_position,map_image_copy,matrix,distance_map,is_close,angle)
        heal(map_image_copy,matrix,is_close,distance_map,angle,distance)
    else:
        return
   
def shoot(enemy_players, reference_real_position, player_real_position, map_image_copy, matrix, distance_map,is_close,angle):
    print("shoot 1")
    enemy_players = sorted(enemy_players, key=lambda x: x[1])
    print("shoot 2")
    for position, distance in enemy_players:
        if reference_real_position and player_real_position:
            print("shoot 3")
            scale_factors = calculate_scale_factors(reference_real_position, player_real_position,
                                                    (0, 0), (400, 300))
            print("shoot 4")
            real_position = pixel_to_real_position((position[0], position[1]), reference_real_position, scale_factors)
            print("shoot 5")
            write_enemy_real(real_position,common_path)
            print("shoot 6")        
        try:
            path, player_map_position = find_path("battle", map_image_copy, matrix, distance_map)
            print("shoot 7")
            is_clear_bool = is_clear(matrix, player_map_position)
            print("shoot 8")
            if is_clear_bool:
                stop_movement()
                print("shoot 9")
                mouse.position = (position[0],position[1])
                # Simulate pressing and releasing space key
                time.sleep(0.01)
                keyboard.press(Key.space)
                time.sleep(0.01)
                keyboard.release(Key.space)
                print("shoot 10")
                return True
            else:
                print("shoot 11")
                visualise_path(path,map_image_copy,player_map_position)
                print("shoot 12")
                move(is_close,angle,distance)
                print("shoot 13")
        except ValueError as e:
            print(f"Error in find_path: {e}")
            return False  # Handle the error case by returning False
    
            
def follow(enemy_players,is_close,angle,distance,reference_real_position,player_real_position,map_image_copy,matrix,distance_map):
    print("follow 1")
    position,distance = enemy_players[0]
    print("follow 2")
    if(reference_real_position and player_real_position):
        print("follow 3")
        scale_factors = calculate_scale_factors(reference_real_position, player_real_position,
                                            (0,0), (400,300))
        print("follow 4")
        real_position = pixel_to_real_position((position[0],position[1]), reference_real_position, scale_factors)
        print("follow 5")
        write_enemy_real(real_position,common_path)
        print("follow 6")
    if(distance > 190):
        print("follow 7")
        path,player_position = find_path("battle", map_image_copy, matrix, distance_map)
        print("follow 8")
        visualise_path(path,map_image_copy,player_position)
        print("follow 9")
        move(is_close,angle,distance)
        print("follow 10")
def collect(map_image_copy,matrix,distance_map,angle,distance):
    print("collect 1")
    path, player_position = find_path("collect",map_image_copy, matrix, distance_map)
    print("collect 2")
    visualise_path(path,map_image_copy,player_position)
    print("collect 3")
    move(False,angle,distance)
    print("collect 4")
    
def heal(map_image_copy,matrix,is_close,distance_map,angle,distance):
    print("heal 1")
    path,player_position = find_path("heal",map_image_copy,matrix,distance_map)
    print("heal 2")
    visualise_path(path,map_image_copy,player_position)
    print("heal 3")
    move(is_close,angle,distance)
    print("heal 4")

def traverse(map_image_copy, matrix, is_close, distance_map, angle, distance):
    print("traverse 1")
    path, player_position = find_path("traverse", map_image_copy, matrix, distance_map)
    print("path : ", path)
    print("traverse 2")
    print(player_position)
    
    # Check if path is empty or None
    if not path:
        print("No valid path found. Handling edge case...")
        # Handle this edge case appropriately, e.g., stop movement or take alternative action
        # For now, let's return from the function
        return
    
    visualise_path(path, map_image_copy, player_position)
    
    print("traverse 3")
    move(is_close, angle, distance)
    print("traverse 4")
    

def move(is_close,angle,distance):
    if is_close:
        stop_movement()
    else:
        if angle:
            rotation_keyboard(angle)
            follow_path(angle,distance)

def stop_movement():
    ReleaseKey(W)
    ReleaseKey(A)
    ReleaseKey(D)

def rotation_keyboard(angle):
    activate_game_window()

    if angle > 20:
        PressKey(D)
        ReleaseKey(A)
    elif angle < -20:
        PressKey(A)
        ReleaseKey(D)
    else:
        ReleaseKey(A)
        ReleaseKey(D)

def follow_path(angle,distance):
    if(distance > 0.2):
        PressKey(W)
    else:
        PressKey(W)
        time.sleep(0.2)
        ReleaseKey(W)


def process_handler(results, names, fps, frame):
    global decision, closest_coin, closest_health, player_position, reference_position, reference_pixel_position, enemy_players, is_close, angle, distance, previous_decision
    global last_succesful_coin,last_succesful_coin_nearby,last_succesful_health,last_succesful_enemy_count,last_succesful_teammate_count

    try:
        boxes = results[0].boxes.xyxy.tolist()
        classes = results[0].boxes.cls.tolist()
        confidences = results[0].boxes.conf.tolist()

        detections = list(zip(boxes, classes, confidences))
        detections.sort(key=lambda x: x[1] == 2, reverse=True)

        sorted_boxes = [box for box, cls, conf in detections]
        sorted_classes = [cls for box, cls, conf in detections]
        sorted_confidences = [conf for box, cls, conf in detections]

        selected_indices = non_max_suppression(np.array(sorted_boxes), np.array(sorted_confidences), threshold=0.9)
        filtered_boxes = [sorted_boxes[i] for i in selected_indices]
        filtered_classes = [sorted_classes[i] for i in selected_indices]
        filtered_confidences = [sorted_confidences[i] for i in selected_indices]

        decision = {"coins": [], "players": [], "healths": []}
        closest_objects = {"coin": None, "player": None, "health": None}
        min_distances = {"coin": float('inf'), "player": float('inf'), "health": float('inf')}

        for box, cls, confidence in zip(filtered_boxes, filtered_classes, filtered_confidences):
            x1, y1, x2, y2 = box
            label = names[cls]
            center_x, center_y = (x1 + x2) / 2, (y1 + y2) / 2

            if label == "coin":
                decision["coins"].append((center_x, center_y))
            elif label == "player":
                decision["players"].append((center_x, center_y, box))
            elif label == "health":
                decision["healths"].append((center_x, center_y))

        # Your player's location
        player_location = (400, 300)
        player_color = None
        other_players = []
        team_players = []
        enemy_players = []

        # Calculate distances for each player and determine if it's your player or not
        for player in decision["players"]:
            center_x, center_y, box = player
            player_center_distance = math.sqrt((center_x - player_location[0]) ** 2 + (center_y - player_location[1]) ** 2)
            if player_center_distance <= 35:
                player_color = extract_color(frame, box)
            else:
                other_players.append((player, player_center_distance))

        # Determine team and enemy players based on color similarity
        for other_player, distance in other_players:
            center_x, center_y, box = other_player
            other_player_color = extract_color(frame, box)

            if is_similar_color(player_color, other_player_color):
                team_players.append((other_player, distance))
            else:
                enemy_players.append((other_player, distance))

        # Debug prints
        print("Team Players:")
        for position, distance in team_players:
            print(f"Player at ({position[0]}, {position[1]}), Box: {position[2]}, Distance: {distance}")

        print("Enemy Players:")
        for position, distance in enemy_players:
            print(f"Player at ({position[0]}, {position[1]}), Box: {position[2]}, Distance: {distance}")

        # Calculate closest objects
        for box, cls, confidence in zip(filtered_boxes, filtered_classes, filtered_confidences):
            x1, y1, x2, y2 = box
            label = names[cls]
            center_x, center_y = (x1 + x2) / 2, (y1 + y2) / 2
            if player_location and label in closest_objects:
                distance = calculate_distance(player_location, (center_x, center_y))
                if closest_objects[label] is None:
                    min_distances[label] = distance
                    closest_objects[label] = (center_x, center_y)
                elif distance < min_distances[label]:
                    min_distances[label] = distance
                    closest_objects[label] = (center_x, center_y)
        filename_0_0 = common_path + '\\reference.txt'
        filename_400_300 = common_path + '\\player.txt'
        reference_position = read_real_position(filename_0_0)
        player_position = read_real_position(filename_400_300)
        if len(decision["coins"]) > 0:
            closest_coin = closest_objects["coin"]
            closest_health = closest_objects["health"]

            

            reference_pixel_position = (0, 0)
            player_pixel_position = (400, 300)

            closest_coin_800x600 = closest_coin

            if player_position and reference_position:
                scale_factors = calculate_scale_factors(reference_position, player_position, reference_pixel_position, player_pixel_position)
                real_position = pixel_to_real_position(closest_coin_800x600, reference_position, scale_factors)
                write_reference_real(real_position, common_path)

        for box, cls, confidence in zip(filtered_boxes, filtered_classes, filtered_confidences):
            x1, y1, x2, y2 = box
            label = names[cls]
            center_x, center_y = (x1 + x2) / 2, (y1 + y2) / 2
            line_thickness = 1.5

            if player_location:
                if label == "player":
                    color = COLORS["player"]
                else:
                    if label == "coin":
                        if closest_coin and (center_x, center_y) == closest_coin:
                            color = COLORS["closest"]
                        elif is_inside_circle(player_location, (center_x, center_y), CIRCLE_RADIUS):
                            color = COLORS["inside_circle"]
                        else:
                            color = COLORS.get(label, (0, 255, 255))
                    elif label == "health":
                        if closest_health and (center_x, center_y) == closest_health:
                            color = COLORS["closest"]
                        else:
                            color = COLORS.get(label, (0, 255, 255))
                    else:
                        color = COLORS.get(label, (0, 255, 255))

                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness=int(line_thickness))
                cv2.putText(frame, f'{label} {confidence:.2f}', (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, thickness=int(line_thickness))

                if player_location:
                    for coin_location in decision["coins"]:
                        if (center_x, center_y) == coin_location:
                            line_color = COLORS["closest"] if coin_location == closest_coin else color
                            cv2.line(frame, (int(player_location[0]), int(player_location[1])),
                                     (int(coin_location[0]), int(coin_location[1])), line_color, thickness=int(line_thickness))
                    for health_location in decision["healths"]:
                        if (center_x, center_y) == health_location:
                            line_color = COLORS["closest"] if health_location == closest_health else color
                            cv2.line(frame, (int(player_location[0]), int(player_location[1])),
                                     (int(health_location[0]), int(health_location[1])), line_color, thickness=int(line_thickness))

                    cv2.circle(frame, (int(player_location[0]), int(player_location[1])), CIRCLE_RADIUS, COLORS["inside_circle"], thickness=int(line_thickness))

        if player_location:
            player_rotation_degrees = angle_reader()
            target_point = read_movement_vector()
            pixel_coordinates = centered_to_pixel(target_point[0], target_point[1])

            if pixel_coordinates:
                direction_vector = np.array([pixel_coordinates[0] - player_location[0], player_location[1] - pixel_coordinates[1]])

                path_line_angle_adjusted_rad = np.deg2rad(path_line_angle) + np.deg2rad(player_rotation_degrees)
                end_x_path = int(player_location[0] + PATH_LINE_LENGTH * np.cos(path_line_angle_adjusted_rad))
                end_y_path = int(player_location[1] - PATH_LINE_LENGTH * np.sin(path_line_angle_adjusted_rad))

                cv2.line(frame, (int(player_location[0]), int(player_location[1])), (end_x_path, end_y_path), PATH_LINE_COLOR, thickness=PATH_LINE_THICKNESS)

                EXTENSION_FACTOR = 50
                extended_end_x = int(pixel_coordinates[0] + EXTENSION_FACTOR * direction_vector[0])
                extended_end_y = int(pixel_coordinates[1] + EXTENSION_FACTOR * direction_vector[1])

                cv2.line(frame, (pixel_coordinates[0], pixel_coordinates[1]), (extended_end_x, extended_end_y), PATH_LINE_COLOR, thickness=PATH_LINE_THICKNESS)

                angle = rotate_to_path_angle(player_location, (end_x_path, end_y_path), pixel_coordinates, (extended_end_x, extended_end_y))
                print("Angle to be rotated: ", angle)

                player_position_file = common_path + '\\player.txt'
                path_end_file = common_path + '\\goal.txt'
                print("A")
                distance = is_within_distance(player_position_file, path_end_file)
                print("B")

                is_close = distance < 1
                print("C")
                player_health = read_health(health_path) if os.path.exists(health_path) else last_succesful_health
                player_coin = read_coin(coin_path) if os.path.exists(coin_path) else last_succesful_coin
                enemy_count = len(enemy_players) if enemy_players is not None else last_succesful_enemy_count
                teammate_count = len(team_players) if team_players is not None else last_succesful_teammate_count
                coins_nearby = len(decision.get("coins", [])) > 0 if decision is not None else last_succesful_coin_nearby
                print("G")
                print(f"Player health: {player_health}")
                print(f"Player gold: {player_coin}")
                print(f"Enemy count: {enemy_count}")
                print(f"Teammate count: {teammate_count}")
                print(f"Coins nearby: {coins_nearby}")

            cv2.putText(frame, f'FPS: {fps:.1f}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), thickness=2)

        decision = decision_messenger(previous_decision, player_health, player_coin, enemy_count, teammate_count, coins_nearby)
        previous_decision = decision
        print(decision)
        print(previous_decision)
        print(enemy_players)
        print(is_close)
        print(angle)
        print(distance)
        print(reference_position)
        print(player_position)
        if decision is not None and enemy_players is not None and is_close is not None and angle is not None and distance is not None and reference_position is not None and player_position is not None:
            return decision, enemy_players, is_close, angle, distance, reference_position, player_position

    except Exception as e:
        print(f"An error occurred: {e}")
        return frame  # Return the frame unprocessed


def read_real_position(filename, max_retries=5, retry_delay=0.1):
    retries = 0
    while retries < max_retries:
        try:
            with open(filename, 'r') as file:
                line = file.readline().strip()
                # Extract coordinates from the line, assuming it's in the format "(-14.87, 11.77)"
                position = tuple(map(float, line[1:-1].split(', ')))  # remove parentheses and split by comma and space
            return position
        
        except (FileNotFoundError, IOError, ValueError) as e:
            print(f"Error reading position from {filename}: {e}")
            retries += 1
            if retries < max_retries:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)


def calculate_scale_factors(point1_real_position, point2_real_position, 
                            point1_pixel_position, point2_pixel_position):
    # Extract real positions
    x1, y1 = point1_real_position
    x2, y2 = point2_real_position
    
    # Extract pixel positions
    px1, py1 = point1_pixel_position
    px2, py2 = point2_pixel_position
    
    # Calculate distances in real units
    distance_x = x2 - x1
    distance_y = y2 - y1
    
    # Calculate distances in pixel units
    distance_px = px2 - px1
    distance_py = py2 - py1
    
    # Calculate scale factors
    scale_factor_x = distance_x / distance_px
    scale_factor_y = distance_y / distance_py
    
    return scale_factor_x, scale_factor_y

def pixel_to_real_position(pixel_position, point1_real_position, scale_factors):
    # Extract pixel position
    px, py = pixel_position
    
    # Extract scale factors
    scale_factor_x, scale_factor_y = scale_factors
    
    # Calculate real positions
    real_x = point1_real_position[0] + px * scale_factor_x
    real_y = point1_real_position[1] + py * scale_factor_y
    
    return real_x, real_y

def read_coordinates_from_file(filename):
    
    
    coord_pattern = re.compile(r'\(\s*([-+]?\d*\.?\d+)\s*,\s*([-+]?\d*\.?\d+)\s*\)')
    
    with open(filename, 'r') as file:
        for line in file:
            match = coord_pattern.search(line)
            if match:
                groups = match.groups()
                if len(groups) == 2:
                    x, y = map(float, groups)
                    return x, y
                else:
                    print(f"Error: Unexpected number of values in match groups: {groups}")
    
    # If no valid coordinates found, return None
    return None, None

def convert_coordinates(x, y):
    # Constants for the map sizes
    original_map_size = 400
    new_map_size = 100
    half_original_map = original_map_size / 2
    half_new_map = new_map_size / 2
    
    # Scale the coordinates
    scaled_x = x / (original_map_size / new_map_size)
    scaled_y = y / (original_map_size / new_map_size)
    
    # Translate the coordinates
    translated_x = scaled_x - half_new_map
    translated_y = half_new_map - scaled_y
    
    return translated_x, translated_y

last_player_position = None
last_path_end = None

def is_within_distance(player_position_file, path_end_file):
    global last_player_position, last_path_end

    # Attempt to read player position from file (already in 100x100)
    player_x, player_y = read_coordinates_from_file(player_position_file)

    # Attempt to read path end position from file (in 400x400)
    path_end_x, path_end_y = read_coordinates_from_file(path_end_file)

    # Update global variables with the latest successful reads
    if player_x is not None and player_y is not None:
        last_player_position = (player_x, player_y)
    else:
        player_x, player_y = last_player_position

    if path_end_x is not None and path_end_y is not None:
        last_path_end = (path_end_x, path_end_y)
    else:
        path_end_x, path_end_y = last_path_end

    # Convert path end coordinates to 100x100
    converted_x, converted_y = convert_coordinates(path_end_x, path_end_y)

    # Calculate the distance between player position and path end point
    distance = math.sqrt((converted_x - player_x) ** 2 + (converted_y - player_y) ** 2)


    # Check if the distance is less than the threshold
    return distance

def centered_to_pixel(x_centered, y_centered, window_width=800, window_height=600):
    # Calculate pixel coordinates
    pixel_x = int((x_centered + window_width / 2) * (window_width / window_width))
    pixel_y = int((-y_centered + window_height / 2) * (window_height / window_height))
    
    return pixel_x, pixel_y

def capture_game_window():
    """Capture the game window using PyAutoGUI."""
    try:
        game_window = np.array(pyautogui.screenshot(region=(GAME_WINDOW_X, GAME_WINDOW_Y, GAME_WINDOW_WIDTH, GAME_WINDOW_HEIGHT)))
        game_window = cv2.cvtColor(game_window, cv2.COLOR_BGR2RGB)
        return game_window
    except Exception as e:
        print(f"Error capturing game window: {e}")
        return None

def read_movement_vector():
    global last_successful_target_point
    file_path = common_path+'\\movement_vector.txt'
    try:
        with open(file_path, 'r') as file:
            for line in file:
                # Remove any leading or trailing whitespace and parentheses
                line = line.strip().strip('()')

                # Split the line into components and convert them to integers
                components = line.split(',')
                last_successful_target_point = tuple(int(component.strip()) for component in components if(component != ""))

    except (FileNotFoundError, IOError, ValueError) as e:
        print(f"Error reading angle from file: {e}")

    return last_successful_target_point

def rotate_to_path_angle(point1, end1, point2, end2):
    # Calculate direction vectors
    direction_vector1 = np.array([end1[0] - point1[0], end1[1] - point1[1]])
    direction_vector2 = np.array([end2[0] - point2[0], end2[1] - point2[1]])
    
    # Normalize direction vectors
    direction_vector1_norm = direction_vector1 / np.linalg.norm(direction_vector1)
    direction_vector2_norm = direction_vector2 / np.linalg.norm(direction_vector2)
    
    # Calculate angle between the two direction vectors in radians
    angle_rad = np.arccos(np.clip(np.dot(direction_vector1_norm, direction_vector2_norm), -1.0, 1.0))
    
    # Calculate cross product to determine the sign of the angle
    cross_product = np.cross(direction_vector1_norm, direction_vector2_norm)
    
    # Determine the signed angle in degrees
    angle_deg = np.rad2deg(angle_rad)
    if cross_product < 0:
        angle_deg = -angle_deg
    
    return angle_deg

SendInput = ctypes.windll.user32.SendInput

W = 0x11
A = 0x1E
D = 0x20
SPACE = 0x39

# C struct redefinitions
PUL = ctypes.POINTER(ctypes.c_ulong)
class KeyBdInput(ctypes.Structure):
    _fields_ = [
        ("wVk", ctypes.c_ushort),
        ("wScan", ctypes.c_ushort),
        ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", PUL)
    ]

class HardwareInput(ctypes.Structure):
    _fields_ = [
        ("uMsg", ctypes.c_ulong),
        ("wParamL", ctypes.c_short),
        ("wParamH", ctypes.c_ushort)
    ]

class MouseInput(ctypes.Structure):
    _fields_ = [
        ("dx", ctypes.c_long),
        ("dy", ctypes.c_long),
        ("mouseData", ctypes.c_ulong),
        ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", PUL)
    ]

class Input_I(ctypes.Union):
    _fields_ = [
        ("ki", KeyBdInput),
        ("mi", MouseInput),
        ("hi", HardwareInput)
    ]

class Input(ctypes.Structure):
    _fields_ = [
        ("type", ctypes.c_ulong),
        ("ii", Input_I)
    ]

def PressKey(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput(0, hexKeyCode, 0x0008, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(1), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

def ReleaseKey(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput(0, hexKeyCode, 0x0008 | 0x0002, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(1), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

# Key checking function
keyList = ['A', 'D', 'W', 'Space']

def key_check():
    keys = []
    for key in keyList:
        if wapi.GetAsyncKeyState(ord(key)):
            keys.append(key)
    return keys

# Function to activate game window (adjust as needed)
def activate_game_window():
    game_window_title = "Unity Multiplayer"  # Replace with actual game window title
    game_window = pyautogui.getWindowsWithTitle(game_window_title)[0]
    game_window.activate()
# Create a named window for object detection
cv2.namedWindow('Object Detection', cv2.WINDOW_NORMAL)


closest_coin = None
closest_health = None

# Initialize variables
frame_count = 0
start_time = time.time()
last_displayed_fps = 0.0
update_threshold_percent = 10

map_image, map_image_copy = get_map(file_paths['map'])
matrix, distance_map = get_matrix(map_image,True,True)
import cProfile
import pstats
import cv2
import time

def profile_code():
    global frame_count, start_time, last_displayed_fps
    frame_count = 0
    start_time = time.time()
    last_displayed_fps = 0.0
    update_threshold_percent = 5  # Adjust this threshold as needed

    profiler = cProfile.Profile()
    profiler.enable()

    try:
        while True:
            try:
                key = cv2.waitKey(1)
                
                if key == ord('q'):  # Press 'q' to quit
                    break

                start_capture = time.time()
                frame = capture_game_window()
                end_capture = time.time()

                if frame is not None:
                    start_detection = time.time()
                    results = model(frame, conf=0.45, save=True)
                    end_detection = time.time()
                        
                    start_processing = time.time()
                    frame_count += 1
                    current_time = time.time()
                    fps = frame_count / (current_time - start_time)
                        
                    # Update displayed FPS if the difference exceeds the threshold
                    if abs(fps - last_displayed_fps) > (update_threshold_percent / 100 * fps):
                        last_displayed_fps = fps
                            
                        # Draw FPS on the frame
                        cv2.putText(frame, f'FPS: {fps:.1f}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), thickness=2)

                    decision, enemy_players, is_close, angle, distance, reference_position, player_position = process_handler(results, model.names, fps, frame)
                 
                    if decision is not None:
                        action_handler(decision, enemy_players, is_close, angle, distance, reference_position, player_position, map_image_copy, matrix, distance_map)
              
                    end_processing = time.time()

                    cv2.imshow('Object Detection', frame)
            
            except KeyboardInterrupt:
                break
            except PermissionError as pe:
                print(f"PermissionError: {pe}")
                continue  # Skip this frame and continue
            except Exception as e:
                print(f"An error occurred: {e}")
                continue  # Skip this frame and continue
    finally:
        profiler.disable()
        with open('profiling_results.txt', 'w') as f:
            stats = pstats.Stats(profiler, stream=f)
            stats.sort_stats(pstats.SortKey.TIME)
            stats.print_stats()

        cv2.destroyAllWindows()

# Call the profiling function
profile_code()