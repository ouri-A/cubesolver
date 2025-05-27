import cv2
import numpy as np

multiplier = 7

# Configuration
GRID_SIZE_RATIO = 0.5  # Size of grid relative to webcam frame (50%)
INNER_SIZE_RATIO = 0.5  # Size of inner square relative to grid cell (50%)

# Initialize webcam
cap = cv2.VideoCapture(0)

# Color order for calibration
COLOR_ORDER = ["white", "red", "blue", "green", "orange", "yellow"]
color_samples = {color: [] for color in COLOR_ORDER}
current_color_idx = 0

def draw_grid(frame):
    """Draw smaller 3x3 grid with inner sampling squares"""
    h, w = frame.shape[:2]
    grid_size = int(min(h, w) * GRID_SIZE_RATIO)  # Scale down grid size
    offset_x = (w - grid_size) // 2  # Center grid horizontally
    offset_y = (h - grid_size) // 2  # Center grid vertically
    cell_size = grid_size // 3
    
    # Draw outer grid lines
    for i in range(1, 3):
        cv2.line(frame, (offset_x, offset_y + i * cell_size),
                (offset_x + grid_size, offset_y + i * cell_size),
                (0, 255, 0), 2)
        cv2.line(frame, (offset_x + i * cell_size, offset_y),
                (offset_x + i * cell_size, offset_y + grid_size),
                (0, 255, 0), 2)
    
    # Draw inner sampling squares
    inner_size = int(cell_size * INNER_SIZE_RATIO)
    inner_offset = (cell_size - inner_size) // 2
    for i in range(3):
        for j in range(3):
            if i == 1 and j == 1:  # Skip the center piece
                continue
            x_start = offset_x + j * cell_size + inner_offset
            y_start = offset_y + i * cell_size + inner_offset
            x_end = x_start + inner_size
            y_end = y_start + inner_size
            cv2.rectangle(frame,
                        (x_start, y_start),
                        (x_end, y_end),
                        (0, 0, 255),  # Red color for inner square
                        thickness=2)
    return frame

def get_grid_cells(frame):
    """Extract LAB colors from smaller inner squares in the flipped grid"""
    h, w = frame.shape[:2]
    grid_size = int(min(h, w) * GRID_SIZE_RATIO)
    offset_x = (w - grid_size) // 2
    offset_y = (h - grid_size) // 2
    cell_size = grid_size // 3
    inner_size = int(cell_size * INNER_SIZE_RATIO)
    inner_offset = (cell_size - inner_size) // 2
    cells = []
    
    for i in range(3):
        for j in range(3):
            if i == 1 and j == 1:  # Skip the center piece
                continue
            y_start = offset_y + i * cell_size + inner_offset
            x_start = offset_x + j * cell_size + inner_offset
            y_end = y_start + inner_size
            x_end = x_start + inner_size
            
            # Extract pixels from the smaller square
            inner_cell = frame[y_start:y_end, x_start:x_end]
            
            # Convert to LAB and compute average color
            lab_cell = cv2.cvtColor(inner_cell, cv2.COLOR_BGR2LAB)
            avg_lab = np.mean(lab_cell.reshape(-1, 3), axis=0)
            cells.append(avg_lab)
    
    return cells

def calculate_ranges(samples):
    """Calculate LAB ranges from samples and store mean values"""
    ranges = {}
    
    for color, values in samples.items():
        if values:
            arr = np.array(values)
            mean = np.mean(arr, axis=0)
            std = np.std(arr, axis=0)
            lower = np.clip(mean - std * multiplier, 0, 255).astype(int)
            upper = np.clip(mean + std * multiplier, 0, 255).astype(int)
            ranges[color] = {
                "lower": lower.tolist(),
                "upper": upper.tolist(),
                "mean": mean.tolist()  # Store mean values for reference
            }
    
    return ranges

# Calibration process
print("Starting calibration...")

while current_color_idx < len(COLOR_ORDER):
    color = COLOR_ORDER[current_color_idx]
    print(f"\nPlace {color} face in the smaller flipped grid and press 'c' when ready (q to quit)")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Unable to read frame from webcam.")
            break
        
        # Flip the frame horizontally to avoid mirroring effect
        flipped_frame = cv2.flip(frame.copy(), 1)
        
        # Draw the grid on the flipped frame
        frame_with_grid = draw_grid(flipped_frame.copy())
        
        cv2.putText(frame_with_grid,
                   f"Calibrating: {color}",
                   (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX,
                   1,
                   (0, 255, 0),
                   thickness=2)
        
        cv2.imshow("Calibration", frame_with_grid)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('c'):
            cells = get_grid_cells(flipped_frame)  # Use flipped frame for sampling LAB values
            color_samples[color].extend(cells)
            current_color_idx += 1
            break
        elif key == ord('q'):
            print("Calibration aborted.")
            cap.release()
            cv2.destroyAllWindows()
            exit()

cap.release()
cv2.destroyAllWindows()

# Calculate final ranges
COLOR_RANGES = calculate_ranges(color_samples)

# Export ranges to file
if COLOR_RANGES:
    with open("calibrated.py", "w") as f:
        f.write("COLOR_RANGES = {\n")
        for color, ranges in COLOR_RANGES.items():
            f.write(f'    "{color}": {{\n')
            f.write(f'        "lower": {ranges["lower"]},\n')
            f.write(f'        "upper": {ranges["upper"]},\n')
            f.write(f'        "mean": {ranges["mean"]}\n')
            f.write('    },\n')
        f.write("}\n")
    print("Calibration complete! Ranges saved to calibrated.py")
else:
    print("Calibration failed - no data collected.")
