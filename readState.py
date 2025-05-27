import cv2
import numpy as np
from calibrated import COLOR_RANGES

def overwrite_centers(cube_state):
    FACE_ORDER_SCAN = ["F", "L", "B", "R", "U", "D"]
    corrected_cube_state = list(cube_state)
    for i, face_letter in enumerate(FACE_ORDER_SCAN):
        corrected_cube_state[i * 9 + 4] = face_letter
    return "".join(corrected_cube_state)

FACE_ORDER_SCAN = ["F", "L", "B", "R", "U", "D"]
COLOR_TO_FACE = {
    "yellow": "F",
    "red": "L",
    "white": "B",
    "orange": "R",
    "blue": "U",
    "green": "D"
}

FACE_TO_COLOR = {v: k[0].upper() for k, v in COLOR_TO_FACE.items()}
COLOR_LETTER_TO_FACE = {
    "Y": "F",
    "R": "L",
    "W": "B",
    "O": "R",
    "B": "U",
    "G": "D"
}

GRID_SIZE_RATIO = 0.5
INNER_SIZE_RATIO = 0.5

def draw_grid(frame, detected_colors=None, center_color_letter=None):
    h, w = frame.shape[:2]
    grid_size = int(min(h, w) * GRID_SIZE_RATIO)
    offset_x = (w - grid_size) // 2
    offset_y = (h - grid_size) // 2
    cell_size = grid_size // 3
    
    cv2.rectangle(frame, (offset_x, offset_y), (offset_x+grid_size, offset_y+grid_size), (0,255,0), 2)
    
    inner_size = int(cell_size * INNER_SIZE_RATIO)
    inner_offset = (cell_size - inner_size) // 2
    for i in range(3):
        for j in range(3):
            x_start = offset_x + j * cell_size + inner_offset
            y_start = offset_y + i * cell_size + inner_offset
            x_end = x_start + inner_size
            y_end = y_start + inner_size
            cv2.rectangle(frame, (x_start, y_start), (x_end, y_end), (0, 0, 0), 2)
            if i == 1 and j == 1:
                cv2.putText(frame, center_color_letter,
                          (x_start + 10, y_start + inner_size // 2),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
            elif detected_colors:
                color_letter = detected_colors[i * 3 + j]
                cv2.putText(frame, color_letter,
                          (x_start + 10, y_start + inner_size // 2),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

def detect_color(cell):
    """Identify color using distance from calibrated means"""
    lab = cv2.cvtColor(cell, cv2.COLOR_BGR2LAB)
    avg_lab = np.mean(lab.reshape(-1, 3), axis=0)
    
    # Calculate distance to each reference color
    distances = {}
    for color, ranges in COLOR_RANGES.items():
        ref_color = np.array(ranges["mean"])
        # Euclidean distance in LAB space
        distance = np.linalg.norm(avg_lab - ref_color)
        distances[color] = distance
    
    # Find the closest match
    closest_color = min(distances, key=distances.get)
    
    return closest_color[0].upper()

def scan_cube():
    cap = cv2.VideoCapture(0)
    cube_state = []
    
    try:
        for face_letter in FACE_ORDER_SCAN:
            center_color_letter = FACE_TO_COLOR[face_letter]
            while True:
                ret, frame = cap.read()
                if not ret: break
                
                flipped_frame = cv2.flip(frame, 1)
                preview_frame = flipped_frame.copy()
                detected_colors_preview = []
                h, w = flipped_frame.shape[:2]
                grid_size = int(min(h, w) * GRID_SIZE_RATIO)
                offset_x = (w - grid_size) // 2
                offset_y = (h - grid_size) // 2
                cell_size = grid_size // 3
                inner_size = int(cell_size * INNER_SIZE_RATIO)
                inner_offset = (cell_size - inner_size) // 2
                
                for i in range(3):
                    for j in range(3):
                        if i == 1 and j == 1:
                            detected_colors_preview.append(center_color_letter)
                            continue
                        y_start = offset_y + i * cell_size + inner_offset
                        x_start = offset_x + j * cell_size + inner_offset
                        cell_roi = flipped_frame[y_start:y_start+inner_size, x_start:x_start+inner_size]
                        detected_colors_preview.append(detect_color(cell_roi))
                
                draw_grid(preview_frame, detected_colors_preview, center_color_letter)
                cv2.putText(preview_frame, f"Press 'c' to capture this face", (10, 30),
                          cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.imshow("Rubik's Cube Scanner", preview_frame)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord('c'):
                    facelet_order = [2,1,0,5,4,3,8,7,6]
                    rearranged_colors = [detected_colors_preview[i] for i in facelet_order]
                    cube_state.append("".join([
                        COLOR_LETTER_TO_FACE.get(color.upper(), "X")
                        for color in rearranged_colors
                    ]))
                    break

        stateString = "".join([cube_state[FACE_ORDER_SCAN.index(f)] for f in ["U","R","F","D","L","B"]])
        stateString = overwrite_centers(stateString)
        return stateString

    except KeyboardInterrupt:
        return None
    finally:
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    print("Rubik's Cube Scanner")
    print("Follow the instructions to scan each face of the cube.")
    cube_state_string = scan_cube()
    
    if cube_state_string:
        print("\nCube state string generated successfully!")
        print(f"Kociemba input: {cube_state_string}")
        try:
            import kociemba
            solution = kociemba.solve(cube_state_string)
            print("\nSolution:", solution)
            with open("rubiks_solution.py", "w") as f:
                f.write(f'solution = "{solution}"\n')
            print("Solution saved to rubiks_solution.py")
        except ImportError:
            print("\nError: Install kociemba first - 'pip install kociemba'")
        except Exception as e:
            print("\nError during solving:", str(e))
