# Project-Numera-Quest-Kingdom-of-Math-Runes
A retro-inspired math adventure where kids use camera-based finger input to solve challenges and save the Kingdom with Arduino UNO Q.  
  
<img src="/Images/Numera-Quest-thm.jpg" height="200">  
    
Numera Quest: Kingdom of Math Runes is an interactive math-adventure game built around the Arduino UNO Q. The idea is to turn simple arithmetic into an exploration-based game where the player travels through three different worlds—Number Forest, Crystal Caverns, and Number Temple—and solves a math challenge at the end of each quest. Instead of entering the answer using a keyboard or touchscreen, the player simply shows the answer using their fingers in front of a camera. This combines game interaction with an AI-based vision system.

The system uses UNO Q's Linux/MPU side for the main PyGame application, handling the game world, player movement, collision detection, game state, quests and progression. Arduino App Lab runs alongside it and handles the Video Image Classification Brick for finger detection, the Sound Generator Brick for voice and sound effects, and Arduino Bridge for communicating with the UNO Q's STM32U585 and its onboard 8×13 LED matrix. The PyGame application and App Lab communicate through UDP on port 5005. A Logitech C270 webcam captures the player's hand, App Lab classifies the gesture as one to five fingers, and sends the result back to the game. The game stabilizes the detection before accepting it as an answer.

The game flow is simple: explore → reach the QUEST marker → press A → hear the challenge → show the answer with your fingers → get immediate feedback. A correct answer completes the quest and unlocks the next world, while an incorrect answer consumes one of three attempts and provides audio feedback. After completing all three quests, the player reaches the final victory screen, showing that the Kingdom of Numbers is safe, with options to Play Again or Exit.
