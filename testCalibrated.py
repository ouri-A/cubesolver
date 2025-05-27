import cv2
import numpy as np
from calibrated import COLOR_RANGES

def detect_color(lab_pixels):
    """Identify color using distance from calibrated means"""
    avg_lab = np.mean(lab_pixels, axis=0)
    
    # Calculate distance to each reference color
    distances = {}
    for color_name, ranges in COLOR_RANGES.items():
        ref_color = np.array(ranges["mean"])
        # Euclidean distance in LAB space
        distance = np.linalg.norm(avg_lab - ref_color)
        distances[color_name] = distance
    
    # Find the closest match
    closest_color = min(distances, key=distances.get)
    
    return closest_color[0].upper()  # Return first letter (R/G/B/etc)

# Webcam and grid settings
GRID_SIZE_RATIO = 0.5
INNER_SIZE_RATIO = 0.5

cap = cv2.VideoCapture(0)

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        # Flip frame to remove mirror effect
        frame = cv2.flip(frame, 1)
        h, w = frame.shape[:2]
        
        # Calculate grid parameters
        grid_size = int(min(h, w) * GRID_SIZE_RATIO)
        offset_x = (w - grid_size) // 2
        offset_y = (h - grid_size) // 2
        cell_size = grid_size // 3
        inner_size = int(cell_size * INNER_SIZE_RATIO)
        inner_offset = (cell_size - inner_size) // 2
        
        # Process each grid cell (skip center)
        for i in range(3):
            for j in range(3):
                if i == 1 and j == 1:  # Skip center piece
                    continue
                
                # Get cell coordinates
                x_start = offset_x + j*cell_size + inner_offset
                y_start = offset_y + i*cell_size + inner_offset
                x_end = x_start + inner_size
                y_end = y_start + inner_size
                
                # Extract cell pixels
                cell = frame[y_start:y_end, x_start:x_end]
                lab_cell = cv2.cvtColor(cell, cv2.COLOR_BGR2LAB)
                lab_pixels = lab_cell.reshape(-1, 3)  # Flatten to pixel list
                
                # Detect color using distance-based method
                color = detect_color(lab_pixels)
                
                # Draw cell border and label
                cv2.rectangle(frame, (x_start, y_start), (x_end, y_end), (0,0,0), 2)
                cv2.putText(frame, color, 
                          (x_start+10, y_start+30), 
                          cv2.FONT_HERSHEY_SIMPLEX, 1, 
                          (147,20,255), 2)

        # Draw outer grid
        cv2.rectangle(frame, 
                     (offset_x, offset_y), 
                     (offset_x+grid_size, offset_y+grid_size), 
                     (0,255,0), 2)
        
        cv2.imshow("Rubik's Cube Color Check", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except Exception as e:
    print(f"Error: {e}")
finally:
    cap.release()
    cv2.destroyAllWindows()
