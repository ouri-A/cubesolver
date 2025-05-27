# CUBESOLVER

This project is an autonomous Rubik's cube-solving robot that uses computer vision to detect the cube's state and stepper motors controlled by ESP32 microcontrollers to execute the solution.

## how to use :

1.  **calibrate all the colors (only needs to be done once):**
    *   run calibrate.py and follow the instructions on screen show a solved cubes faces one by one

2.  **test calibration(only needs to be done once):**
    *   run testCalibrated.py
    *   check the calibration of colors , place the cube in the grid on the screen add the colors being read will be shown on the screen for every peice

3.  **read unsolved state :**
    *   now scramble the cube as desiered
    *   run readState.py
    *   scan the whole cube by following the instructions on the screen
    *   once done the solution string will be updated in rubics\_solution.py

4.  **execution put the cube in the bot:**
    *   run send\_to\_esp.py
    *   the bot will solve the cube


## How It Works  
1. **Calibration** – The system dynamically samples color ranges using the **LAB color space**, ensuring consistent detection under different lighting conditions.  
2. **State Detection** – Using **OpenCV**, the solver scans all cube faces and extracts the current cube state.  
3. **Solution Execution** – The **Kociemba algorithm** calculates the optimal solution, which is then executed by the robotic mechanism.  

## Features  
- Real-time color calibration for accurate cube recognition  
- Efficient state extraction using advanced computer vision techniques  
- Optimized move sequence generation for fast and effective solving  
## Project Context and Future Potential

This iteration of the project was developed under significant budget constraints. To manage costs:
*   Cost-effective motors were utilized.
*   The use of 3D-printed parts was minimized to reduce printing expenses.

Currently, the process involves manual scanning of the cube by placing it in front of a webcam, followed by manual placement into the solver mechanism.

**Future Enhancements (with increased budget):**
With adequate funding, this system has the potential to be upgraded into a fully autonomous cube solver capable of:
*   Solving the cube in under 5 seconds.
*   Performing all operations, including calibration, scanning, and execution, without human intervention.
The primary limiting factors to achieving this are the current motor specifications and the extent of 3D-printed mechanical components.



---
