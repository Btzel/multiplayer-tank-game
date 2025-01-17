import pyautogui
import numpy as np
import cv2
import time
import keyboard

# Game window position and size
GAME_WINDOW_X = 0
GAME_WINDOW_Y = 0
GAME_WINDOW_WIDTH = 800
GAME_WINDOW_HEIGHT = 600

def capture_game_frame():
    # Capture screenshot of game window
    screenshot = pyautogui.screenshot(region=(GAME_WINDOW_X, GAME_WINDOW_Y, GAME_WINDOW_WIDTH, GAME_WINDOW_HEIGHT))
    
    # Convert screenshot to OpenCV format (BGR color)
    frame = np.array(screenshot)
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    
    return frame

if __name__ == "__main__":
    # Output directory for saving captured frames
    output_dir = 'Dataset/'
    
    # Create output directory if it doesn't exist
    import os
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Number of frames to capture
    num_frames = 100  # Adjust as needed
    
    print("Press 'b' to start capturing frames.")
    print("Press 'h' to stop capturing frames.")
    
    capturing = False
    frame_count = 0
    
    try:
        while True:
            if keyboard.is_pressed('b'):
                capturing = True
                print("Started capturing frames...")
            
            if capturing:
                # Capture frame
                frame = capture_game_frame()
                
                # Save frame with unique filename
                filename = f'{output_dir}/frame_{frame_count}.png'
                cv2.imwrite(filename, frame)
                
                print(f"Captured frame {frame_count}")
                frame_count += 1
                time.sleep(2)  # Adjust delay as needed
            
            if keyboard.is_pressed('h'):
                if capturing:
                    print(f"Stopped capturing frames. Captured {frame_count} frames.")
                else:
                    print("Capture was not started.")
                break
    
    except KeyboardInterrupt:
        print("\nFrame capturing stopped by user.")