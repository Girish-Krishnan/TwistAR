# TwistAR

TwistAR is an open-source exergame that encourages movement using computer vision. It was developed for users who spend long hours seated or standing in the same position. The game challenges players to match on-screen prompts with body poses detected from a webcam.

## Features
- Uses [MediaPipe](https://google.github.io/mediapipe/) pose detection to track 33 body landmarks.
- Optional Bluetooth controller built with an ESP32 for additional feedback.
- Progressive levels that require placing each limb on colored targets.

## Installation
1. Clone this repository.
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Game
Execute the main script with a connected webcam. If you are using the optional controller, provide its serial port via the `--port` argument:
```bash
python3 TwistAR.py --port /dev/ttyUSB0
```
The default baud rate is `115200` and can be changed with `--baud`.

## Repository Structure
- `TwistAR.py` – main Python game using OpenCV and MediaPipe.
- `Python/ECE16Lib/` – helper library for communication and sensor processing.
- `TwistARController/` – Arduino code for the optional ESP32 controller.
- `images/` – screenshots of the game in action.

## Gameplay Screenshots
![Levels Display](images/plot1_showinglevels.png)

![Level 6 Complete](images/plot2_level6completed.png)

## License
This project is released under the MIT License.
