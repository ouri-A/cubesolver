import requests

# Configuration (Update these with your ESP32 IPs)
MAIN_IP = "192.168.129.61"  # L, R, F, B controller
UD_IP = "192.168.129.250"     # U, D controller

def send_move(move):
    """Send move to appropriate ESP32"""
    try:
        # Determine target ESP based on move
        if move[0].upper() in {'U', 'D'}:
            url = f"http://{UD_IP}/command"
        else:
            url = f"http://{MAIN_IP}/command"
        
        response = requests.post(
            url,
            data=move,
            headers={"Content-Type": "text/plain"},
            timeout=30
        )
        return response.text
        
    except requests.exceptions.RequestException as e:
        return f"Error: {str(e)}"

def validate_move(move):
    """Check if move format is valid"""
    if not move:
        return False
    if move[0].upper() not in {'U', 'D', 'L', 'R', 'F', 'B'}:
        return False
    if len(move) > 1:
        if move[1] not in {'\'', '2'} or len(move) > 2:
            return False
    return True

def manual_control():
    print("Rubik's Cube Manual Controller")
    print("Enter moves (e.g., U, R', F2) or 'exit' to quit")
    print("Connected ESPs:")
    print(f"- Main Controller (L/R/F/B): {MAIN_IP}")
    print(f"- U/D Controller: {UD_IP}\n")
    
    while True:
        move = input("Enter move: ").strip().upper()
        
        if move == "EXIT":
            print("Exiting...")
            break
            
        if not validate_move(move):
            print("Invalid move! Valid examples: U, R', F2, B")
            continue
            
        result = send_move(move)
        print(f"ESP32 Response: {result}")

if __name__ == "__main__":
    manual_control()
