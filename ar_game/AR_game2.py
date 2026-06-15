'''
ToDo's:
- webcam readout (similar to exercise)
- detect aruco markers
- get aruco area is rectangle with same resolution as webcam (variable resolution)
- display warped rectangle in pyglet
- Game Mechanics: tarcking object (not from aruco markers)
    - example: use finger to destroy target object or to move things around   
'''

'''
Current Problems:
- Phone Camera and Macbook connection doesn't work 
- wrong aruco version (fixed)
- only 1 of 4 markers are being detected (fixed)
- using hand gets markers blocked and perspective wrap goes away (fixed)
- everything flipped
- bullets shoot in wrong direction (prob. fix: mirroring earlier) (fixed)
- bullets shoot continiously (fixed)
'''
import cv2
import cv2.aruco as aruco
import sys
import numpy as np
import pyglet
from pyglet.window import key
from PIL import Image
import random

video_id = 0
# to save perspective even if it gets block during play
saved_matrix = None

bullets = []
# saves if the fingergun shot in the frame before
trigger_state = 0

enemies = []

ENEMY_SPEED = 5

# skin color range (Die strengen Werte gegen das Whiteboard!)
LOWER_SKIN = np.array([0, 80, 70], dtype=np.uint8)
UPPER_SKIN = np.array([20, 255, 255], dtype=np.uint8)

if len(sys.argv) > 1:
    video_id = int(sys.argv[1])

print(f"Starting camera from index {video_id} ... lets pray it works ( ̵˃﹏˂̵ )")
cam = cv2.VideoCapture(video_id)

# checking for webcam
if not cam.isOpened():
    print(f"Could not open webcam {video_id} (」°ロ°)」, check your cables!")
    sys.exit(1)

# check for webcam resolution
CAM_WIDTH = int(cam.get(cv2.CAP_PROP_FRAME_WIDTH))
CAM_HEIGHT = int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))
print(f"Webcam initialized successfully! Resolution: {CAM_WIDTH}x{CAM_HEIGHT}")

# copied from example
aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_6X6_250)
aruco_params = aruco.DetectorParameters()
detector = aruco.ArucoDetector(aruco_dict, aruco_params)

# ordering aruco markers
def order_points(pts):
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect

# converts OpenCV image to PIL image and then to pyglet texture
def cv2glet(img,fmt):
    if fmt == 'GRAY':
      rows, cols = img.shape
      channels = 1
    else:
      rows, cols, channels = img.shape

    raw_img = Image.fromarray(img).tobytes()
    top_to_bottom_flag = -1
    bytes_per_row = channels*cols
    pyimg = pyglet.image.ImageData(width=cols, 
                                   height=rows, 
                                   fmt=fmt, 
                                   data=raw_img, 
                                   pitch=top_to_bottom_flag*bytes_per_row)
    return pyimg


win = pyglet.window.Window(CAM_WIDTH, CAM_HEIGHT, caption="AR Game (｡•̀ᴗ-)✧")
current_bg_sprite = None

def track_pointer(frame):
    # convert color to hsv
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    # filter anything except skin color
    mask = cv2.inRange(hsv, LOWER_SKIN, UPPER_SKIN)
    
    # cleanup noise
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.dilate(mask, kernel, iterations=2)
    mask = cv2.GaussianBlur(mask, (5, 5), 100)
    
    # search hand outlines
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        return None
        
    # set largest skin colored area as hand
    hand_contour = max(contours, key=cv2.contourArea)
    
    # cancel out noise
    if cv2.contourArea(hand_contour) < 5000:
        return None
        
    # find most left point (index finger)
    index_tip = min(hand_contour, key=lambda p: p[0][0])[0]
    # find most up point (thumb)
    thumb_tip = min(hand_contour, key=lambda p: p[0][1])[0]
    # gap between thumb tip and index finger
    vertical_gap = abs(index_tip[1] - thumb_tip[1])
    
    # finger gun fires when thumb "pull the trigger" 
    is_firing = vertical_gap <30
    
    return tuple(index_tip), is_firing
    

