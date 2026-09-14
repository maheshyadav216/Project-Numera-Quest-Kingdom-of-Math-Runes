//=============================================================================//
// Project/Tutorial       - Numera Quest: Kingdom of Math Runes
// Device                 - Arduino UNO Q
// Author                 - https://www.hackster.io/maheshyadav216
// Hardware               - Arduino UNO Q  
// Software               - Arduino App Lab
// GitHub Repo of Project - https://github.com/maheshyadav216/Project-Numera-Quest-Kingdom-of-Math-Runes 
// Code last Modified on  - 14/09/2026
// Code/Content license   - (CC BY-NC-SA 4.0) https://creativecommons.org/licenses/by-nc-sa/4.0/
//============================================================================//

#include <Arduino_RouterBridge.h>
#include <Arduino_LED_Matrix.h>

ArduinoLEDMatrix matrix;

// ============================================================
// NUMERA QUEST
// UNO Q MCU SIDE
//
// 8 x 13 = 104 LEDs
//
// Commands exposed to Linux / App Lab:
//
//   move_up
//   move_down
//   move_left
//   move_right
//   button_a
//   button_b
//   game_pause
//   game_resume
//   game_idle
//
// The matrix displays the current game action.
// ============================================================

uint8_t frame[104];

// ============================================================
// HELPER: CLEAR FRAME
// ============================================================

void clearFrame()
{
  for (int i = 0; i < 104; i++)
  {
    frame[i] = 0;
  }
}

// ============================================================
// HELPER: SET PIXEL
// ============================================================

void setPixel(int row, int col)
{
  if (row < 0 || row >= 8)
    return;

  if (col < 0 || col >= 13)
    return;

  frame[row * 13 + col] = 1;
}

// ============================================================
// HELPER: DRAW FRAME
// ============================================================

void showFrame()
{
  matrix.draw(frame);
}

// ============================================================
// IDLE / PLAYER ICON
// ============================================================

void showIdle()
{
  clearFrame();

  // Head
  setPixel(1, 5);
  setPixel(1, 6);
  setPixel(1, 7);

  setPixel(2, 4);
  setPixel(2, 5);
  setPixel(2, 6);
  setPixel(2, 7);
  setPixel(2, 8);

  // Eyes
  frame[2 * 13 + 5] = 0;
  frame[2 * 13 + 7] = 0;

  // Body
  setPixel(3, 5);
  setPixel(3, 6);
  setPixel(3, 7);

  setPixel(4, 4);
  setPixel(4, 5);
  setPixel(4, 6);
  setPixel(4, 7);
  setPixel(4, 8);

  // Legs
  setPixel(5, 5);
  setPixel(5, 7);

  setPixel(6, 4);
  setPixel(6, 5);
  setPixel(6, 7);
  setPixel(6, 8);

  showFrame();
}

// ============================================================
// UP ARROW
// ============================================================

void showUp()
{
  clearFrame();

  // Arrow head
  setPixel(0, 6);

  setPixel(1, 5);
  setPixel(1, 6);
  setPixel(1, 7);

  setPixel(2, 4);
  setPixel(2, 5);
  setPixel(2, 6);
  setPixel(2, 7);
  setPixel(2, 8);

  // Shaft
  setPixel(3, 6);
  setPixel(4, 6);
  setPixel(5, 6);
  setPixel(6, 6);
  setPixel(7, 6);

  showFrame();
}

// ============================================================
// DOWN ARROW
// ============================================================

void showDown()
{
  clearFrame();

  // Shaft
  setPixel(0, 6);
  setPixel(1, 6);
  setPixel(2, 6);
  setPixel(3, 6);
  setPixel(4, 6);

  // Arrow head
  setPixel(5, 4);
  setPixel(5, 5);
  setPixel(5, 6);
  setPixel(5, 7);
  setPixel(5, 8);

  setPixel(6, 5);
  setPixel(6, 6);
  setPixel(6, 7);

  setPixel(7, 6);

  showFrame();
}

// ============================================================
// LEFT ARROW
// ============================================================

void showLeft()
{
  clearFrame();

  // Arrow head
  setPixel(3, 0);

  setPixel(2, 1);
  setPixel(3, 1);
  setPixel(4, 1);

  setPixel(1, 2);
  setPixel(2, 2);
  setPixel(3, 2);
  setPixel(4, 2);
  setPixel(5, 2);

  // Shaft
  for (int col = 3; col <= 12; col++)
  {
    setPixel(3, col);
  }

  showFrame();
}

// ============================================================
// RIGHT ARROW
// ============================================================

