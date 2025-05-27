

import requests
import time


MAIN_CONTROLLER_IP = "192.168.129.61"  # Handles L, R, F, B
UD_CONTROLLER_IP = "192.168.129.250"    # Handles U, D

def send_to_controller(move, controller_ip):
    try:
        response = requests.post(
            f"http://{controller_ip}/command",
            data=move,
            headers={"Content-Type": "text/plain"},
            timeout=30  # Increased timeout to 30 seconds
        )
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

def execute_solution():
    from rubiks_solution import solution
    moves = solution.strip().split()
    
    print(f"Executing {len(moves)} moves across two controllers:")
    print(f"Main Controller ({MAIN_CONTROLLER_IP}): L, R, F, B")
    print(f"U/D Controller ({UD_CONTROLLER_IP}): U, D\n")
    
    if input("Start execution? (yes/no): ").lower() != "yes":
        print("Aborted")
        return

    try:
        for idx, move in enumerate(moves, 1):
            print(f"{idx}/{len(moves)}: {move}")
            
            # Determine target controller
            if move[0].upper() in {'U', 'D'}:
                result = send_to_controller(move, UD_CONTROLLER_IP)
            else:
                result = send_to_controller(move, MAIN_CONTROLLER_IP)
            
            print(f"Response: {result}")
            # time.sleep(5)

        # Send completion to both controllers
        print("\nSending completion signals:")
        print("Main Controller:", send_to_controller("complete", MAIN_CONTROLLER_IP))
        print("U/D Controller:", send_to_controller("complete", UD_CONTROLLER_IP))
        
        print("\nSolution executed successfully!")
        
    except Exception as e:
        print(f"\nCritical error: {str(e)}")

if __name__ == "__main__":
    execute_solution()