def update(dt):
    global current_bg_sprite, detector, saved_matrix, bullets, trigger_state
    
    ret, frame = cam.read()
    if not ret:
        print("Camera dropped a frame (╥_╥)")
        return
    # resize frame since my 1920x1080 is to large
    small_frame = cv2.resize(frame, (640, 360))
    
    # Use small_frame for consistency
    gray = cv2.cvtColor(small_frame, cv2.COLOR_BGR2GRAY)
    
    # detect aruco markers
    corners, ids, _ = detector.detectMarkers(gray) # type: ignore
    # scale markers 
    scale_factor = CAM_WIDTH / 640
    marker_count = len(ids) if ids is not None else 0
    
    # if 4 markers were detected, save the matrix
    if ids is not None and len(ids) == 4:
        marker_centers = []
        for corner in corners:
            c = corner[0] * scale_factor
            marker_centers.append([int(c[:, 0].mean()), int(c[:, 1].mean())])
            
        pts1 = np.array(marker_centers, dtype="float32")
        pts1 = order_points(pts1)
        pts2 = np.array([[CAM_WIDTH, 0], [0, 0], [0, CAM_HEIGHT], [CAM_WIDTH, CAM_HEIGHT]], dtype=np.float32)
        
        saved_matrix = cv2.getPerspectiveTransform(pts1, pts2)
        
    # get pointer coordinates and firing state from small frame
    pointer_data = track_pointer(small_frame)
    
    if saved_matrix is not None:
        # locking of warped board
        warped_frame = cv2.warpPerspective(frame, saved_matrix, (CAM_WIDTH, CAM_HEIGHT))
        
        # map pointer coordinates to warped board
        if pointer_data is not None:
            # unapck data
            pointer_coords, is_firing = pointer_data
            
            raw_pt = np.array([[[float(pointer_coords[0]) * scale_factor, float(pointer_coords[1]* scale_factor)]]], dtype=np.float32)
            # map camera pixel to warped board pixel
            mapped_pt = cv2.perspectiveTransform(raw_pt, saved_matrix)
            
            board_x = int(mapped_pt[0][0][0])
            board_y = int(mapped_pt[0][0][1])
            
            # firing logic
            if is_firing and trigger_state == 0:
                # fire bullet with given speed
                bullets.append({"x": board_x, "y": board_y, "speed": 25})
                # save state as bullet fired
                trigger_state = 1
            elif is_firing and trigger_state == 1:
                pass
            elif not is_firing:
                # thumb released, reset to ready
                trigger_state = 0

            # debug: crosshair changes to red to see visually current status
            color = (0, 0, 255) if trigger_state == 1 else (0, 255, 0)
            
            # draw green crosshair
            cv2.circle(warped_frame, (board_x, board_y), 10, color, 2)
            cv2.line(warped_frame, (board_x-20, board_y), (board_x+20, board_y), color, 2)
            cv2.line(warped_frame, (board_x, board_y-20), (board_x, board_y+20), color, 2)
        

        # projectile physics
        # copy list to delete bullets
        for b in bullets[:]:
            # move bullet right
            b["x"] += b["speed"]
            
            # draw bullet orange
            cv2.circle(warped_frame, (b["x"], b["y"]), 8, (0, 165, 255), -1)
            
            # delete bullet if it crosses right window border
            if b["x"] > CAM_WIDTH:
                bullets.remove(b)
                # enemy spawning logic
        if random.random() < 0.01:
            enemies.append({
                "x": CAM_WIDTH,
                "y": random.randint(59, CAM_HEIGHT - 50),
                "radius": 20 
            })
            
        
        # enemy physiscs
        for e in enemies [:]:
            # move towards index finger (palyer)
            e["x"] -= ENEMY_SPEED
            #draw enemy
            cv2.circle(warped_frame, (int(e["x"]), int(e["y"])), int(e["radius"]), (255, 0, 0), -1)
            
            # collision with hand
            dist = np.sqrt((e["x"]- board_x)**2 + (e["y"] - board_y)**2) # type: ignore
            if dist < (e["radius"]+10):
                print("Wamp waaaamp, you got touched by an enemy so you lost")
                # reset game
                enemies.remove(e)
            
            # collision with bullets
            for b in bullets[:]:
                b_dist = np.sqrt((e["x"] -b ["x"])**2 + (e["y"] - b["y"])**2)
                if b_dist < (e["radius"]+8):
                    if e in enemies: enemies.remove(e)
                    if b in bullets: bullets.remove(b)
            if e["x"] <0:
                enemies.remove(e)
                    
    else:
        # normal camera view until 4 markers are found
        warped_frame = frame.copy()
        if ids is not None:
            cv2.aruco.drawDetectedMarkers(warped_frame, corners, ids)
        cv2.putText(warped_frame, f"Searching... Markers visible: {marker_count}/4", (30, 130), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

    cv2.waitKey(1)
        
    # conversion frame to pyglet
    init_warped_frame = cv2.cvtColor(warped_frame, cv2.COLOR_BGR2RGB)
    # mirroring window
    init_warped_frame = cv2.flip(init_warped_frame, 1)
    
    img_data = cv2glet(init_warped_frame, 'RGB')
    current_bg_sprite = pyglet.sprite.Sprite(img=img_data, x=0, y=0)
    

@win.event
def on_draw():
    win.clear()
    if current_bg_sprite:
        current_bg_sprite.draw()

@win.event
def on_close():
    print("Bye bye! (￣▽￣)ノ...")
    cam.release()
    
@win.event
def on_keypress(Symbol, Modifier):
    if Symbol == key.Q or Symbol == key.ESCAPE:
        cam.release()
        cv2.destroyAllWindows()
        pyglet.app.exit()
    
if __name__ == "__main__":
    pyglet.clock.schedule_interval(update, 1/60.0)
    pyglet.app.run()