void showRight()
{
  clearFrame();

  // Shaft
  for (int col = 0; col <= 9; col++)
  {
    setPixel(3, col);
  }

  // Arrow head
  setPixel(3, 10);

  setPixel(1, 10);
  setPixel(2, 10);
  setPixel(4, 10);
  setPixel(5, 10);

  setPixel(2, 11);
  setPixel(3, 11);
  setPixel(4, 11);

  setPixel(3, 12);

  showFrame();
}

// ============================================================
// A BUTTON
//
//  ###
// #   #
// #   #
// #####
// #   #
// #   #
// #   #
//
// 7 rows x 5 columns
// ============================================================

void showA()
{
  clearFrame();

  // Row 0
  setPixel(0, 6);
  setPixel(0, 7);
  setPixel(0, 8);

  // Row 1
  setPixel(1, 5);
  setPixel(1, 9);

  // Row 2
  setPixel(2, 5);
  setPixel(2, 9);

  // Row 3
  setPixel(3, 5);
  setPixel(3, 6);
  setPixel(3, 7);
  setPixel(3, 8);
  setPixel(3, 9);

  // Row 4
  setPixel(4, 5);
  setPixel(4, 9);

  // Row 5
  setPixel(5, 5);
  setPixel(5, 9);

  // Row 6
  setPixel(6, 5);
  setPixel(6, 9);

  showFrame();
}

// ============================================================
// B BUTTON
//
// ####
// #   #
// #   #
// ####
// #   #
// #   #
// ####
//
// 7 rows x 5 columns
// ============================================================

void showB()
{
  clearFrame();

  // Row 0
  setPixel(0, 5);
  setPixel(0, 6);
  setPixel(0, 7);
  setPixel(0, 8);

  // Row 1
  setPixel(1, 5);
  setPixel(1, 9);

  // Row 2
  setPixel(2, 5);
  setPixel(2, 9);

  // Row 3
  setPixel(3, 5);
  setPixel(3, 6);
  setPixel(3, 7);
  setPixel(3, 8);

  // Row 4
  setPixel(4, 5);
  setPixel(4, 9);

  // Row 5
  setPixel(5, 5);
  setPixel(5, 9);

  // Row 6
  setPixel(6, 5);
  setPixel(6, 6);
  setPixel(6, 7);
  setPixel(6, 8);

  showFrame();
}

// ============================================================
// PAUSE ICON
//
// ||
// ||
// ||
// ||
// ============================================================

void showPause()
{
  clearFrame();

  for (int row = 1; row <= 6; row++)
  {
    setPixel(row, 4);
    setPixel(row, 8);
  }

  showFrame();
}

// ============================================================
// PLAY / RESUME ICON
// ============================================================

void showPlay()
{
  clearFrame();

  setPixel(1, 4);

  setPixel(2, 4);
  setPixel(2, 5);

  setPixel(3, 4);
  setPixel(3, 5);
  setPixel(3, 6);

  setPixel(4, 4);
  setPixel(4, 5);
  setPixel(4, 6);
  setPixel(4, 7);

  setPixel(5, 4);
  setPixel(5, 5);
  setPixel(5, 6);

  setPixel(6, 4);
  setPixel(6, 5);

  setPixel(7, 4);

  showFrame();
}

// ============================================================
// BRIDGE CALLBACKS
// ============================================================

void moveUp()
{
  showUp();
}

void moveDown()
{
  showDown();
}

void moveLeft()
{
  showLeft();
}

void moveRight()
{
  showRight();
}

void buttonA()
{
  showA();
}

void buttonB()
{
  showB();
}

void gamePause()
{
  showPause();
}

void gameResume()
{
  showPlay();
}

void gameIdle()
{
  showIdle();
}

// ============================================================
// SETUP
// ============================================================

void setup()
{
  // ----------------------------------------------------------
  // LED MATRIX
  // ----------------------------------------------------------

  matrix.begin();

  // 1-bit grayscale:
  // 0 = OFF
  // 1 = ON
  matrix.setGrayscaleBits(1);

  // ----------------------------------------------------------
  // ROUTER BRIDGE
  // ----------------------------------------------------------

  Bridge.begin();

  // ----------------------------------------------------------
  // GAME EVENTS
  // ----------------------------------------------------------

  Bridge.provide_safe("move_up", moveUp);
  Bridge.provide_safe("move_down", moveDown);
  Bridge.provide_safe("move_left", moveLeft);
  Bridge.provide_safe("move_right", moveRight);

  Bridge.provide_safe("button_a", buttonA);
  Bridge.provide_safe("button_b", buttonB);

  Bridge.provide_safe("game_pause", gamePause);
  Bridge.provide_safe("game_resume", gameResume);
  Bridge.provide_safe("game_idle", gameIdle);

  // ----------------------------------------------------------
  // INITIAL MATRIX STATE
  // ----------------------------------------------------------

  showIdle();
}

// ============================================================
// LOOP
// ============================================================

void loop()
{
  // RouterBridge handles incoming RPC requests.
}