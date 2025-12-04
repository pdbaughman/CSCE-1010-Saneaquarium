# Fish Tank

A simple resizable aquarium game in Python using Pygame. Feed your fish, collect coins, and keep your aquatic friends alive!

---

## Members

Dalton Baughman
Gavin Johnson
Jackson Sloan

---

## Features

- **Resizable Window:** All assets and game logic scale to fit any window size.
- **Feed the Fish:** Click in the tank to drop food (costs money).
- **Collect Coins:** Fish periodically produce coins—click them to collect.
- **Buy More Fish:** Press `F` (with enough money) to add a new fish.
- **Food and Coins Decay:** Leftover food and coins disappear if not collected in time.
- **Smart Fish AI:** Fish chase food only when hungry and wander otherwise.
- **Tank Floor:** Everything is bound above a simulated floor.

---

## How to Play

- **Run**:  
  ```
  python fishtank.py
  ```
- **Controls:**
  - **Click** mouse: Drop food (if you have enough money) or collect coins.
  - **F key:** Buy a new fish (requires sufficient funds).
  - **Window Resize:** The tank and its contents adjust automatically.

- **Objective:**  
  Keep your fish alive and your money growing! If you don't feed fish in time, they die.

---

## Game Assets

- `background.png` — Tank background image  
- `fish/basicfish.png` — Fish sprite  
- `money.png` — Coin sprite  
- `ff.png` — Food sprite  

Make sure these image files are in the same directory as `fishtank.py`.

---

## Requirements

- Python 3.x
- [Pygame](https://www.pygame.org/)

Install Pygame with:
```
pip install pygame
```

---

## Game Logic Highlights

- **Adaptive Scaling:** Assets and UI automatically scale on window resize.
- **Object-Oriented Design:** Fish, food, and coins are each self-contained classes.
- **Timers:** Handles coin production and hunger through tracked timestamps.
- **Spoil Timers:** Food/coins disappear after 30 seconds.
- **No External Data:** Fully self-contained (except images).

---

## License

MIT License — See LICENSE file for details.

---

Enjoy your digital aquarium!
