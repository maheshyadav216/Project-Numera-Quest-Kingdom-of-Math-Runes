# Project - Numera Quest : Kingdom of Math Runes
A retro-inspired math adventure where kids use camera-based finger input to solve challenges and save the Kingdom with Arduino UNO Q.  
  
<img src="/Images/Numera-Quest-thm.jpg" height="200">  
    
Numera Quest: Kingdom of Math Runes is an interactive math-adventure game built around the Arduino UNO Q. The idea is to turn simple arithmetic into an exploration-based game where the player travels through three different worlds—Number Forest, Crystal Caverns, and Number Temple—and solves a math challenge at the end of each quest. Instead of entering the answer using a keyboard or touchscreen, the player simply shows the answer using their fingers in front of a camera. This combines game interaction with an AI-based vision system.

The system uses UNO Q's Linux/MPU side for the main PyGame application, handling the game world, player movement, collision detection, game state, quests and progression. Arduino App Lab runs alongside it and handles the Video Image Classification Brick for finger detection, the Sound Generator Brick for voice and sound effects, and Arduino Bridge for communicating with the UNO Q's STM32U585 and its onboard 8×13 LED matrix. The PyGame application and App Lab communicate through UDP on port 5005. A Logitech C270 webcam captures the player's hand, App Lab classifies the gesture as one to five fingers, and sends the result back to the game. The game stabilizes the detection before accepting it as an answer.

The game flow is simple: explore → reach the QUEST marker → press A → hear the challenge → show the answer with your fingers → get immediate feedback. A correct answer completes the quest and unlocks the next world, while an incorrect answer consumes one of three attempts and provides audio feedback. After completing all three quests, the player reaches the final victory screen, showing that the Kingdom of Numbers is safe, with options to Play Again or Exit.  
  
------------------------------------------------------------------------------------------------------

## BOM / Components

The following Bill of Materials lists the hardware components used to build and demonstrate Numera Quest  

**Hardware** 🛠️  
- Arduino UNO Q — 1 — Main computing and embedded platform
- Multiport USB-C Hub — 1 — Peripheral connectivity and expansion
- HDMI Monitor — 1 — Main game display
- Logitech C270 USB Webcam — 1 — Camera-based finger interaction
- Wireless Gamepad / Joypad — 1 — Primary gameplay controller
- Keyboard — 1 — Development and auxiliary operation
- Mouse — 1 — Development and auxiliary operation
- External Speakers with 3.5 mm input — 2 — Voice prompts, music and sound effects
- 5V/4A Power Adapter — 1 — External power for the USB-C hub
- Ethernet Cable — 1 — Wired network connection

**Software & Tools** 🖥️
- Arduino App Lab — AI, audio and Arduino Bridge integration, STM32U585 MCU development
- PyGame — Main game engine and rendering
- Edge Impulse — Finger-recognition model development and training
- Python — PyGame and App Lab applications

  
## Documentation

- Refer the [Documentation website](https://docs.arduino.cc/hardware/uno-q/) for more information.  
- Arduino UNO Q [User Guide](https://docs.arduino.cc/tutorials/uno-q/user-manual/)  
- Arduino UNO Q [Launch Page](https://www.arduino.cc/product-uno-q/)  

------------------------------------------------------------------------------------------------------

📕 **YouTube Video Links**  
  
▶️  Camera-Based Finger Recognition with Edge Impulse 🔗 https://youtu.be/K7Qo9uM6nGU   
  
▶️  Project - Numera Quest: Kingdom of Math Runes - 🔗 https://youtu.be/jCOB4jtAcek  

------------------------------------------------------------------------------------------------------

📜 Source Code, Circuit Diagrams and Documentation : 

🌐 GitHub Repository - 🔗 https://github.com/maheshyadav216/Project-Numera-Quest-Kingdom-of-Math-Runes     
  
🌐 Hackster Blog -  
🔗 https://www.hackster.io/maheshyadav216/numera-quest-kingdom-of-math-runes-bba48f 

-------------------------------------------------------------------------------------------------------
📒 **Important Links**  
 
📖 UNO Q User Manual :🔗 https://docs.arduino.cc/tutorials/uno-q/user-manual/    
💾 Arduino Docs : 🔗 https://docs.arduino.cc/hardware/uno-q/  

📌 Arduino UNO Q Accessories :  🔗 https://blog.make2explore.com/arduino-drops-seven-fresh-accessories-to-supercharge-the-uno-q/   

🛒  Purchase  -   
Arduino® UNO™ Q 4GB  : 🔗 https://store-usa.arduino.cc/products/uno-q-4gb  
Arduino® UNO™ Q 2GB  : 🔗 https://store-usa.arduino.cc/products/uno-q-2gb  

Product page :  🔗 https://www.arduino.cc/product-uno-q/   

------------------------------------------------------------------------------------------------------
  

[![CC BY-NC-SA 4.0][cc-by-nc-sa-shield]][cc-by-nc-sa]

This work is licensed under a
[Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License][cc-by-nc-sa].

[![CC BY-NC-SA 4.0][cc-by-nc-sa-image]][cc-by-nc-sa]

[cc-by-nc-sa]: http://creativecommons.org/licenses/by-nc-sa/4.0/
[cc-by-nc-sa-image]: https://licensebuttons.net/l/by-nc-sa/4.0/88x31.png
[cc-by-nc-sa-shield]: https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg
