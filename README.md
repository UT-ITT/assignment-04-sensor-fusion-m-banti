[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/AktWbCri)

# assignment-04-CV-Sensor-Fusion
To test all three applicsations create a python virtual environment by using the requirements.txt file. (Since it's assignment 4 and we all know how it works I'm not writing an instruction)

## Perspective Transformer

The script image_extractor.py allows us to select an image that needs to be cropped. The cropping area results from choosing 4 corner points inside the image. The cropped picture can be saved, discarded or the process can be canceled.

### How it works

1. Either use the provided image or choose your own (I highly recomment using the provided one)
2. Input to terminal (you need to be in the folder "perspective_transformation):

```bash
    python3 image_extractor.py <input_path> <output_path> <width> <height>"
```

Example:

```bash
    python3 image_extractor.py images/image.jpg images/extracted_image.png 200 200
```

3. To cut the image just set the corner points of the selecting by right clicking with your mouse on the respective area.
4. To save the image press the key "s". To discard the selection press the key "d". To exit after saving the image or to cancel the process press the key "esc"

#### Assets

[Source of: image.jpg](https://en.meming.world/wiki/File:Crying_Cat.jpg/)

## AR Game
This is a Aruco Shooter game!!

### Gameplay
Welcome to your very own Augmented Reality shooting range!

- Controls:
    - The Weapon: You use your hand to do a "finger gun" sign. Your index finger acts as your crosshair (it glows green when ready to fire).
    - Pew Pew: When your thumb "pulls the trigger" by going down towards your index finger, the crosshair turns red and shoots an orange projectile straight ahead!
    - The Enemies: Evil blue circles will continuously spawn from the right side of the board and rush toward your hand.
- Goal:
    - You shoot the circles to rack up your "Killed enemies" score until no circle is left! But be careful, if a circle touches any part of your physical hand inside the game board... wamp waaaamp, you lose!
- Tipps:
    - Having trouble with the skin detection? The game has you covered: 
    - Press Arrow UP to switch to "Daylight Mode" (natural vitamin D lighting).
    - Press Arrow DOWN to switch to "Nighttime/Werewolf Mode" (for moonlight gaming).
    - Press Q or ESC to rage quit.


### How it works
- Part 1: Selecting the right Aruco Dictionary:
    1. If you use Aruco markers in the dictionary range of DICT_4x4_50 and DICT_4x4_250 congratulations you need to change nothing and go straight to Step 2 (without collecting your 200€).

    2. If it is not in the mentioned frame but you know your Aruco marker dictionary then do the following:
        1. Search in the file AR_game.py for following line of code:
        ```python
            aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_6X6_250)
        ```
        2. exchange the dictionary version with the one form your aruco markers.
        For Example:
        ```python
            aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_250)
        ```
        3. Go now straight to Step 2 (also here you go wothiut collecting your 200€)

    3. Since you don't know which version you got, follow these instructions
        1. Run in the Terminal following command(be sure to be in the directory: ar_game):
        ```bash
            python3 aruco_detection.py
        ```
        2. A window will open. Please hold your Aruco marker/s into the camera. In the window will be displayed the recommended version to use for your markers. (Also the Terminal will display it). For example:
        ```bash
            Match found, you can use a dictionary in following range: 6X6_50 to 6X6_250. Choose highest dictionary = 6X6_250
        ```
        3. Go directly to Number 2 in Part 1 and congratulations since you did some extra steps you get your 200€ (of course it's fictional)!
- Part 2: Start the Game:
    1. To start the Game input following into the terminal (be sure to be in the directory: ar_game):
        ```bash
            python3 AR_game.py
        ```
    2. Have fun!


#### Assets

- Sources:
    - Skin detection: https://pyimagesearch.com/2014/08/18/skin-detection-step-step-example-using-python-opencv/
    
## Sensor Fusion
Because trusting just one sensor is boring, right? This script uses a complementary filter to fuse the camera position with your accelerometer data to produce a much smoother prediction.
### How it works
1. Input to terminal:
    ```bash
    python3 sensor_fusion.py
    ```
    > (If your camera doesn't start, try python3 sensor_fusion.py 1 or whatever your index is)
2. Visuals: 
    - Red Dot: camera position (laggy but accurate)
    - Green Dot: predicted position using sensor fusion
3. Controls:
    - Arrow UP / RIGHT: increase alpha (trust the accelerometer more)
    - Arrow DOWN / LEFT: decrease alpha (trust the camera more)
    - DIPPID Button 1: reset prediction back to camera position (for when the green dot inevitably drifts into the abyss)
    - Q or ESC: Quit

#### Reflection on Alpha Values
When trying out different alpha values I noticed following:

- If alpha is close to 0.0 (trusting the camera), the prediction is highly accurate but suffers from camera lag and lower frame rates.
- If alpha is close to 1.0 (trusting the accelerometer), the movement of the green dot gets incredibly snappy and smooth but it drifts out of bounds very fast because of sensor noise.
- So the sweet spot is around 0.8 to 0.9. It keeps it snappy but the camera constantly drags the prediction back to the right position.